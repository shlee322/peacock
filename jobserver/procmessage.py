from couchbase.bucket import Bucket as CouchbaseBucket
from couchbase.views.iterator import View, Query

exchange = None
event_db = CouchbaseBucket('couchbase://localhost/events')
link_db = CouchbaseBucket('couchbase://localhost/links')
analyzer_db = CouchbaseBucket('couchbase://localhost/analyzers')
analyzer_input_db = CouchbaseBucket('couchbase://localhost/analyzer_input')


def set_mq_exchange(ex):
    global exchange
    exchange = ex


def process_message(message):
    if message['type'] == 'link' or message['type'] == 'unlink' or message['type'] == 'event':
        process_event_message(message)

        if message['type'] == 'event':
            notify_update_entity(message['entity']['kind'], message['entity']['id'], message['log_key'])
        else:
            notify_update_entity_change_links(message['service']['id'],
                                              message['entity']['kind'], message['entity']['id'],
                                              message['timestamp'])

        # { 'type':'update_entity', 'analyzer':'' } # analyzer가 존재하지 않을 경우 analyzer을 전부 찾아서 메시지큐에 등록
        # 이벤트가 추가된 경우에는 단순한데 이벤트 추가를 알림
        # 문제는 링크랑 언링크가 변경된 경우
        # 만약 링크가 된 경우 해당 링크된 시점부터 언링크 발견시까지... add 처리
        # 언링크 된 경우 언링크된 시점부터 다음 링크 시점까지... delete 처리

        # 링크/언링크 같은 경우 현재 해당 엔티티의 현재 시간 이후의 모든 이벤트를 update 시키는 방식으로 처리해야 할듯
        # 이벤트 추가시
        #  해당 이벤트가 참조되는 분석기를 콜! (추가로)
        #  변경의 경우도 삭제후 추가니까 ㅇㅇ
    elif message['type'] == 'update_entity':
        # input 관리 서버에서 찾아서 없으면 그냥 종료하고 만약 발견된 경우
        # 그룹 탐색 (만약 이미 해당 이벤트가 다른 그룹인 경우 제거)
        # 그룹 인풋에 데이터 쓰기
        # log_key
        update_entity(message)


def update_entity(message):
    event_data = event_db.get(message['log_key'])

    event = event_data.value
    q = Query(
        inclusive_end=True,
        mapkey_range=[
            [event['service']['id'], event['entity']['kind'], event['event_name'], ],
            [event['service']['id'], event['entity']['kind'], event['event_name'], Query.STRING_RANGE_END]
        ],
        limit=1000000
    )

    view = View(analyzer_db, "analyzers", "event_to_analyzer", query=q)
    for result in view:
        update_entity_analyzer(result.docid, result.value, event)


def update_entity_analyzer(analyzer_id, analyzer, event):
    # analyzer에서 정보 긁어와서 그룹핑 해주고 리듀스 호출

    groups = []
    if True:
        group_time = 0
        if analyzer['group'].get('time'):
            group_time = int(event['timestamp'] / analyzer['group']['time'])

        if not analyzer['group'].get('entity_kind'):
            groups.append((group_time, ''))
        else:
            if analyzer['group']['entity_kind'] == event['entity']['kind']:
                groups.append((group_time, event['entity']['id']))

            q = Query(
                inclusive_end=True,
                descending=True,
                mapkey_range=[
                    [event['service']['id'], event['entity']['kind'], event['entity']['id'], event['timestamp']],
                    [event['service']['id'], event['entity']['kind'], event['entity']['id'], 0]
                ],
                limit=1,
                stale='false'
            )

            view = View(link_db, "links", "timeline", query=q)
            # ㄹㅇ 똥코드 ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ 데드라인이 코앞이다 으아아아아아아럼ㅇ나리ㅓ래ㅑ저맫
            for result in view:
                for link in result.value['links']:
                    if analyzer['group']['entity_kind'] == link['kind']:
                        groups.append((group_time, link['id']))
                break
    else:
        pass

    # 기존의 자료 제거
    # 관련있는자료 업데이트하고
    exist_groups = {}
    for group in groups:
        group_key = '%s_%s' % group
        exist_groups[group_key] = True
        analyzer_input_db.upsert("%s_%s_%s" % (analyzer_id, group_key, event['log_key']), {
            'service': {
                'id': event['service']['id']
            },
            'analyzer_id': analyzer_id,
            'group': group,
            'event_id': event['log_key']
        })

        # 리듀스 호출
        update_analyzer_group(analyzer_id, group_key)

    q = Query(
        mapkey_range=[
            [event['service']['id'], analyzer_id, event['log_key'], ],
            [event['service']['id'], analyzer_id, event['log_key'], Query.STRING_RANGE_END]
        ],
        limit=100000000,     # TODO : 차후 수정 (만약 100000000개가 넘는게 중간에 들어올 경우 [그럴일은 거의 없지만])
    )

    view = View(analyzer_input_db, "input", "event", query=q)
    for result in view:
        group = result.value['group']
        group_key = '%s_%s' % (group[0], group[1])
        if not exist_groups.get(group_key):
            analyzer_input_db.remove("%s_%s_%s" % (analyzer_id, group_key, event['log_key']))
            # 삭제후 리듀스 호출
            update_analyzer_group(analyzer_id, group_key)


def notify_update_entity(entity_kind, entity_id, log_key):
    import hashlib
    import struct
    import asynqp
    import msgpack

    from jobserver.config import JOB_RING_SIZE

    hash_key = "%s_%s" % (entity_kind, entity_id)
    hash_key = struct.unpack('>I', hashlib.md5(hash_key.encode('utf8')).digest()[0:4])
    hash_key = hash_key[0] % JOB_RING_SIZE

    obj = {
        'log_key': log_key,
        'type': 'update_entity'
    }

    exchange.publish(asynqp.Message(msgpack.packb(obj)), 'peacock_job_%d' % hash_key)


def update_analyzer_group(analyzer_id, group):
    import hashlib
    import struct
    import asynqp
    import msgpack

    from jobserver.config import JOB_RING_SIZE

    hash_key = "%s_%s_%s" % (analyzer_id, group[0], group[1])
    hash_key = struct.unpack('>I', hashlib.md5(hash_key.encode('utf8')).digest()[0:4])
    hash_key = hash_key[0] % JOB_RING_SIZE

    obj = {
        'type': 'update_analyzer_group',
        'analyzer_id': analyzer_id,
        'group': group
    }

    exchange.publish(asynqp.Message(msgpack.packb(obj)), 'peacock_job_%d' % hash_key)


def notify_update_entity_change_links(service_id, entity_kind, entity_id, timestamp):
    q = Query(
        mapkey_range=[
            [service_id, entity_kind, entity_id, timestamp, ],
            [service_id, entity_kind, entity_id, Query.STRING_RANGE_END, Query.STRING_RANGE_END]
        ],
        limit=100000000,     # TODO : 차후 수정 (만약 100000000개가 넘는게 중간에 들어올 경우 [그럴일은 거의 없지만])
    )

    view = View(event_db, "events", "entity_timeline", query=q)

    for result in view:
        notify_update_entity(entity_kind, entity_id, result.docid)


def process_event_message(message):
    event_db.upsert(message['log_key'], message)

    if message['type'] == 'event':
        return

    # 우선 바로 전 과거 내역을 찾아 카피한 이후 저장 (변경한 후 수정)
    # 그 이후 시간 데이터를 순차적으로 돌며 변경 내용 저장

    service_id = message['service']['id']
    timestamp = message['timestamp']
    entity_kind = message['entity']['kind']
    entity_id = message['entity']['id']

    target = message['target']

    main_doc_id = "%s/%s/%s/%d" % (service_id, entity_kind, entity_id, timestamp)

    q = Query(
        inclusive_end=True,
        descending=True,
        mapkey_range=[
            [service_id, entity_kind, entity_id, timestamp],
            [service_id, entity_kind, entity_id, 0]
        ],
        limit=1,
        stale='false'
    )

    link_data = {
        'service': message['service'],
        'entity': message['entity'],
        'timestamp': message['timestamp'],
        'links': []
    }

    view = View(link_db, "links", "timeline", query=q)
    for result in view:
        link_data = result.value

    link_data['timestamp'] = message['timestamp']
    link_db.upsert(main_doc_id, link_data)

    # 미래 내역 정리
    q = Query(
        inclusive_end=True,
        mapkey_range=[
            [service_id, entity_kind, entity_id, timestamp],
            [service_id, entity_kind, entity_id, Query.STRING_RANGE_END]
        ],
        limit=100000000,     # TODO : 차후 수정 (만약 100000000개가 넘는게 중간에 들어올 경우 [그럴일은 거의 없지만])
        stale='false'
    )

    view = View(link_db, "links", "timeline", query=q)

    for result in view:
        update_link_data(result.value, timestamp, target['kind'], target['id'], 1 if message['type'] == 'link' else -1)
        link_db.upsert(result.docid, result.value)


def update_link_data(data, timestamp, target_kind, target_id, count):
    remove_links = []
    update = False
    links = data['links']
    for link in links:
        if link['kind'] != target_kind or link['id'] != target_id:
            if link['count'] == 0 and link['timestamp'] != timestamp:
                remove_links.append(link)
            continue

        update = True
        link['count'] += count
        if link['count'] == 0 and link['timestamp'] != timestamp:
            remove_links.append(link)

    if not update:
        data['links'].append({
            'timestamp': timestamp,
            'kind': target_kind,
            'id': target_id,
            'count': count
        })

    for link in remove_links:
        data['links'].remove(link)

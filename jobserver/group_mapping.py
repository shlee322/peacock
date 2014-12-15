from couchbase.views.iterator import View, Query
from jobserver import database


def update_entity(message):
    """
    엔티티에 변경 사항(새로운 이벤트 발생)이 생겼을때 호출되는 함수로
    관련있는 Analyzer를 찾아 Mapping 작업을 수행한다
    """
    event_data = database.event_db.get(message['log_key'])

    event = event_data.value
    q = Query(
        inclusive_end=True,
        mapkey_range=[
            [event['service']['id'], event['entity']['kind'], event['event_name'], ],
            [event['service']['id'], event['entity']['kind'], event['event_name'], Query.STRING_RANGE_END]
        ],
        limit=1000000
    )

    view = View(database.analyzer_db, "analyzers", "event_to_analyzer", query=q)
    for result in view:
        update_entity_analyzer(result.docid, result.value, event)


def update_entity_analyzer(analyzer_id, analyzer, event):
    """
    analyzer에서 정보 긁어와서 그룹핑 해주고 리듀스 호출
    """

    groups = []

    #import lupa
    #from lupa import LuaRuntime
    #lua = LuaRuntime(unpack_returned_tuples=True)

    if True:    # TODO : input filter
        group_time_select = analyzer['group'].get('time')
        if group_time_select != 0:
            group_time = int(event['timestamp'] / analyzer['group']['time']) * analyzer['group']['time']
        else:     # 전체를 하나로
            group_time = 0

        if not analyzer['group'].get('entity_kind') or analyzer['group'].get('entity_kind') == '':
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

            view = View(database.link_db, "links", "timeline", query=q)
            # ㄹㅇ 똥코드 ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ 데드라인이 코앞이다 으아아아아아아럼ㅇ나리ㅓ래ㅑ저맫
            for result in view:
                for link in result.value['links']:
                    if analyzer['group']['entity_kind'] == link['kind']:
                        groups.append((group_time, link['id']))
                break

    # 기존의 자료 제거
    # 관련있는자료 업데이트하고
    exist_groups = {}
    for group in groups:
        group_key = '%s_%s' % group
        exist_groups[group_key] = True
        database.analyzer_input_db.upsert("%s_%s_%s" % (analyzer_id, group_key, event['log_key']), {
            'service': {
                'id': event['service']['id']
            },
            'analyzer_id': analyzer_id,
            'group': group,
            'event_id': event['log_key']
        })

        # 리듀스 호출
        update_analyzer_group(analyzer_id, group)

    q = Query(
        mapkey_range=[
            [event['service']['id'], analyzer_id, event['log_key'], ],
            [event['service']['id'], analyzer_id, event['log_key'], Query.STRING_RANGE_END]
        ],
        limit=100000000,     # TODO : 차후 수정 (만약 100000000개가 넘는게 중간에 들어올 경우 [그럴일은 거의 없지만])
    )

    view = View(database.analyzer_input_db, "input", "event", query=q)
    for result in view:
        group = result.value['group']
        group_key = '%s_%s' % (group[0], group[1])
        if not exist_groups.get(group_key):
            database.analyzer_input_db.remove("%s_%s_%s" % (analyzer_id, group_key, event['log_key']))
            # 삭제후 리듀스 호출
            update_analyzer_group(analyzer_id, group)


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

    from jobserver.messagequeue import get_exchange
    get_exchange().publish(asynqp.Message(msgpack.packb(obj)), 'peacock_job_%d' % hash_key)


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

    from jobserver.messagequeue import get_exchange
    get_exchange().publish(asynqp.Message(msgpack.packb(obj)), 'peacock_job_%d' % hash_key)


def notify_update_entity_change_links(service_id, entity_kind, entity_id, timestamp):
    q = Query(
        mapkey_range=[
            [service_id, entity_kind, entity_id, timestamp, ],
            [service_id, entity_kind, entity_id, Query.STRING_RANGE_END, Query.STRING_RANGE_END]
        ],
        limit=100000000,     # TODO : 차후 수정 (만약 100000000개가 넘는게 중간에 들어올 경우 [그럴일은 거의 없지만])
    )

    view = View(database.event_db, "events", "entity_timeline", query=q)

    for result in view:
        notify_update_entity(entity_kind, entity_id, result.docid)

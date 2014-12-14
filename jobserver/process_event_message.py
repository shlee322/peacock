from couchbase.views.iterator import View, Query
from jobserver import database


def process_event_message(message):
    database.event_db.upsert(message['log_key'], message)

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

    view = View(database.link_db, "links", "timeline", query=q)
    for result in view:
        link_data = result.value

    link_data['timestamp'] = message['timestamp']
    database.link_db.upsert(main_doc_id, link_data)

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

    view = View(database.link_db, "links", "timeline", query=q)

    for result in view:
        update_link_data(result.value, timestamp, target['kind'], target['id'], 1 if message['type'] == 'link' else -1)
        database.link_db.upsert(result.docid, result.value)


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

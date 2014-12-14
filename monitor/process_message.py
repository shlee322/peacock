import asyncio


@asyncio.coroutine
def process_message(websocket, service_id, message):
    print(message)

    if message['type'] == 'subscribe':
        viewer_id = message['viewer_id']
        target = message['target']

        # subscribe 등록
        start_timestamp = target['timestamp']['start']

        import hashlib
        analyzer_key = hashlib.sha256(("%s_%s" % (service_id, 'test')).encode('utf8')).hexdigest()

        from couchbase.views.iterator import View, Query
        query = Query(
            inclusive_end=True,
            mapkey_range=[
                [analyzer_key, start_timestamp, ],
                [analyzer_key, Query.STRING_RANGE_END, Query.STRING_RANGE_END]
            ],
            limit=100000000
        )

        from monitor.database import analyzer_result_db
        view = View(analyzer_result_db, "monitor", "monitor", query=query)

        for result in view:
            import json
            yield from websocket.send(json.dumps({
                'type': 'subscribe_message',
                'viewer_id': viewer_id,
                'data': result.value
            }))

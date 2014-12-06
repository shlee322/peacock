import asyncio
import websockets
import json

log_db = None


@asyncio.coroutine
def handler(websocket, path):
    service_id = path[1:]
    while True:
        message = yield from websocket.recv()
        if message is None:
            break

        data = json.loads(message)

        method = data['method']
        if method == 'get_event_list':
            timestamp = data['timestamp']

            from couchbase.views.iterator import View, Query

            q = Query(
                descending=True,
                mapkey_range=[
                    [service_id, timestamp],
                    [service_id, data.get('start_timestamp', 0)]
                ],
                limit=20
            )

            view = View(log_db, "events", "eventviewer", query=q)

            result_data = []
            for result in view:
                result_obj = {
                    'timestamp': result.value['timestamp'],
                    'entity': result.value['entity'],
                    'event_name': result.value.get('event_name')
                }

                if result.value.get('timestamp_length'):
                    result_obj['timestamp_length'] = result.value.get('timestamp_length')
                else:
                    result_obj['timestamp_length'] = 0

                if result.value.get('data'):
                    result_obj['data'] = json.dumps(result.value.get('data'))[:100]

                result_data.insert(0, result_obj)

            yield from websocket.send(json.dumps({
                'method': 'get_event_list',
                'results': result_data
            }))
        elif method == "get_entity_timeline":
            yield from websocket.send(json.dumps({
                'method': 'get_entity_timeline',
                'results': []
            }))


if __name__ == '__main__':
    from couchbase.bucket import Bucket as CouchbaseBucket
    log_db = CouchbaseBucket('couchbase://localhost/events')

    loop = asyncio.get_event_loop()
    start_server = websockets.serve(handler, '0.0.0.0', 7000)
    loop.run_until_complete(start_server)
    loop.run_forever()

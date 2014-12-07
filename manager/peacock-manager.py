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



if __name__ == '__main__':
    from couchbase.bucket import Bucket as CouchbaseBucket
    log_db = CouchbaseBucket('couchbase://localhost/events')

    loop = asyncio.get_event_loop()
    start_server = websockets.serve(handler, '0.0.0.0', 7000)
    loop.run_until_complete(start_server)
    loop.run_forever()

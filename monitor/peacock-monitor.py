"""
Peacock Monitor

Websocket로 유저들이 보고 싶어하는 그래프를 DB나 MessageQueue에서 받아온다.
처음 유저가 요청을 하면 MQ에 등록하고 DB에서 해당 기간에 해당하는 데이터를 긁어옴.
"""
import asyncio
import websockets
import json


@asyncio.coroutine
def handler(websocket, path):
    service_id = path[1:]

    from monitor.process_message import process_message
    while True:
        message = yield from websocket.recv()
        if message is None:
            break

        data = json.loads(message)
        yield from process_message(websocket, service_id, data)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    start_server = websockets.serve(handler, '0.0.0.0', 7000)
    loop.run_until_complete(start_server)
    loop.run_forever()

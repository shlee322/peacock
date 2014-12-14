"""
Peacock Monitor

Websocket로 유저들이 보고 싶어하는 그래프를 DB나 MessageQueue에서 받아온다.
처음 유저가 요청을 하면 MQ에 등록하고 DB에서 해당 기간에 해당하는 데이터를 긁어옴.
"""
import asyncio
import websockets
import json


@asyncio.coroutine
def init_monitor():
    import asynqp
    global mq_connection, mq_channel
    mq_connection = yield from asynqp.connect('localhost', 5672, username='guest', password='guest')
    mq_channel = yield from mq_connection.open_channel()

    exchange = yield from mq_channel.declare_exchange('monitor_queue', 'topic')

    from monitor.messagequeue import set_channel, set_exchange
    set_channel(mq_channel)
    set_exchange(exchange)


@asyncio.coroutine
def handler(websocket, path):
    service_id = path[1:]

    from monitor.process_message import Handler
    yield from Handler(service_id, websocket).run()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_monitor())
    start_server = websockets.serve(handler, '0.0.0.0', 7000)
    loop.run_until_complete(start_server)
    loop.run_forever()

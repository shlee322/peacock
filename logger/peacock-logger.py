import asyncio
import aiozmq
import msgpack


class LoggerZmqProtocol(aiozmq.ZmqProtocol):
    transport = None

    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def msg_received(self, msg):
        results = []
        for data in msg:
            results.append(self.task_log(data))
        self.transport.write(results)

    def connection_lost(self, exc):
        import logging
        logging.exception(exc)

    def task_log(self, data):
        data = msgpack.unpackb(data)
        token = data[0]
        data = msgpack.unpackb(data[1])
        print(data)
        return '0'.encode('utf8')


@asyncio.coroutine
def init_logger():
    import zmq
    router, temp = yield from aiozmq.create_zmq_connection(
        lambda: LoggerZmqProtocol(), zmq.REP,
        bind='tcp://0.0.0.0:6000')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.async(init_logger(), loop=loop)
    loop.run_forever()

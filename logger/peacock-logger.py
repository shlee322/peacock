import asyncio
import aiozmq
import msgpack
import asynqp

log_db = None
now_time = 0
seq = 0
messagequeue_exchange = None


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

        log_data = msgpack.unpackb(data[1], encoding='utf-8')
        log_data['service'] = {
            'id': data[0].decode('utf8')
        }

        import time
        global now_time, seq
        log_time = int(time.time() * 1000)
        if now_time != log_time:
            now_time = log_time
            seq = 0
        seq += 1
        log_key = '%s_%s_%s' % (log_time, '1', seq)
        log_db.insert(log_key, log_data)

        messagequeue_exchange.publish(asynqp.Message({'log_id': log_key}), 'peacock_job_1')

        return log_key.encode('utf8')


@asyncio.coroutine
def init_logger():
    messagequeue_conn = yield from asynqp.connect('localhost', 5672, username='guest', password='guest')
    messagequeue_channel = yield from messagequeue_conn.open_channel()

    global messagequeue_exchange
    messagequeue_exchange = yield from messagequeue_channel.declare_exchange('peacock_job.exchange', 'direct')
    queue = yield from messagequeue_channel.declare_queue('peacock_job_1')
    yield from queue.bind(messagequeue_exchange, 'peacock_job_1')

    import zmq
    router, temp = yield from aiozmq.create_zmq_connection(
        lambda: LoggerZmqProtocol(), zmq.REP,
        bind='tcp://0.0.0.0:6000')


if __name__ == '__main__':
    from couchbase.bucket import Bucket as CouchbaseBucket
    log_db = CouchbaseBucket('couchbase://localhost/events')

    loop = asyncio.get_event_loop()
    asyncio.async(init_logger(), loop=loop)
    loop.run_forever()

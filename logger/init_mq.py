import asyncio
import asynqp


@asyncio.coroutine
def init_mq():
    messagequeue_conn = yield from asynqp.connect('localhost', 5672, username='guest', password='guest')
    messagequeue_channel = yield from messagequeue_conn.open_channel()

    global messagequeue_exchange
    messagequeue_exchange = yield from messagequeue_channel.declare_exchange('peacock_job.exchange', 'direct')

    queue = yield from messagequeue_channel.declare_queue('peacock_job_0')
    for i in range(8192):
        yield from queue.bind(messagequeue_exchange, 'peacock_job_%d' % i)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_mq())

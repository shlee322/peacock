import asyncio
import asynqp

@asyncio.coroutine
def init_mq():
    messagequeue_conn = yield from asynqp.connect('localhost', 5672, username='guest', password='guest')
    messagequeue_channel = yield from messagequeue_conn.open_channel()

    messagequeue_exchange = yield from messagequeue_channel.declare_exchange('peacock_job.exchange', 'direct')

    import logging

    for i in range(8192):
        logging.info("Init Queue - %d" % i)
        queue = yield from messagequeue_channel.declare_queue('peacock_job_%d' % i)
        yield from queue.bind(messagequeue_exchange, 'peacock_job_%d' % i)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.async(init_mq(), loop=loop)
    loop.run_forever()
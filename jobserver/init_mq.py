import asyncio
import asynqp


@asyncio.coroutine
def init_mq():
    from jobserver.config import MESSAGE_QUEUE_ADDRESS, MESSAGE_QUEUE_PORT, MESSAGE_QUEUE_USER, MESSAGE_QUEUE_PASSWORD

    messagequeue_conn = yield from asynqp.connect(MESSAGE_QUEUE_ADDRESS, MESSAGE_QUEUE_PORT,
                                                  username=MESSAGE_QUEUE_USER, password=MESSAGE_QUEUE_PASSWORD)
    messagequeue_channel = yield from messagequeue_conn.open_channel()

    messagequeue_exchange = yield from messagequeue_channel.declare_exchange('peacock_job.exchange', 'direct')

    import logging
    from jobserver.config import JOB_RING_SIZE

    for i in range(JOB_RING_SIZE):
        logging.info("Init Queue - %d" % i)
        queue = yield from messagequeue_channel.declare_queue('peacock_job_%d' % i)
        yield from queue.bind(messagequeue_exchange, 'peacock_job_%d' % i)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.async(init_mq(), loop=loop)
    loop.run_forever()

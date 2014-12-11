import logging
import asyncio
import asynqp
import msgpack
from kazoo.client import KazooClient

my_node_name = None
node_start_queue_id = -1
node_end_queue_id = -1
jobs = {}
mq_connection = None
mq_channel = None

loop = asyncio.get_event_loop()


@asyncio.coroutine
def init_jobserver():
    global mq_connection, mq_channel
    mq_connection = yield from asynqp.connect('localhost', 5672, username='guest', password='guest')
    mq_channel = yield from mq_connection.open_channel()

    from jobserver.procmessage import set_mq_exchange
    exchange = yield from mq_channel.declare_exchange('peacock_job.exchange', 'direct')
    set_mq_exchange(exchange)


@asyncio.coroutine
def job_node_processor(node_index):
    from jobserver.procmessage import process_message
    queue = yield from mq_channel.declare_queue('peacock_job_%d' % node_index)
    while True:
        if not(node_start_queue_id <= node_index <= node_end_queue_id):
            jobs[node_index] = None
            return

        message = yield from queue.get()
        if not message:
            continue

        try:
            data = msgpack.loads(message.body, encoding='utf-8')
            process_message(data)
            message.ack()
        except Exception as e:
            logging.exception(e)
            message.reject()


def job_node_watch(nodes):
    if not my_node_name or len(nodes) < 1:
        return

    # 링이 8192로 나눠져 있음
    # 8192를 nodes의 길이로 나누고
    # 노드의 index를 곱한거 ~ (노드인덱스+1)

    ring_size = 8192 / len(nodes)
    node_index = nodes.index(my_node_name)

    global node_start_queue_id, node_end_queue_id
    node_start_queue_id = int(node_index * ring_size)
    node_end_queue_id = int((node_index+1) * ring_size - 1)
    logging.info("node_start_queue_id = %d, node_end_queue_id = %d" % (node_start_queue_id, node_end_queue_id))

    for i in range(node_start_queue_id, node_end_queue_id):
        if not jobs.get(i):
            asyncio.async(job_node_processor(i), loop=loop)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(init_jobserver())

    from config import ZOOKEEPER_HOST
    zk = KazooClient(hosts=ZOOKEEPER_HOST)
    zk.start()

    zk.ChildrenWatch("/peacock/job/nodes", job_node_watch)
    my_node = zk.create("/peacock/job/nodes/node", ephemeral=True, sequence=True, makepath=True)
    my_node_name = my_node[my_node.rfind('/')+1:]
    job_node_watch(zk.get_children("/peacock/job/nodes"))

    asyncio.async(init_jobserver(), loop=loop)
    loop.run_forever()

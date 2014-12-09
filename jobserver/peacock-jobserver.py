import logging
import asyncio
import asynqp
from kazoo.client import KazooClient

my_node_name = None
node_start_queue_id = -1
node_end_queue_id = -1


@asyncio.coroutine
def init_jobserver():
    """
    messagequeue_conn = yield from asynqp.connect('localhost', 5672, username='guest', password='guest')
    messagequeue_channel = yield from messagequeue_conn.open_channel()

    global messagequeue_exchange
    messagequeue_exchange = yield from messagequeue_channel.declare_exchange('peacock_job.exchange', 'direct')
    """
    # 쩝..


def job_node_processor(node_id):
    pass


def job_node_watch(nodes):
    if not my_node_name:
        return

    # 링이 8192로 나눠져 있음
    # 8192를 nodes의 길이로 나누고
    # 노드의 index를 곱한거 ~ (노드인덱스+1)

    ring_size = 8192 / len(nodes)
    node_index = nodes.index(my_node_name)

    global node_start_queue_id, node_end_queue_id
    node_start_queue_id = node_index * ring_size
    node_end_queue_id = (node_index+1) * ring_size - 1
    logging.info("node_start_queue_id = %d, node_end_queue_id = %d" % (node_start_queue_id, node_end_queue_id))


if __name__ == '__main__':
    from config import ZOOKEEPER_HOST
    zk = KazooClient(hosts=ZOOKEEPER_HOST)
    zk.start()

    zk.ChildrenWatch("/peacock/job/nodes", job_node_watch)
    my_node = zk.create("/peacock/job/nodes/node", ephemeral=True, sequence=True, makepath=True)
    global my_node_name
    my_node_name = my_node[my_node.rfind('/')+1:]
    job_node_watch(zk.get_children("/peacock/job/nodes"))

    loop = asyncio.get_event_loop()
    asyncio.async(init_jobserver(), loop=loop)
    loop.run_forever()

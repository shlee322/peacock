import logging
import asyncio
import asynqp
import msgpack
from kazoo.client import KazooClient

"""
기본적으로 사용하는 변수들
"""
my_node_name = None
node_start_queue_id = -1
node_end_queue_id = -1
jobs = {}
mq_connection = None
mq_channel = None

loop = asyncio.get_event_loop()


@asyncio.coroutine
def init_jobserver():
    """
    Init Job Server
    MessageQueue랑 커넥션을 맺는다.
    """
    global mq_connection, mq_channel
    from jobserver.config import MESSAGE_QUEUE_ADDRESS, MESSAGE_QUEUE_PORT, MESSAGE_QUEUE_USER, MESSAGE_QUEUE_PASSWORD

    mq_connection = yield from asynqp.connect(MESSAGE_QUEUE_ADDRESS, MESSAGE_QUEUE_PORT,
                                              username=MESSAGE_QUEUE_USER, password=MESSAGE_QUEUE_PASSWORD)
    mq_channel = yield from mq_connection.open_channel()

    from jobserver.messagequeue import set_exchange, set_monitor_queue

    exchange = yield from mq_channel.declare_exchange('peacock_job.exchange', 'direct')
    monitor_queue = yield from mq_channel.declare_exchange('monitor_queue', 'topic')
    set_exchange(exchange)
    set_monitor_queue(monitor_queue)


@asyncio.coroutine
def job_node_processor(node_index):
    """
    Queue Ring[node_index]를 처리함
    """
    logging.info("job_node_processor - %d" % node_index)

    from jobserver.procmessage import process_message
    # 해당 메시지 큐를 얻음
    queue = yield from mq_channel.declare_queue('peacock_job_%d' % node_index)

    # 메시지 큐 처리 루프
    while True:
        message = yield from queue.get()

        # Job Server가 처리해야할 큐 범위가 달라져서 처리하면 안될 경우 무한 루프를 빠져나감
        if not (node_start_queue_id <= node_index <= node_end_queue_id):
            jobs[node_index] = None

            # 메시지를 받아온 경우 실패 처리 (다시 큐에 넣음)
            if message:
                message.reject()

            logging.info("remove job_node_processor - %d" % node_index)
            break

        # TODO : 메시지가 없는 경우 블럭
        if not message:
            yield from asyncio.sleep(0.1)
            continue

        try:
            data = msgpack.loads(message.body, encoding='utf-8')
            # 메시지 처리
            process_message(data)
            message.ack()
        except Exception as e:
            # 메시지 처리 도중 문제가 생긴 경우 로그를 남기고 큐에 다시 등록
            logging.exception(e)
            message.reject()


def job_node_watch(nodes):
    """
    Job Server 노드들에 변화가 생긴 경우 감지 (노드 추가, 제외 등)
    """

    # 아직 초기화가 덜된 경우 나감
    if not my_node_name or len(nodes) < 1:
        return

    # 링이 JOB_RING_SIZE로 나눠져 있음
    # JOB_RING_SIZE를 nodes의 길이로 나누고
    # 노드의 index를 곱한거 ~ (노드인덱스+1)

    # 이 Job Server의 index를 구해옴
    from jobserver.config import JOB_RING_SIZE

    ring_size = JOB_RING_SIZE / len(nodes)
    node_index = nodes.index(my_node_name)

    # Job Server가 처리해야할 queue id를 구함
    global node_start_queue_id, node_end_queue_id
    node_start_queue_id = int(node_index * ring_size)
    node_end_queue_id = int((node_index + 1) * ring_size - 1)
    logging.info("node_start_queue_id = %d, node_end_queue_id = %d" % (node_start_queue_id, node_end_queue_id))

    # 큐 처리
    for i in range(node_start_queue_id, node_end_queue_id + 1):
        if not jobs.get(i):
            jobs[i] = job_node_processor(i)
            asyncio.async(jobs[i], loop=loop)


def set_python_logger():
    """
    파이썬 로거 셋팅
    """
    import sys

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)


def join_peacock_network():
    """
    주키퍼에 watch를 등록하고 해당 노드를 가입시킨다.
    """
    from config import ZOOKEEPER_HOST

    zk = KazooClient(hosts=ZOOKEEPER_HOST)
    zk.start()

    zk.ChildrenWatch("/peacock/job/nodes", job_node_watch)
    my_node = zk.create("/peacock/job/nodes/node", ephemeral=True, sequence=True, makepath=True)
    global my_node_name
    my_node_name = my_node[my_node.rfind('/') + 1:]
    job_node_watch(zk.get_children("/peacock/job/nodes"))


if __name__ == '__main__':
    # Python Logger Setting
    set_python_logger()

    # Init Job Server
    asyncio.get_event_loop().run_until_complete(init_jobserver())

    # Join Peacock Network
    join_peacock_network()

    # Loop
    loop.run_forever()

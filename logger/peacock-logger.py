import asyncio
import aiozmq
import msgpack
import asynqp
import zmq
from kazoo.client import KazooClient


log_db = None
node_id = ''
now_time = 0
seq = 0
messagequeue_exchange = None


def get_log_key():
    import time
    global now_time, seq
    log_time = int(time.time() * 1000)
    if now_time != log_time:
        now_time = log_time
        seq = 0
    seq += 1
    return '%s_%s_%s' % (log_time, node_id, seq)


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

    def publish_mq(self, obj):
        import hashlib
        import struct
        from logger.config import JOB_RING_SIZE

        log_key = "%s_%s" % (obj['entity']['kind'], obj['entity']['id'])
        log_key = struct.unpack('>I', hashlib.md5(log_key.encode('utf8')).digest()[0:4])
        log_key = log_key[0] % JOB_RING_SIZE

        messagequeue_exchange.publish(asynqp.Message(msgpack.packb(obj)), 'peacock_job_%d' % log_key)

    def task_log(self, data):
        try:
            data = msgpack.unpackb(data)

            log_data = msgpack.unpackb(data[1], encoding='utf-8')

            log_data['service'] = {
                'id': data[0].decode('utf8')
            }

            log_data['log_key'] = get_log_key()

            self.publish_mq(log_data)
            if log_data['type'] == 'link' or log_data['type'] == 'unlink':
                temp = log_data['entity']
                log_data['entity'] = log_data['target']
                log_data['target'] = temp
                log_data['log_key'] = get_log_key()
                self.publish_mq(log_data)
        except:
            return 'fail'.encode('utf8')

        return 'ok'.encode('utf8')


@asyncio.coroutine
def init_logger():
    messagequeue_conn = yield from asynqp.connect('localhost', 5672, username='guest', password='guest')
    messagequeue_channel = yield from messagequeue_conn.open_channel()

    global messagequeue_exchange
    messagequeue_exchange = yield from messagequeue_channel.declare_exchange('peacock_job.exchange', 'direct')

    from config import BIND_ADDRESS
    yield from aiozmq.create_zmq_connection(
        lambda: LoggerZmqProtocol(), zmq.REP,
        bind='tcp://%s' % BIND_ADDRESS)


if __name__ == '__main__':
    # 주키퍼에 등록
    from config import ZOOKEEPER_HOST, BIND_ADDRESS
    zk = KazooClient(hosts=ZOOKEEPER_HOST)
    zk.start()
    my_node = zk.create("/peacock/logger/zmq/node", BIND_ADDRESS.encode('utf8'), ephemeral=True, sequence=True, makepath=True)
    node_id = my_node[my_node.rfind('/')+1:]

    loop = asyncio.get_event_loop()
    asyncio.async(init_logger(), loop=loop)
    loop.run_forever()

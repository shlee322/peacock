import asyncio
import asynqp
import logging


class Handler:
    def __init__(self, service_id, websocket):
        self.service_id = service_id
        self.websocket = websocket
        self.queue = None
        self.analyzer_name = {}

    @asyncio.coroutine
    def run(self):
        from monitor.messagequeue import get_channel
        self.queue = yield from get_channel().declare_queue(exclusive=True)
        asyncio.async(self.process_queue(), loop=asyncio.get_event_loop())

        import json
        while True:
            message = yield from self.websocket.recv()
            if message is None:
                break

            data = json.loads(message)
            yield from self.process_message(data)

    @asyncio.coroutine
    def process_queue(self):
        import msgpack

        while self.websocket.open:
            message = yield from self.queue.get()
            if not message:
                yield from asyncio.sleep(0.2)
                continue

            try:
                data = msgpack.loads(message.body, encoding='utf-8')
                import json
                yield from self.websocket.send(json.dumps({
                    'type': 'subscribe_message',
                    'analyzer_name': self.analyzer_name[data['analyzer_id']],
                    'data': data
                }))
                message.ack()
            except Exception as e:
                # 메시지 처리 도중 문제가 생긴 경우 로그를 남기고 큐에 다시 등록
                logging.exception(e)
                message.reject()

        yield from self.queue.delete()

    @asyncio.coroutine
    def process_message(self, message):
        if message['type'] == 'subscribe':
            target = message['target']

            start_timestamp = target['timestamp']['start']

            import hashlib
            analyzer_key = hashlib.sha256(("%s_%s" % (self.service_id, target['analyzer_name'])).encode('utf8')).hexdigest()

            if not self.analyzer_name.get(analyzer_key):
                self.analyzer_name[analyzer_key] = target['analyzer_name']
            else:   # 이미 등록된 경우
                return

            from monitor.messagequeue import get_exchange
            yield from self.queue.bind(exchange=get_exchange(), routing_key=analyzer_key)

            from couchbase.views.iterator import View, Query
            query = Query(
                inclusive_end=True,
                mapkey_range=[
                    [analyzer_key, start_timestamp, ],
                    [analyzer_key, Query.STRING_RANGE_END, Query.STRING_RANGE_END]
                ],
                limit=100000000
            )

            from monitor.database import analyzer_result_db
            view = View(analyzer_result_db, "monitor", "monitor", query=query)

            for result in view:
                import json
                yield from self.websocket.send(json.dumps({
                    'type': 'subscribe_message',
                    'analyzer_name': target['analyzer_name'],
                    'data': result.value
                }))

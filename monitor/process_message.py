
def process_message(websocket, service_id, message):
    if message['type'] == 'subscribe':
        target = message['target']
        print(message)

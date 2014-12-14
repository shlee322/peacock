channel = None
exchange = None


def set_channel(c):
    global channel
    channel = c


def get_channel():
    return channel


def set_exchange(e):
    global exchange
    exchange = e


def get_exchange():
    return exchange

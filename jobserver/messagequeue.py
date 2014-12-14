exchange = None
monitor_queue = None


def set_exchange(e):
    global exchange
    exchange = e


def get_exchange():
    return exchange


def set_monitor_queue(e):
    global monitor_queue
    monitor_queue = e


def get_monitor_queue():
    return monitor_queue

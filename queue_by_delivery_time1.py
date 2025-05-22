


def queue_by_delivery_time(requests):
    return sorted(requests, key=lambda r: r['delivery_time'])



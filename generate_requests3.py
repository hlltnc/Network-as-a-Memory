

import random

def generate_requests(num_requests, num_nodes, demand_range, simulation_time):
    requests = []

    for i in range(num_requests):
        source = random.randint(0, num_nodes - 1)
        destination = source
        while destination == source:
            destination = random.randint(0, num_nodes - 1)

        # Arrival time anywhere within simulation_time
        arrival_time = round(random.uniform(0, simulation_time), 3)

        # delivery delay: 10%–50% of simulation_time
        delivery_delay = random.uniform(0.1, 0.5) * simulation_time
        delivery_time = round(arrival_time + delivery_delay, 3)

        # leave delay: 10%–50% of simulation_time (after delivery)
        leave_delay = random.uniform(0.1, 0.5) * simulation_time
        leave_time = round(delivery_time + leave_delay, 3)

        demand = random.randint(*demand_range)

        request = {
            "id": i,
            "source": source,
            "destination": destination,
            "arrival_time": arrival_time,
            "delivery_time": delivery_time,
            "leave_time": leave_time,
            "demand": demand
        }

        requests.append(request)

    return requests


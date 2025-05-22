import random

def assign_edge_capacities(graph, capacity_range):
    """
    Her bir kenar için bir capacity değeri atar ve capacities vektöründe depolar.

    Parameters:
        graph (networkx.Graph): Kenarlarına capacity atanacak grafik.
        capacity_range (tuple): Capacity değerinin alınacağı aralık (min, max).

    Returns:
        dict: Her bir kenar için capacity değerlerini içeren sözlük.
    """
    capacities = {}

    # Her bir kenar için capacity değeri ata
    for u, v in graph.edges():
        capacity = random.randint(capacity_range[0], capacity_range[1])
        capacities[(u, v)] = capacity

    return capacities

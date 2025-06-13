import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from generate_requests3 import generate_requests
from assign_edge_capacities1 import assign_edge_capacities
from queue_by_delivery_time1 import queue_by_delivery_time
from calculate_tau1 import calculate_tau
from calculate_fidelity1 import calculate_fidelity
from calculate_entanglement_time1 import calculate_entanglement_time
from Calculate_final_fid1 import calculate_final_fidelity
from select_best_path_by_delay6 import select_best_path_by_delay

success_rates_dizin = []
drop_rates_dizin = []
mean_diff_list = []
mean_diff_success_list = []

for jj in range(1, 3):
    mean_diff = []
    mean_diff_success = []
    simulation_time_list = np.arange(0.000001, 1, 0.0001)
    success_rates = []
    drop_rates = []
    simulation_time=0.5


    threshold_list=np.linspace(0.0001, 0.8, 1000)
    for threshold in threshold_list:
        
        num_requests = 20

        G = nx.read_gml("/home/hilal/Documents/networks/TU DRESDEN2/TU_Dresden_Suedvorstadt_connected2.gml")
        for i, node in enumerate(G.nodes()):
            G.nodes[node]["id"] = i
        id_to_node = {G.nodes[node]["id"]: node for node in G.nodes}

        distances = [((u, v), data["distance_km"]) for u, v, data in G.edges(data=True) if data.get("distance_km") is not None]
        assign_edge_capacities(G, [100, 100])

        num_nodes = G.number_of_nodes()
        requests = generate_requests(num_requests, num_nodes, [10, 10], simulation_time)
        for r in requests:
            r["source"] = id_to_node[r["source"]]
            r["destination"] = id_to_node[r["destination"]]
        sorted_requests = queue_by_delivery_time(requests)

        c = 2e8
        F_av = 0.8
        kappa = 0.2
        c_fiber = 2e8
        fidelities = {}
        tau_values = {}

        for edge, dist in distances:
            dist_m = dist * 1000
            fid = calculate_fidelity(dist_m, c)
            fidelities[edge] = fid
            tau_values[edge] = calculate_tau(F_av, fid, kappa)

        min_tau_value = min(tau_values.values())

        completion_results = []
        dropped_requests = []
        diff_diz = []
        diff_success_diz = []

        for request in sorted_requests:
            arrival = request["arrival_time"]
            delivery = request["delivery_time"]
            path_delay = delivery - arrival
            src = request["source"]
            dst = request["destination"]

            try:
                if path_delay < threshold:
                    path = nx.shortest_path(G, source=src, target=dst, weight="distance_km")
                    dist_km = sum(G[path[i]][path[i + 1]]['distance_km'] for i in range(len(path) - 1))
                    dist_m = dist_km * 1000
                    edge_fids = [fidelities.get((path[i], path[i + 1])) or fidelities.get((path[i + 1], path[i])) for i in range(len(path) - 1)]
                    if None in edge_fids:
                        raise ValueError("Missing fidelity for edge.")
                    min_fid = min(edge_fids)
                    ent_time = calculate_entanglement_time(dist_m, min_fid)
                    trans_time = dist_m / c_fiber
                    total_time = ent_time + trans_time
                    F_final = calculate_final_fidelity(min_fid, kappa, total_time)

                    if F_final >= 0.8 : 
                        completion_time = delivery
                        diff = 0
                        status = "success"
                    else:
                        completion_time = total_time
                        diff = abs(completion_time - delivery)
                        status = "dropped"
                        F_final = calculate_final_fidelity(min_fid, kappa, total_time)

                    result = {
                        "request_id": request["id"],
                        "source": src,
                        "destination": dst,
                        "arrival_time": arrival,
                        "delivery_time": delivery,
                        "completion_time": completion_time,
                        "difference": diff,
                        "status": status
                    }

                else:
                    best_path_info = select_best_path_by_delay(G, src, dst, path_delay, fidelities, kappa, c_fiber)
                    if best_path_info["status"] != "success":
                        raise ValueError("No valid path.")

                    completion_time = best_path_info["total_time"]
                    diff = best_path_info["delay_error"]
                    F_final = best_path_info["F_final"]
                    status = "dropped" if F_final < 0.8 or diff > threshold or completion_time > min_tau_value else "success"

                    result = {
                        "request_id": request["id"],
                        "source": src,
                        "destination": dst,
                        "arrival_time": arrival,
                        "delivery_time": delivery,
                        "completion_time": completion_time,
                        "selected_path": best_path_info["path"],
                        "distance_km": best_path_info["distance_km"],
                        "F_dist": best_path_info["F_dist"],
                        "F_final": best_path_info["F_final"],
                        "difference": diff,
                        "status": status
                    }

                completion_results.append(result)
                diff_diz.append(abs(diff))
                if status == "success":
                    diff_success_diz.append(abs(diff))
                if status == "dropped":
                    dropped_requests.append(result)

            except Exception as e:
                print(f"Error processing request {request['id']}: {e}")
                continue

        total = len(completion_results)
        num_success = len([r for r in completion_results if r["status"] == "success"])
        num_dropped = len([r for r in completion_results if r["status"] == "dropped"])

        success_rates.append((num_success / total) * 100 if total > 0 else 0)
        drop_rates.append((num_dropped / total) * 100 if total > 0 else 0)
        mean_diff.append(sum(diff_diz) / total if total > 0 else 0)
        mean_diff_success.append(sum(diff_success_diz) / num_success if num_success > 0 else 0)




    success_rates_dizin.append(success_rates)
    drop_rates_dizin.append(drop_rates)
    mean_diff_list.append(mean_diff)
    mean_diff_success_list.append(mean_diff_success)

    



# Sonuçları kaydet
np.save("Threshold_network_as_a_mem_DDC01micro.npy", [np.mean(col) for col in zip(*mean_diff_list)])
np.save("Threshold_success_rates_network_as_a_mem_DDC01micro.npy", [np.mean(rates) for rates in zip(*success_rates_dizin)])

average_diff = [np.mean(col) for col in zip(*mean_diff_list)]
average_diff_success = [np.mean(col) for col in zip(*mean_diff_success_list)]
average_success_rates = [np.mean(rates) for rates in zip(*success_rates_dizin)]
average_drop_rates = [np.mean(rates) for rates in zip(*drop_rates_dizin)]




# Grafik 1: Tüm istekler için ortalama zaman farkı
plt.figure(figsize=(10, 6))
plt.plot(threshold_list, average_diff , label="Mean Time Deviation", marker='o', linewidth=2)
plt.xlabel("Number of Requests", fontsize=12)
plt.ylabel("Average Time Difference (seconds)", fontsize=12)
plt.title("Mean Time Deviation vs Number of Requests", fontsize=14)
plt.legend(fontsize=11)
plt.grid(True)
plt.tight_layout()
plt.show()

# Grafik 2: Başarı oranı
plt.figure(figsize=(10, 6))
plt.plot(threshold_list, average_success_rates , label="Success Rate", marker='s', linewidth=2)
plt.xlabel("Number of Requests", fontsize=12)
plt.ylabel("Success Rate (%)", fontsize=12)
plt.title("Success Rate vs Number of Requests", fontsize=14)
plt.legend(fontsize=11)
plt.grid(True)
plt.tight_layout()
plt.show()

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import math
from random import seed, randint
import xml.etree.ElementTree as ET

from generate_requests3 import generate_requests
from assign_edge_capacities1 import assign_edge_capacities
from queue_by_delivery_time1 import queue_by_delivery_time
from calculate_tau1 import calculate_tau
from calculate_fidelity1 import calculate_fidelity
from calculate_entanglement_time1 import calculate_entanglement_time
from Calculate_final_fid1 import calculate_final_fidelity
from select_best_path_by_delay4 import select_best_path_by_delay

success_rates_dizin = []
drop_rates_dizin = []
mean_diff_list = []
mean_diff_success_list = []
mean_completion_success_list=[]

for jj in range(1, 101):
    mean_diff = []
    mean_diff_success=[]
    mean_completion_success=[]
    simulation_time_list = np.arange(3, 21, 1)
    success_rates = []
    drop_rates = []

    for simulation_time in simulation_time_list:
        
        
        num_requests=20
        
        S = "/home/hilal/Documents/networks/TU DRESDEN2/TU_Dresden_Suedvorstadt_connected2.gml"
        G = nx.read_gml(S)

        for i, node in enumerate(G.nodes()):
            G.nodes[node]["id"] = i

        id_to_node = {G.nodes[node]["id"]: node for node in G.nodes}

        distances = []
        for u, v, data in G.edges(data=True):
            distance = data.get('distance_km')
            if distance is not None:
                distances.append(((u, v), distance))

        capacity_range = [100, 100]
        capacities = assign_edge_capacities(G, capacity_range)

        num_nodes = G.number_of_nodes()
        demand_range = [10, 10]
        

        requests = generate_requests(num_requests, num_nodes, demand_range, simulation_time)

        # ID'den node ismine çevirme — önemli düzeltme
        for r in requests:
            r["source"] = id_to_node[r["source"]]
            r["destination"] = id_to_node[r["destination"]]

        sorted_requests = queue_by_delivery_time(requests)

        c = 2 * 10**8
        F_av = 0.8
        kappa = 0.2

        fidelities = {}
        tau_values = {}

        for edge, distance in distances:
            distance_in_meters = distance * 1000
            fidelity = calculate_fidelity(distance_in_meters, c)
            fidelities[edge] = fidelity
            tau = calculate_tau(F_av, fidelity, kappa)
            tau_values[edge] = tau

        min_tau_edge = min(tau_values, key=tau_values.get)
        min_tau_value = tau_values[min_tau_edge]

        completion_results = []
        dropped_requests = []
        diff_diz = []
        diff_success_diz=[]
        completion_success_diz=[]


        for request in sorted_requests:
            arrival = request["arrival_time"]
            delivery = request["delivery_time"]
            path_delay = delivery - arrival

            src = str(request["source"])
            dst = str(request["destination"])

            try:
                best_path_info = select_best_path_by_delay(
                    G=G,
                    src=src,
                    dst=dst,
                    path_delay=path_delay,
                    fidelities=fidelities,
                    kappa=kappa,
                    c_fiber=c
                )

                if best_path_info["status"] != "success":
                    raise ValueError("No valid path found.")

                completion_time = best_path_info["total_time"]
                diff = best_path_info["delay_error"]
                diff_diz.append(abs(diff))

                is_dropped = best_path_info["F_final"] < 0.8 or diff > 1.0
                if  not is_dropped:
                     diff_success=diff
                     diff_success_diz.append(abs(diff_success))
                     completion_success=completion_results
                     completion_success_diz.append(completion_time)
        




                outcome = {
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
                    "status": "dropped" if is_dropped else "success"
                }
                
                    

                completion_results.append(outcome)
                if is_dropped:
                    dropped_requests.append(outcome)

            except Exception as e:
                print(f"Error processing request {request['id']}: {e}")
                continue

        successful_requests = [r for r in completion_results if r["status"] == "success"]
        dropped_requests = [r for r in completion_results if r["status"] == "dropped"]

        num_success = len(successful_requests)
        num_dropped = len(dropped_requests)
        total = num_success + num_dropped

        success_rate = num_success / total * 100 if total > 0 else 0
        drop_rate = num_dropped / total * 100 if total > 0 else 0

        success_rates.append(success_rate)
        drop_rates.append(drop_rate)

        sum_diff_diz = sum(diff_diz)
        if total > 0:
            mean_diff.append(sum_diff_diz / total)
        else:
            mean_diff.append(0)


        sum_diff_succ_diz = sum(diff_success_diz)
        if num_success > 0:
            mean_diff_success.append(sum_diff_succ_diz / num_success)
        else:
            mean_diff_success.append(0)


        sum_completion_success_diz = sum(completion_success_diz)
        if num_success > 0:
            mean_completion_success.append(sum_completion_success_diz / num_success)
        else:
            mean_completion_success.append(0)



    success_rates_dizin.append(success_rates)
    drop_rates_dizin.append(drop_rates)
    mean_diff_list.append(mean_diff)
    mean_diff_success_list.append(mean_diff_success)
    mean_completion_success_list.append(mean_completion_success)

    


print(diff_success_diz)
transposed = list(zip(*success_rates_dizin))
average_success_rates = [np.mean(rates) for rates in transposed]
average_diff = [np.mean(col) for col in zip(*mean_diff_list)]
average_diff_success = [np.mean(suc) for suc in zip(*mean_diff_success_list)]
average_completion_success=[np.mean(vv) for vv in zip(*mean_completion_success_list)]


average_diff_network_as_a_mem1 = average_diff
#np.save("SIMTIMEaverage_diff_network_as_a_meM1.npy", average_diff_network_as_a_mem1)
#np.save("SIMTIMEaverage_success_rates_network_as_a_meM1.npy", average_success_rates)
#np.save("SIMTIMEaverage_success_diff_network_as_a_meM1.npy", average_diff_success)



plt.figure(figsize=(10, 6))
plt.plot(simulation_time_list, average_completion_success, label="Mean Time Deviation", marker='o', linewidth=2)
plt.xlabel("Simulation time", fontsize=12)
plt.ylabel("Average Time Difference (seconds)", fontsize=12)
plt.title("Mean Time Deviation vs Number of Requests", fontsize=14)
plt.legend(fontsize=11)
plt.grid(True)
plt.tight_layout()
plt.show()




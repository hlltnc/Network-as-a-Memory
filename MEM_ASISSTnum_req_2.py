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

success_rates_dizin = []
mean_diff_list = []
mean_diff_success=[]


for jj in range(1, 101):
    
    success_rates = []
    mean_diff = []



    num_requests_list = np.arange(1, 51, 1)
    for num_requests in num_requests_list:
        
        simulation_time=3
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
        assign_edge_capacities(G, capacity_range)

        num_nodes = G.number_of_nodes()
        demand_range = [10, 10]
        

        requests = generate_requests(num_requests, num_nodes, demand_range, simulation_time)
        sorted_requests = queue_by_delivery_time(requests)

        c = 2e8
        F_av = 0.8
        kappa = 0.2

        fidelities = {}
        tau_values = {}

        for edge, distance in distances:
            distance_m = distance * 1000
            fidelity = calculate_fidelity(distance_m, c)
            fidelities[edge] = fidelity
            tau_values[edge] = calculate_tau(F_av, fidelity, kappa)

        min_tau_value = tau_values[min(tau_values, key=tau_values.get)]

        tau_mem = 0.5
    
        c_fiber = 2e8
        sim_time = 0
        time_step = 0.1

        pending_requests = sorted_requests.copy()
        processed_ids = set()
        completion_results = []
        dropped_requests = []
        diff_diz = []
        diff_success_diz=[]
        for r in requests:
            r["source"] = id_to_node[r["source"]]
            r["destination"] = id_to_node[r["destination"]]

        while pending_requests:
            for request in pending_requests[:]:
                arrival = request["arrival_time"]
                delivery_time = request["delivery_time"]
                

                if sim_time >= arrival and request["id"] not in processed_ids:
                    src = str(request["source"])
                    dst = str(request["destination"])

                    try:
                        path = nx.shortest_path(G, source=src, target=dst, weight="distance_km")
                        total_distance_km = sum(G[path[i]][path[i + 1]]["distance_km"] for i in range(len(path) - 1))
                        total_distance_m = total_distance_km * 1000

                        edge_fidelities = [
                            fidelities.get((path[i], path[i + 1])) or fidelities.get((path[i + 1], path[i]))
                            for i in range(len(path) - 1)
                        ]
                        if None in edge_fidelities:
                            raise ValueError("Missing fidelity for an edge in path.")

                        min_fidelity = min(edge_fidelities)
                        ent_time = calculate_entanglement_time(total_distance_m, min_fidelity)
                        transmission_time = total_distance_m / c_fiber

                        
                        #comp_time=transmission_time+ent_time+sim_time

                        
                        wait_time = delivery_time - sim_time
                        F_final = calculate_final_fidelity(min_fidelity, kappa, transmission_time)

                    
                        if wait_time <= tau_mem and F_final >= 0.8:
                           completion_time = delivery_time
                           diff = 0
                           status = "success"
                        elif wait_time > tau_mem and F_final >= 0.8:
                           completion_time =  ent_time + transmission_time
                           diff = abs(completion_time - delivery_time)

                           if diff > 1 and F_final >= 0.8:  # kritik şart
                             status = "dropped"
                           else:
                             status = "success"
                        else:
                           completion_time =  ent_time + transmission_time
                           diff = abs(completion_time - delivery_time)
                           status = "dropped"
                        


                        result = {
                            "request_id": request["id"],
                            "source": src,
                            "destination": dst,
                            "arrival_time": arrival,
                            "leave_time": request["leave_time"],
                            "completion_time": round(completion_time, 6),
                            "delivery_time": delivery_time,
                            "wait_time": round(wait_time, 6),
                            "difference": round(diff, 6),
                            "status": status
                        }



                        diff = abs(result["difference"])
                        diff_diz.append(diff)

                        




                        completion_results.append(result)
                        processed_ids.add(request["id"])
                        pending_requests.remove(request)
                        if status == "dropped":
                            dropped_requests.append(result)




                    except Exception as e:
                        print(f"Error processing request {request['id']}: {e}")
                        pending_requests.remove(request)

            sim_time = round(sim_time + time_step, 3)

        num_success = len([r for r in completion_results if r["status"] == "success"])
        num_dropped = len([r for r in completion_results if r["status"] == "dropped"])
        total_requests = num_success + num_dropped

        success_rate = (num_success / total_requests) * 100 if total_requests > 0 else 0
        success_rates.append(success_rate)
        mean_diff.append(sum(diff_diz) / total_requests if total_requests > 0 else 0)


        sum_diff_succ_diz = sum(diff_success_diz)
        if num_success > 0:
            mean_diff_success.append(sum_diff_succ_diz / num_success)
        else:
            mean_diff_success.append(0)




    success_rates_dizin.append(success_rates)
    mean_diff_list.append(mean_diff)

# Ortalama başarı ve farklar
average_success_rates = [np.mean(col) for col in zip(*success_rates_dizin)]
average_diff = [np.mean(col) for col in zip(*mean_diff_list)]
average_diff_success = [np.mean(suc) for suc in zip(*mean_diff_list)]



np.save("average_diff_memory_assisted_tau_meM_0_5.npy", average_diff)
np.save("average_success_rates_memory_assisted_tau_meM_0_5.npy", average_success_rates)
np.save("average_diff_memory_assisted_tau_meM_0_5_succ.npy", average_diff_success)


# Grafik çizimi
plt.figure(figsize=(10, 6))
plt.plot(num_requests_list, average_diff_success, label="Mean Time Deviation", marker='o', linewidth=2)
plt.xlabel("Number of Requests", fontsize=12)
plt.ylabel("Average Time Difference for succesful req(seconds)", fontsize=12)
plt.title("Mean Time Deviation vs Number of Requests", fontsize=14)
plt.legend(fontsize=11)
plt.grid(True)
plt.tight_layout()
plt.show()





plt.figure(figsize=(10, 6))
plt.plot(num_requests_list, average_diff, label="Mean Time Deviation", marker='o', linewidth=2)
plt.xlabel("Number of Requests", fontsize=12)
plt.ylabel("Average Time Difference (seconds)", fontsize=12)
plt.title("Mean Time Deviation vs Number of Requests", fontsize=14)
plt.legend(fontsize=11)
plt.grid(True)
plt.tight_layout()
plt.show()









# Grafik çizimi
plt.figure(figsize=(10, 6))
plt.plot(num_requests_list, average_success_rates, label="success rate", marker='o', linewidth=2)
plt.xlabel("Number of Requests", fontsize=12)
plt.ylabel("request success rate ", fontsize=12)
#plt.title("Mean Time Deviation vs Number of Requests", fontsize=14)
plt.legend(fontsize=11)
plt.grid(True)
plt.tight_layout()
plt.show()
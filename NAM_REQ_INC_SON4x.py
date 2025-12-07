import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from generate_requests3 import generate_requests
from assign_edge_capacities1 import assign_edge_capacities
from queue_by_delivery_time1 import queue_by_delivery_time
from calculate_tau1 import calculate_tau
from calculate_fidelity1 import calculate_fidelity
from calculate_entanglement_time1 import calculate_entanglement_time
from Calculate_final_fid2 import calculate_final_fidelity
from select_best_path_by_delay6 import select_best_path_by_delay


# -------------------------
# Edge-işgal yardımcıları
# -------------------------
def norm_edge(u, v):
    return tuple(sorted((u, v)))

def intervals_overlap(a_start, a_end, b_start, b_end, eps=1e-12):
    return not (a_end <= b_start + eps or b_end <= a_start + eps)

def path_is_available(path, start_t, end_t, edge_occupancy):
    for i in range(len(path) - 1):
        e = norm_edge(path[i], path[i+1])
        for (s, e_end) in edge_occupancy.get(e, []):
            if intervals_overlap(start_t, end_t, s, e_end):
                return False
    return True

def reserve_path(path, start_t, end_t, edge_occupancy):
    for i in range(len(path) - 1):
        e = norm_edge(path[i], path[i+1])
        edge_occupancy.setdefault(e, []).append((start_t, end_t))

def remove_busy_edges(G, start_t, end_t, edge_occupancy):
    """Return a copy of G with edges busy in [start_t, end_t] removed."""
    H = G.copy()
    to_remove = []
    for u, v in G.edges():
        e = norm_edge(u, v)
        busy_list = edge_occupancy.get(e, [])
        if any(intervals_overlap(start_t, end_t, s, e_end) for (s, e_end) in busy_list):
            to_remove.append((u, v))
    H.remove_edges_from(to_remove)
    return H


# -------------------------
# Simülasyon
# -------------------------
success_rates_dizin = []
drop_rates_dizin = []
mean_diff_list = []
mean_diff_success_list = []

for jj in range(1, 1000):
    mean_diff = []
    mean_diff_success = []
    simulation_time = 0.5                 # RTW (s)
    success_rates = []
    drop_rates = []
    num_requests_list = np.arange(1, 151, 10)

    for num_requests in num_requests_list:
        # Her senaryo başında edge-occupancy sıfırla
        edge_occupancy = {}  # norm_edge -> list of (start_t, end_t)

        threshold = 0.1

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
        alpha = 0.2

        for edge, dist in distances:
            dist_m = dist * 1000
            fidelities[edge] = calculate_fidelity(dist_m, c)

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
                # -----------------------------
                # KISA-PATH (threshold) DAL
                # -----------------------------
                if path_delay < threshold:
                    # 1) En kısa yol
                    path = nx.shortest_path(G, source=src, target=dst, weight="distance_km")
                    dist_km = sum(G[path[i]][path[i + 1]]['distance_km'] for i in range(len(path) - 1))
                    dist_m  = dist_km * 1000

                    # Path fideliteleri
                    edge_fids = [fidelities.get((path[i], path[i + 1])) or fidelities.get((path[i + 1], path[i])) for i in range(len(path) - 1)]
                    if None in edge_fids:
                        raise ValueError("Missing fidelity for edge.")
                    min_fid = min(edge_fids)

                    # Süreler
                    ent_time  = calculate_entanglement_time(dist_m, min_fid)
                    trans_time = dist_m / c_fiber
                    total_time = ent_time + trans_time

                    start_t = arrival
                    end_t   = arrival + total_time

                    # 2) Meşgul mü? Alternatif dene
                    if not path_is_available(path, start_t, end_t, edge_occupancy):
                        H_free = remove_busy_edges(G, start_t, end_t, edge_occupancy)
                        try:
                            path = nx.shortest_path(H_free, source=src, target=dst, weight="distance_km")
                            dist_km = sum(G[path[i]][path[i + 1]]['distance_km'] for i in range(len(path) - 1))
                            dist_m  = dist_km * 1000
                            edge_fids = [fidelities.get((path[i], path[i + 1])) or fidelities.get((path[i + 1], path[i])) for i in range(len(path) - 1)]
                            if None in edge_fids:
                                raise ValueError("Missing fidelity for edge.")
                            min_fid = min(edge_fids)
                            ent_time  = calculate_entanglement_time(dist_m, min_fid)
                            trans_time = dist_m / c_fiber
                            total_time = ent_time + trans_time
                            start_t = arrival
                            end_t   = arrival + total_time
                        except nx.NetworkXNoPath:
                            # Tutarlı drop metrikleri
                            completion_time_abs = arrival + total_time
                            diff = abs(completion_time_abs - delivery)
                            result = {
                                "request_id": request["id"],
                                "source": src,
                                "destination": dst,
                                "arrival_time": arrival,
                                "delivery_time": delivery,
                                "completion_time": completion_time_abs,
                                "difference": diff,
                                "status": "dropped",
                                "reason": "edge_conflict_no_alt"
                            }
                            completion_results.append(result)
                            diff_diz.append(diff)
                            dropped_requests.append(result)
                            continue

                    # 3) Karar: kısa dalda da aynı kural
                    completion_time_abs = arrival + total_time
                    diff = abs(completion_time_abs - delivery)
                    F_final = calculate_final_fidelity(min_fid, kappa, total_time, alpha, dist_km)

                    bad_tau = False
                    ok = (F_final >= 0.8) and (diff <= threshold) and (not bad_tau)


                    
                    if ok:
                        status = "success"
                        completion_time = delivery     # tam hedefe hizaladığını varsayıyorsan
                        # REZERVASYON SADECE BAŞARIDA
                        reserve_path(path, start_t, end_t, edge_occupancy)
                        difference_to_store = 0.0
                    else:
                        status = "dropped"
                        completion_time = completion_time_abs
                        difference_to_store = diff

                    result = {
                        "request_id": request["id"],
                        "source": src,
                        "destination": dst,
                        "arrival_time": arrival,
                        "delivery_time": delivery,
                        "completion_time": completion_time,
                        "selected_path": path,
                        "distance_km": dist_km,
                        "F_final": F_final,
                        "difference": difference_to_store,
                        "status": status
                    }
                    completion_results.append(result)
                    diff_diz.append(abs(difference_to_store))
                    if ok:
                        diff_success_diz.append(0.0)
                    else:
                        dropped_requests.append(result)

                    # Kısa dal tamam — bir sonraki request'e geç
                    continue
                # -----------------------------
                # ELSE: (select_best_path_by_delay)
                # -----------------------------
                best_path_info = select_best_path_by_delay(G=G, source=src, target=dst,
                                                            path_delay=path_delay,
                                                            fidelities=fidelities,
                                                            kappa=kappa, c_fiber=c_fiber)
                if best_path_info["status"] != "success":
                    raise ValueError("No valid path.")

                path       = best_path_info["path"]
                dist_km    = best_path_info["distance_km"]
                min_fid    = best_path_info["F_dist"]     # or recompute from path if needed
                total_time = best_path_info["total_time"]

                start_t = arrival
                end_t   = arrival + total_time

                if not path_is_available(path, start_t, end_t, edge_occupancy):
                    H_free = remove_busy_edges(G, start_t, end_t, edge_occupancy)
                    try:
                        path = nx.shortest_path(H_free, source=src, target=dst, weight="distance_km")
                        dist_km = sum(G[path[i]][path[i + 1]]['distance_km'] for i in range(len(path) - 1))
                        dist_m  = dist_km * 1000
                        edge_fids = [fidelities.get((path[i], path[i + 1])) or fidelities.get((path[i + 1], path[i])) for i in range(len(path) - 1)]
                        if None in edge_fids:
                            raise ValueError("Missing fidelity for edge.")
                        min_fid = min(edge_fids)
                        ent_time  = calculate_entanglement_time(dist_m, min_fid)
                        trans_time = dist_m / c_fiber
                        total_time = ent_time + trans_time
                        start_t = arrival
                        end_t   = arrival + total_time
                    except nx.NetworkXNoPath:
                        completion_time_abs = arrival + total_time
                        diff = abs(completion_time_abs - delivery)
                        result = {
                            "request_id": request["id"],
                            "source": src,
                            "destination": dst,
                            "arrival_time": arrival,
                            "delivery_time": delivery,
                            "completion_time": completion_time_abs,
                            "difference": diff,
                            "status": "dropped",
                            "reason": "edge_conflict_no_alt"
                        }
                        completion_results.append(result)
                        diff_diz.append(diff)
                        dropped_requests.append(result)
                        continue

                # Karar (aynı kural)
                completion_time_abs = arrival + total_time
                diff = abs(completion_time_abs - delivery)
                F_final = calculate_final_fidelity(min_fid, kappa, total_time, alpha, dist_km)

                use_tau_guard = False
                # tau_path = calculate_tau(F_av, min_fid, kappa)
                # bad_tau = (use_tau_guard and total_time > tau_path)
                bad_tau = False

                ok = (F_final >= 0.8) and (diff <= threshold) and (not bad_tau)
                status = "success" if ok else "dropped"
                completion_time = delivery if ok else completion_time_abs

                if status == "success":
                    reserve_path(path, start_t, end_t, edge_occupancy)

                result = {
                    "request_id": request["id"],
                    "source": src,
                    "destination": dst,
                    "arrival_time": arrival,
                    "delivery_time": delivery,
                    "completion_time": completion_time,
                    "selected_path": path,
                    "distance_km": dist_km,
                    "F_final": F_final,
                    "difference": 0.0 if ok else diff,
                    "status": status
                }
                completion_results.append(result)
                diff_diz.append(abs(result["difference"]))
                if ok:
                    diff_success_diz.append(0.0)
                else:
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

# Sonuçları kaydet (opsiyonel)
np.save("NUM_REQ_mean_diff_T05.npy", [np.mean(col) for col in zip(*mean_diff_list)])
np.save("NUM_REQ_success_rates_T05.npy", [np.mean(rates) for rates in zip(*success_rates_dizin)])

# Ortalama metrikler
average_diff = [np.mean(col) for col in zip(*mean_diff_list)]
average_diff_success = [np.mean(col) for col in zip(*mean_diff_success_list)]
average_success_rates = [np.mean(rates) for rates in zip(*success_rates_dizin)]
average_drop_rates = [np.mean(rates) for rates in zip(*drop_rates_dizin)]

# (İstersen aynı plotting kısmını ekleyebilirsin)

# Grafik 1: Tüm istekler için ortalama zaman farkı
plt.figure(figsize=(10, 6))
plt.plot(num_requests_list, average_diff, label="Mean Time Deviation", marker='o', linewidth=2)
plt.xlabel("Number of Requests", fontsize=12)
plt.ylabel("Average Time Difference (seconds)", fontsize=12)
plt.title("Mean Time Deviation vs Number of Requests", fontsize=14)
plt.legend(fontsize=11)
plt.grid(True)
plt.tight_layout()
plt.show()

# Grafik 2: Başarı oranı
plt.figure(figsize=(10, 6))
plt.plot(num_requests_list, average_success_rates, label="Success Rate", marker='s', linewidth=2)
plt.xlabel("Number of Requests", fontsize=12)
plt.ylabel("Success Rate (%)", fontsize=12)
plt.title("Success Rate vs Number of Requests", fontsize=14)
plt.legend(fontsize=11)
plt.grid(True)
plt.tight_layout()
plt.show()

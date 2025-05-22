from calculate_entanglement_time1 import calculate_entanglement_time
from Calculate_final_fid1 import calculate_final_fidelity
import networkx as nx
import math
from itertools import combinations

def select_best_path_by_delay(G, src, dst, path_delay, fidelities, kappa, c_fiber=2e8, max_paths=10, delay_tolerance=1):
    def get_fidelity(u, v):
        return fidelities.get((u, v)) or fidelities.get((v, u))

    all_paths = list(nx.all_simple_paths(G, source=src, target=dst, cutoff=10))
    if not all_paths:
        return {"status": "no_path"}

    path_infos = []

    for path in all_paths[:max_paths]:
        try:
            # Toplam mesafe (metre cinsinden)
            total_distance_km = sum(G[path[i]][path[i + 1]].get("distance_km", 0) for i in range(len(path) - 1))
            total_distance_m = total_distance_km * 1000  # düzeltildi

            # Fidelity hesapla
            edge_fidelities = [get_fidelity(path[i], path[i + 1]) for i in range(len(path) - 1)]
            if None in edge_fidelities:
                continue

            min_fidelity = min(edge_fidelities)
            ent_time = calculate_entanglement_time(total_distance_m, min_fidelity)
            transmission_time = total_distance_m / c_fiber
            total_path_time = ent_time + transmission_time
            F_final = calculate_final_fidelity(min_fidelity, kappa, total_path_time)

            path_info = {
                "path": [path],
                "distance_km": total_distance_km,
                "ent_time": ent_time,
                "transmission_time": transmission_time,
                "total_time": total_path_time,
                "F_dist": min_fidelity,
                "F_final": F_final,
                "delay_error": abs(total_path_time - path_delay)
            }

            if path_info["delay_error"] <= delay_tolerance:
                path_info["status"] = "success"
                return path_info

            path_infos.append(path_info)

        except Exception as e:
            print(f"Path error: {path} — {e}")
            continue

    # Path kombinasyonları
    combo_infos = []
    for path1, path2 in combinations(all_paths[:max_paths], 2):
        try:
            d1_km = sum(G[path1[i]][path1[i + 1]].get("distance_km", 0) for i in range(len(path1) - 1))
            d1 = d1_km * 1000

            fids1 = [get_fidelity(path1[i], path1[i + 1]) for i in range(len(path1) - 1)]
            if None in fids1:
                continue
            min_fid1 = min(fids1)
            ent1 = calculate_entanglement_time(d1, min_fid1)
            t1 = d1 / c_fiber

            d2_km = sum(G[path2[i]][path2[i + 1]].get("distance_km", 0) for i in range(len(path2) - 1))
            d2 = d2_km * 1000

            fids2 = [get_fidelity(path2[i], path2[i + 1]) for i in range(len(path2) - 1)]
            if None in fids2:
                continue
            min_fid2 = min(fids2)
            ent2 = calculate_entanglement_time(d2, min_fid2)
            t2 = d2 / c_fiber

            total_time = ent1 + ent2 + 2*t1 + t2
            combined_fid = min(min_fid1, min_fid2)
            F_final = calculate_final_fidelity(combined_fid, kappa, total_time)

            combo_info = {
                "path": [path1, path2],
                "distance_km": d1_km + d2_km,
                "ent_time": ent1 + ent2,
                "transmission_time": t1 + t2,
                "total_time": total_time,
                "F_dist": combined_fid,
                "F_final": F_final,
                "delay_error": abs(total_time - path_delay)
            }

            if combo_info["delay_error"] <= delay_tolerance:
                combo_info["status"] = "success"
                return combo_info

            combo_infos.append(combo_info)

        except Exception as e:
            print(f"Combo path error: {path1}, {path2} — {e}")
            continue

    all_candidates = path_infos + combo_infos

    if not all_candidates:
        return {"status": "no_valid_path"}

    best = min(all_candidates, key=lambda x: x["delay_error"])
    best["status"] = "success"
    
    return best

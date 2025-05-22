from calculate_entanglement_time1 import calculate_entanglement_time
from Calculate_final_fid1 import calculate_final_fidelity
import networkx as nx
import math
from itertools import combinations


def select_best_path_by_delay(G, src, dst, path_delay, fidelities, kappa, c_fiber=2e8, max_paths=10, delay_tolerance=0.01):
    all_paths = list(nx.all_simple_paths(G, source=src, target=dst, cutoff=10))
    if not all_paths:
        return {"status": "no_path"}

    path_infos = []

    # Tek path'li sonuçları topla
    for path in all_paths[:max_paths]:
        try:
            total_distance_km = sum(G[path[i]][path[i + 1]]["distance_km"] for i in range(len(path) - 1))
            total_distance_m = total_distance_km *1

            edge_fidelities = [
                fidelities.get((path[i], path[i + 1])) or fidelities.get((path[i + 1], path[i]))
                for i in range(len(path) - 1)
            ]
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

            # Eğer tolerans dahilindeyse hemen döndür
            if path_info["delay_error"] <= delay_tolerance:
                path_info["status"] = "success"
                return path_info

            path_infos.append(path_info)

        except Exception as e:
            print(f"Path error: {path} — {e}")
            continue

    # Eğer tek path'lerle uygun bir delay yakalanamadıysa → kombinasyonlara geç
    combo_infos = []
    for path1, path2 in combinations(all_paths[:max_paths], 2):
        try:



            d1 = sum(G[path1[i]][path1[i + 1]]["distance_km"] for i in range(len(path1) - 1)) *1
            fids1 = [fidelities.get((path1[i], path1[i + 1])) or fidelities.get((path1[i + 1], path1[i])) for i in range(len(path1) - 1)]
            if None in fids1:
                continue
            min_fid1 = min(fids1)
            ent1 = calculate_entanglement_time(d1, min_fid1)
            t1 = d1 / c_fiber

            d2 = sum(G[path2[i]][path2[i + 1]]["distance_km"] for i in range(len(path2) - 1)) * 1
            fids2 = [fidelities.get((path2[i], path2[i + 1])) or fidelities.get((path2[i + 1], path2[i])) for i in range(len(path2) - 1)]
            if None in fids2:
                continue
            min_fid2 = min(fids2)
            ent2 = calculate_entanglement_time(d2, min_fid2)
            t2 = d2 / c_fiber

            total_time = ent1 + ent2 + t1 + t2
            combined_fid = min(min_fid1, min_fid2)
            F_final = calculate_final_fidelity(combined_fid, kappa, total_time)

            combo_infos.append({
                "path": [path1, path2],
                "distance_km": (d1 + d2) / 1000,
                "ent_time": ent1 + ent2,
                "transmission_time": t1 + t2,
                "total_time": total_time,
                "F_dist": combined_fid,
                "F_final": F_final,
                "delay_error": abs(total_time - path_delay)
            })

        except Exception as e:
            print(f"Combo path error: {path1}, {path2} — {e}")
            continue

    all_candidates = path_infos + combo_infos

    if not all_candidates:
        return {"status": "no_valid_path"}

    best = min(all_candidates, key=lambda x: x["delay_error"])
    best["status"] = "success"
    return best

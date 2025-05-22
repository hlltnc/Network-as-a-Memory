import math
# 
#  Fidelity formülü (senin verdiğin)



def calculate_final_fidelity(F_dist, kappa, tau):
    return 0.5 + (F_dist - 0.5) * math.exp(-8 * kappa * tau)
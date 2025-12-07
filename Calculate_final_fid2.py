import math
# 
#  Fidelity formülü (senin verdiğin)



def calculate_final_fidelity(F0, kappa, tau, alpha, L):
    """
    Calculates the final fidelity considering both time-dependent decoherence
    and distance-dependent attenuation based on the published model:
    F(L, τ) = 0.5 + (F0 - 0.5) * exp(-8κτ) * exp(-αL)
    """
    return 0.5 + (F0 - 0.5) * math.exp(-8 * kappa * tau) * math.exp(-alpha * L)
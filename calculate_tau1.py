

import math



def calculate_tau(F_av, F_dist, kappa):
    """
    Tau hesaplama fonksiyonu.
    
    Parameters:
        F_av (float): Ortalama fidelite.
        F_dist (float): Mesafeye bağlı fidelite.
        kappa (float): Sabit değer.
        
    Returns:
        float: Tau değeri.
    """
    if F_dist > 0.5 and F_av > 0.5:  # Logaritmanın tanımlı olması için
        return -1 / (8 * kappa) * math.log((F_av - 0.5) / (F_dist - 0.5))
    else:
        return float('inf')  # Tanımsız değer için sonsuz döndür

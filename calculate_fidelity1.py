
import math



def calculate_fidelity(d, c):
   
    return (0.5 + (0.9381 - 0.5) * math.exp(-0.2 * d / c))**2

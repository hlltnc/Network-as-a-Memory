import math

# Constants
C_FIBER = 2 * 10**8  # Speed of light in fiber (m/s)


# Function to calculate eta (transmission parameter)
def calculate_eta(L, Latt):
    Latt=L
    return math.exp(-L / Latt)

# Function to calculate P_failure (failure probability)
def calculate_P_failure(F, eta):
    return (2 * F - 1) * eta / (1 - eta)

# Function to calculate P_success (success probability)
def calculate_P_success(P_failure):
    return 1 - P_failure

# Function to calculate entanglement generation time
# T0 = 2L0 / C_FIBER and <T>0 = T0 / P_success
def calculate_entanglement_time(L0, F):
    Latt = L0  # Attenuation length equals the total length
    eta = calculate_eta(L0, Latt)
    P_failure = calculate_P_failure(F, eta)
    P_success = calculate_P_success(P_failure)

    if P_success <= 0:
        raise ValueError("P_success must be greater than 0 to calculate entanglement generation time.")

    T0 = 2 * L0*1000 / C_FIBER  # Base time for entanglement generation
    T_entanglement = T0 / P_success

    return T_entanglement

# Example inputs
#L0 = 1e3  # Distance between nodes in meters (example: 1 km)
#F = 0.9   # Fidelity of the entangled pair

# Calculate entanglement generation time
#try:
    #entanglement_time = calculate_entanglement_time(L0, F)
    #print(f"Entanglement Generation Time: {entanglement_time:.6f} seconds")
#except ValueError as e:
    #print(e)

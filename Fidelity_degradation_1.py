import numpy as np
import matplotlib.pyplot as plt
from qutip import *

# İdeal Bell durumu (|Φ+⟩)
phi_plus = (tensor(basis(2,0), basis(2,0)) + tensor(basis(2,1), basis(2,1))).unit()
rho_ideal = ket2dm(phi_plus)

# Depolarization channel parametresi (örneğin fiber için ~0.02 / km)
alpha = 0.02  # error rate per km

# Mesafe aralığı (km)
distances = np.linspace(0, 100, 200)

# Fidelity sonuçlarını tutacağımız liste
fidelities = []

# Depolarizasyon kanalı tanımı
def depolarizing_channel(rho, p):
    return (1 - p) * rho + (p / 3) * (sigmax() * rho * sigmax() +
                                     sigmay() * rho * sigmay() +
                                     sigmaz() * rho * sigmaz())

# 2-kübit için depolarizing kanal (her qubit’e uygulanacak)
def two_qubit_depolarizing(rho, p):
    return depolarizing_channel(depolarizing_channel(rho, p).ptrace(0), p).tensor(depolarizing_channel(rho, p).ptrace(1))

# Fidelity hesapla
def fidelity(rho1, rho2):
    return (rho1.sqrtm() * rho2 * rho1.sqrtm()).sqrtm().tr().real ** 2

# Simülasyon döngüsü
for L in distances:
    p = 1 - np.exp(-alpha * L)  # mesafeye bağlı depolarizasyon olasılığı
    noisy_rho = (1 - p) * rho_ideal + (p / 3) * (
        tensor(sigmax(), qeye(2)) * rho_ideal * tensor(sigmax(), qeye(2)) +
        tensor(sigmay(), qeye(2)) * rho_ideal * tensor(sigmay(), qeye(2)) +
        tensor(sigmaz(), qeye(2)) * rho_ideal * tensor(sigmaz(), qeye(2))
    )
    F = fidelity(noisy_rho, rho_ideal)
    fidelities.append(F)

# Grafik
plt.figure(figsize=(8,5))
plt.plot(distances, fidelities, label="Fidelity vs Distance", color="purple")
plt.xlabel("Distance (km)")
plt.ylabel("Fidelity")
plt.title("Fidelity Degradation over Distance in a Depolarizing Channel")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

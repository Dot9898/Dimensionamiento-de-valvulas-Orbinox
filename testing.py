
from iapws import IAPWS95

w = IAPWS95(T=298.15, P=1e6)  # T in K, P in Pa
print(type(w))
print(w.rho)  # density in kg/m³

for t in range(200):
    try:
        print(t, IAPWS95(T=t, P=101.325).rho)
    except:
        pass

















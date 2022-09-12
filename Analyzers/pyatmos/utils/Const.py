import numpy as np
# Some physical constants at sea level
R0 = 6371.0008 # volumetric radius of the Earth, [km] 
g0 = 9.80665 # standard gravity acceleration, [m/s^2]
M0 = 28.9644 # mean molecular weight, [kg/kmol]
R_air = 8314.32/M0 # gas constant for dry air, [J/kg/K]
gamma = 1.4 # specific heat ratio, namely the ratio of constant-pressure to constant-volume specific heat
T0 = 288.15 # temperature, [K]
p0 = 101325 # pressure, [Pa]
h0 = 0 # height, [km] 

pi = np.pi
twopi = 2*np.pi  
fourpi = 4*np.pi
degrad = pi / 180
al10 = np.log(10)

# AVOGAD is Avogadro's number in mks units (molecules/kmol)
avogad = 6.02257e26
pivo2 = 1.5707963
pivo4 = 1.5707963  

# RSTAR is the universal gas-constant in mks units (joules/K/kmol)
rstar = 8314.32

x = np.arange(0.5,48)/24
"""
The U.S. Standard Atmosphere 1976(USSA76) is an idealized, steady-state model of
mean annual conditions of Earth's atmosphere from the surface to 86 km at
latitude 45N, as it is assumed to exist during a period with moderate solar
activity.
"""

import numpy as np
from ..utils import Const
 
def lapse_tp(t_lower, p_lower, lr, h_lower, h_upper):
    '''
    Calculate the temperature and pressure at a given geopotential altitude above base of a specific layer.
    The temperature is computed by the linear interpolation with the slope defined by lapse rates. 
    The pressure is computed from the hydrostatic equations and the perfect gas law. 
    See the detailed documentation in http://www.pdas.com/hydro.pdf

    Usage:
    [t_upper, p_upper] = lapse_tp(t_lower, p_lower, lr, h_lower, h_upper)

    Inputs:
    t_lower -> [float] temperature[K] at the lower boundary of the subset in the specific layer
    p_lower -> [float] pressure[Pa] at the lower boundary of the subset in the specific layer
    lr -> [float] lapse rate[K/m] for the specific layer
    h_lower -> [float] geopotential altitude[m] at the lower boundary of the subset in the specific layer
    h_upper -> [float] geopotential altitude[m] at the upper boundary of the subset in the specific layer
    
    Outputs:
    t1 -> [float] temperature[K] at the upper boundary of the subset in the specific layer
    p1 -> [float] pressure[Pa] at the upper boundary of the subset in the specific layer
    
    Reference: Public Domain Aeronautical Software(http://www.pdas.com/atmos.html) 
               https://gist.github.com/buzzerrookie/5b6438c603eabf13d07e
    '''
    R_air,g0 = Const.R_air,Const.g0

    if lr == 0:
        t_upper = t_lower
        p_upper = p_lower * np.exp(-g0 / R_air / t_lower * (h_upper - h_lower)*1e3)
    else:
        t_upper = t_lower + lr * (h_upper - h_lower)
        p_upper = p_lower * (t_upper / t_lower) ** (-g0 / (lr/1e3) / R_air)

    return t_upper,p_upper

def ussa76(h):
    '''
    Implements the U.S. Standard Atmosphere 1976(USSA76) up to 86km. 
    The standard atmosphere is defined as a set of layers by specified geopotential altitudes and lapse rates.
    The temperature is computed by linear interpolation with the slope defined by the lapse rate. 
    The pressure is computed from the hydrostatic equations and the perfect gas law; the density follows from the perfect gas law. 

    Usage:
    [rho, T, P, C, eta, Kc] = ussa76(h)

    Inputs:
    h -> [float] geopotentail altitude, [km]

    Outputs:
    rho -> [float] density at a given altitude, [kg/m^3]
    T -> [float] temperature ..., [K]
    P -> [float] pressure ..., [Pa]
    C -> [float] speed of sound ..., [m/s]
    eta -> [float] dynamic viscosity ..., [kg/m/s]
    Kc -> [float] thermal conductivity ..., [J/(m*s*K)]
    
    Note: the geometric altitude should be in [-0.611,86] km, otherwise the output will be extrapolated for those input altitudes.

    Reference: 
        U.S. Standard Atmosphere, 1976, U.S. Government Printing Office, Washington, D.C. 
        Public Domain Aeronautical Software(http://www.pdas.com/atmos.html) 
        https://gist.github.com/buzzerrookie/5b6438c603eabf13d07e
        https://ww2.mathworks.cn/help/aerotbx/ug/atmosisa.
        http://www.braeunig.us/space/atmmodel.htm#USSA1976
    '''
    T0,p0,h0 = Const.T0,Const.p0,Const.h0
    R_air,M0,gamma = Const.R_air,Const.M0,Const.gamma

    # the lower atmosphere below 86km is separated into seven layers 
    geopotential_alt = [-np.inf, 11, 20, 32, 47, 51, 71, np.inf] # Geopotential altitudes above MSL, [km]

    lr = np.array([-6.5, 0, 1, 2.8, 0, -2.8, -2]) # Lapse rate, [K/km]   

    for i in range(len(lr)):
        if h <= geopotential_alt[i+1]:
            T, P = lapse_tp(T0, p0, lr[i], h0, h)
            break
        else:
            # if altitudes are greater than the first several layers, then it has to integeate these layers first.
            T0, p0 = lapse_tp(T0, p0, lr[i], h0, geopotential_alt[i+1])
            h0 = geopotential_alt[i+1]

    # density
    rho = P / (R_air * T)

    # speed of sound
    C = np.sqrt(gamma * R_air * T)

    # dynamic viscosity by Sutherland's law
    eta = 1.458e-6*T**1.5/(T+110.4) 

    # thermal conductivity
    Kc = 2.64638e-3 * T ** 1.5 / (T + 245.4 * (10 ** (-12.0 / T))) 

    return rho,T,P,C,eta,Kc
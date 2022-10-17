'''
Because of the interest of aerospace engineers and atmospheric scientists in 
conditions at much higher altitudes than those of the U.S. Standard Atmosphere 
1976(USSA 1976), members of the U.S. Committee on Extension to the Standard 
Atmosphere(COESA 1976) agreed to extend it to 1000 km.
'''

import FreeCAD
import numpy as np
# from pkg_resources import resource_filename

from  .ussa76 import ussa76
from ..utils import Const
from ..utils.utils import alt_conver,check_altitude

from ..class_atmos import ATMOS

def coesa76(alts, alt_type='geometric'):
    '''
    Implements the U.S. Committee on Extension to the Standard Atmosphere(COESA 1976).

    Usage:
    [rhos, Ts, Ps] = coesa76(h)

    Inputs:
    alts -> [float list/array] geometric or geopotentail altitudes, [km]

    Outputs:
    rhos -> [float array] densities at a set of given altitudes, [kg/m^3]
    Ts -> [float] temperatures ..., [K]
    Ps -> [float] pressures ..., [Pa]
    
    Note: the geometric altitudes should be in [-0.611,1000] km, otherwise the output will be extrapolated for those input altitudes.

    Reference: 
        U.S. Standard Atmosphere, 1976, U.S. Government Printing Office, Washington, D.C. 
        http://www.braeunig.us/space/atmmodel.htm#USSA1976
        https://docs.poliastro.space/en/stable/index.html
    '''

    # Base altitude for the COESA 1976, [km].
    zb = np.array([86, 91, 100, 110, 120, 150, 200, 300, 500, 750, np.inf])

    # load the coefficients used to approximate density and pressure above 86km 
    # data_path = resource_filename('pyatmos', 'data/') - Modify to use FreeCAD path functions
    data_path = FreeCAD.getUserAppDataDir() + "Mod/Rocket/Analyzers/pyatmos/data/"
    data = np.load(data_path+'coesa76_coeffs.npz')
    rho_coeffs,p_coeffs = data['rho'],data['p']

    R0 = Const.R0 # volumetric radius for the Earth, [km] 

    # Get geometric and geopotential altitudes
    zs,hs = alt_conver(alts, alt_type)

    # Test if altitudes are inside valid range
    check_altitude(zs,(-0.611,1e3),'warning')  

    # inds = np.zeros_like(zs,dtype=int)
    np.zeros_like(zs,dtype=int)
    rhos,Ts,Ps = np.zeros((3,len(zs)))

    j = 0
    for z,h in zip(zs,hs):

        if z <= zb[0]: 
            rho,T,P,Cs,eta,Kc = ussa76(h)
        else:
            if z > zb[0] and z <= zb[1]:
                T = 186.8673
            elif z > zb[1] and z <= zb[3]:
                T = 263.1905 - 76.3232 * np.sqrt(1 - ((z - 91) / 19.9429) ** 2)
            elif z > zb[3] and z <= zb[4]:
                T = 240 + 12 * (z - 110)
            else:
                epsilon = (z - 120) * (R0 + 120) / (R0 + z)
                T = 1e3 - 640 * np.exp(-0.01875 * epsilon)  

            ind = np.where((z - zb) >= 0)[0][-1]

            # A 4th order polynomial is used to approximate density and pressure.  
            # This is directly taken from: http://www.braeunig.us/space/atmmodel.htm
            poly_rho = np.poly1d(rho_coeffs[ind])
            poly_p = np.poly1d(p_coeffs[ind])
            rho = np.exp(poly_rho(z))
            P = np.exp(poly_p(z))

        rhos[j],Ts[j],Ps[j] = rho,T,P
        j += 1    

        info = {'rho':rhos,'T':Ts,'P':Ps}
 
    return ATMOS(info)             
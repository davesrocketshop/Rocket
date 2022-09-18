import numpy as np
import warnings
from . import Const

def vectorize(x):
    '''
    Vectorize a number(int, float) or a list to a numpy array.
    '''
    try:
        n = len(x)
        x = np.array(x)
    except:
        x = np.array([x])
    return x    
          
def wraplon(lon):
    '''
    Wrap a longitude in range of [0,360] to [-180,180].

    Usage:
    lon_wrap = wraplon(lon)

    Inputs:
    lon -> [float] longitude in range of [0,360]

    Outputs:
    lon_wrap -> [float] wrapped longitude in range of [-180,180]
    '''
    if lon > 180:
        lon_wrap = lon - 360
    else:
        lon_wrap = lon
    return lon_wrap 

def wraplons(lons):
    '''
    Wrap a set of longitudes in range of [0,360] to [-180,180].

    Usage:
    lons_wrap = wraplons(lons)

    Inputs:
    lons -> [float list/array] longitudes in range of [0,360]

    Outputs:
    lons_wrap -> [float array] wrapped longitudes in range of [-180,180]
    '''
    lons = vectorize(lons)
    lons_wrap = lons.copy()
    flags = lons > 180
    lons_wrap[flags] = lons[flags] - 360

    return lons_wrap     

def hms_conver(h,m,s):
    '''
    Convert the form of hour/minute/second to hours and seconds.

    Uasge:
    hours,seconds = hms_conversion(h,m,s)
    '''
    hours = h + m/60 + s/3.6e3
    seconds = h*3.6e3 + m*60 + s
    return hours,seconds

def ydhms_days(ydhms):
    '''
    Convert the form of hour/minute/second to hours and seconds.

    Uasge:
    hours,seconds = hms_conversion(h,m,s)
    '''
    days = ydhms[1] + ydhms[2]/24 + ydhms[3]/1440 + ydhms[4]/86400 - 1
    return days

def alt_conver(alts,alt_type='geometric'):
    '''
    Fulfill conversions between geometric altitudes and geopotential altitudes.  

    Usage:
    zs,hs = alt_conver(alts,'geometric') 
    or
    zs,hs = alt_conver(alts,'geopotential') 

    Inputs:
    alts -> [float list/array] geometric altitudes or geopotential altitudes, [km]
    
    Parameters:
    alt_type -> [string] 'geometric' or 'geopotential'

    Outputs:
    zs -> [float array] geometric altitudes, [km]
    hs -> [float array] geopotential altitudes, [km]
    '''

    alts = vectorize(alts)

    R0 = Const.R0

    if alt_type == 'geometric': 
        zs = alts
        # from geometric altitude to geopotential altitude
        hs = zs*R0/(R0+zs)  

    elif alt_type == 'geopotential':
        hs = alts
        # from geopotential altitude to geometric altitude
        zs = hs*R0/(R0-hs)  
    return zs,hs

def check_altitude(zs,z_range,mode):
    '''
    Checks if altitudes are inside a valid range.

    Inputs:
    zs -> [float list/array] geometric altitude to be checked
    lower_z -> [float] lower limit of geometric altitudes
    upper_z -> [float] upper limit of geometric altitudes
    '''
    zs = np.array(zs)

    lower_z,upper_z = z_range
    # Assert in range

    if (zs < lower_z).any() or (zs > upper_z).any():
        msg_warning = "Geometric altitudes are outside the range of [{}, {}] km. Output values will be extrapolated for those heights.".format(lower_z,upper_z)
        msg_error = "Geometric altitudes are outside the range of [{}, {}] km.".format(lower_z,upper_z)
        if mode == 'warning':
            warnings.warn(msg_warning)      
        elif mode == 'error':
            raise Exception(msg_error)  
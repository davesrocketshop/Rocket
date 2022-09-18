'''
pyatmos utils subpackage

This subpackage defines the following functions:

Const.py - Defines some basic physical constants at sea level.

try_download.py
    tqdm_request - Try to download files from a remote server by request with a colored progress bar.

utils.py
    vectorize - Vectorize a number(int, float) or a list to a numpy array.
    wraplon - Wrap a longitude in range of [0,360] to [-180,180]
    hms_conver - Convert the form of hour/minute/second to hours and seconds.
    alt_conver - Fulfill conversions between geometric altitudes and geopotential altitudes. 
    check_altitude - Checks if altitudes are inside a valid range.
'''
# Welcome to ATMOS

[![PyPI version shields.io](https://img.shields.io/pypi/v/pyatmos.svg)](https://pypi.python.org/pypi/pyatmos/) [![PyPI pyversions](https://img.shields.io/pypi/pyversions/pyatmos.svg)](https://pypi.python.org/pypi/pyatmos/) [![PyPI status](https://img.shields.io/pypi/status/pyatmos.svg)](https://pypi.python.org/pypi/pyatmos/) [![GitHub contributors](https://img.shields.io/github/contributors/lcx366/ATMOS.svg)](https://GitHub.com/lcx366/ATMOS/graphs/contributors/) [![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/lcx366/ATMOS/graphs/commit-activity) [![GitHub license](https://img.shields.io/github/license/lcx366/ATMOS.svg)](https://github.com/lcx366/ATMOS/blob/master/LICENSE) [![Documentation Status](https://readthedocs.org/projects/pystmos/badge/?version=latest)](http://pyatmos.readthedocs.io/?badge=latest)

This package is an archive of scientific routines that estimates the vertical structure of atmosphere with various *atmospheric density models*, such as **Exponential**(-0.611\~1000 km), **COESA76**(-0.611\~1000 km), **NRLMSISE-00**(0\~2000 km), and **JB2008**(90\~2500 km). 

The **NRLMSISE-00** model was developed by the US Naval Research Laboratory. It is based on mass spectrometry and incoherent radar scatter data, also incorporates drag and accelerometer data, and accounts for anomalous oxygen at high altitudes(>500 km). It is recommended by the International Committee on Space Resarch (COSPAR) as the standard for atmospheric composition. Two indices are used in this model: *F10.7* (both the daily solar flux value of the previous day and the 81-day average centred on the input day) and $A_p$ (geomagnetic daily value).

The **JB2008** (Jacchia-Bowman) model is a newer model developed by Space Environment Technologies(SET) and the US Air Force Space Command. The model accounts for various phenomena related to EUV heating of the thermosphere and uses the DST index as the driver of global density changes. The model is complementary to the NRLMSISE00 model and is more accurate during times of high solar activity and geomagnetic storms. It is recommended by COSPAR as the standard for thermospheric density in satellite drag calculations. Four solar indices and two geomagnetic activity indices are used in this model: *F10.7* (both tabular value one day earlier and the 81-day average centred on the input time); *S10.7* (both tabular value one day earlier and the 81-day average centred on the input time); *M10.7* (both tabular value five days earlier and the 81-day average centred on the input time); Y10.7 (both tabular value five days earlier and the 81-day average centred on the input time); $a_p$ (3 hour tabular value); and *DST* (converted and input as a dTc temperature change tabular value on the input time).

The **Exponential** returns

- the mass density

The **COESA76** returns

- the mass density,  temperature, and pressure at the altitude

The **NRLMSISE-00** returns

- the number densities of atmospheric constituents including N$_2$, O$_2$, Ar, He, O, N, and anomalous oxygen at altitude above 500 km

- the temperature at the altitude

- the total mass density including the anomalous oxygen component

The **JB2008** returns

- the temperature at the altitude

- the total mass density

## How to install

On Linux, macOS and Windows architectures, the binary wheels can be installed using **pip** by executing one of the following commands:

```sh
pip install pyatmos
pip install pyatmos --upgrade # to upgrade a pre-existing installation
```

## How to use

#### Exponential

```python
>>> from pyatmos import expo
>>> expo_geom = expo([0,20,40,60,80]) # geometric altitudes by default
>>> print(expo_geom.rho) # [kg/m^3]
>>> # expo_geop = expo([0,20,40,60,80],'geopotential') # geopotential altitudes

[1.22500000e+00 7.76098911e-02 3.97200000e-03 3.20600000e-04
 1.90500000e-05]
```

#### COESA 1976

```python
>>> from pyatmos import coesa76
>>> coesa76_geom = coesa76([0,20,40,60,80]) # geometric altitudes by default
>>> print(coesa76_geom.rho) # [kg/m^3]
>>> print(coesa76_geom.T) # [K]
>>> print(coesa76_geom.P) # [Pa]
>>> # coesa76_geop = coesa76([0,20,40,60,80],'geopotential') # geopotential altitudes

[1.22499916e+00 8.89079563e-02 3.99535051e-03 3.09628985e-04
 1.84514759e-05]
[288.15       216.65       250.35120115 247.01740767 198.63418825]
[1.01325000e+05 5.52919008e+03 2.87122194e+02 2.19548951e+01
 1.05207648e+00] 
```

#### NRLMSISE-00

*Before using NRLMSISE-00, the space weather data needs to be prepared in advance.*

```python
>>> from pyatmos import download_sw_nrlmsise00,read_sw_nrlmsise00
>>> # Download or update the space weather file from www.celestrak.com
>>> swfile = download_sw_nrlmsise00() 
>>> # Read the space weather data
>>> swdata = read_sw_nrlmsise00(swfile) 
```

```python
>>> from pyatmos import nrlmsise00
>>> # Set a specific time and location
>>> t = '2014-07-22 22:18:45' # time(UTC) 
>>> lat,lon,alt = 25,102,600 # latitude, longitude in [degree], and altitude in [km]
>>> nrl00 = nrlmsise00(t,(lat,lon,alt),swdata)
>>> print(nrl00.rho) # [kg/m^3]
>>> print(nrl00.T) # [K]
>>> print(nrl00.nd) # composition in [1/m^3]

1.714115212984513e-14
765.8976564552341
{'He': 645851224907.2849, 'O': 456706971423.5056, 'N2': 531545420.00015724, 'O2': 2681352.1654067687, 'Ar': 406.9308900607773, 'H': 157249711103.90558, 'N': 6759664327.87355, 'ANM O': 10526544596.059282}
```

#### JB2008

*Before using JB2008, the space weather data needs to be prepared in advance.*

```python
>>> from pyatmos import download_sw_jb2008,read_sw_jb2008
>>> # Download or update the space weather file from https://sol.spacenvironment.net
>>> swfile = download_sw_jb2008() 
>>> # Read the space weather data
>>> swdata = read_sw_jb2008(swfile) 
```

```python
>>> from pyatmos import jb2008
>>> # Set a specific time and location
>>> t = '2014-07-22 22:18:45' # time(UTC) 
>>> lat,lon,alt = 25,102,600 # latitude, longitude in [degree], and altitude in [km]
>>> jb08 = jb2008(t,(lat,lon,alt),swdata)
>>> print(jb08.rho) # [kg/m^3]
>>> print(jb08.T) # [K]

1.2991711750265394e-14
754.2803276187265
```

## Change log
- **1.2.3 — Jun 7, 2021**
  - Added atmospheric models **JB2008**
  - Changed the output of the result to an instance
  - Improved the code structure for NRLMSISE-00, and the running speed is nearly threefold
- **1.2.1 — Jan 22, 2021**
  - Added **Exponential Atmosphere** up to 1000 km
  - Added **Committee on Extension to the Standard Atmosphere(COESA)** up to 1000 km
  - Completed part of the help documentation for NRLMSISE-00
  - Improved the code structure to make it easier to read
- **1.1.2 — Jul 26, 2020**
  - Added colored-progress bar for downloading data
- **1.1.0 — Mar 29,  2020**
  - Added the International Standard Atmosphere(ISA) Model up to 86kms  

## Next release

- Because there is a **45-day lag** between the current Day-Of-Year and the last data DOY in the indices files provided by Space Environment Technologies(SET), the forecasts through the last data DOY out to 137 days (5 solar rotations) need to be estimated using machine learning or other methods.
- Add other atmospheric models, such as the **Earth Global Reference Atmospheric Model(Earth-GRAM) 2016**, and the **Drag Temperature Model(DTM)2013**.

## Reference

- U.S. Standard Atmosphere, 1976, U.S. Government Printing Office, Washington, D.C. 
- [Public Domain Aeronautical Software](http://www.pdas.com/atmos.html) 
- https://gist.github.com/buzzerrookie/5b6438c603eabf13d07e
- https://ww2.mathworks.cn/help/aerotbx/ug/atmosisa.html
- [Original Fortran and C code](https://ccmc.gsfc.nasa.gov/pub/modelweb/atmospheric/msis/)
- [MSISE-00 in Python and Matlab](https://github.com/space-physics/msise00)
- [NRLMSISE-00 Atmosphere Model - Matlab](https://ww2.mathworks.cn/matlabcentral/fileexchange/56253-nrlmsise-00-atmosphere-model?requestedDomain=zh)
- [NRLMSISE-00 Atmosphere Model - Aerospace Blockset](https://www.mathworks.com/help/aeroblks/nrlmsise00atmospheremodel.html?requestedDomain=)
- [NRLMSISE-00 Atmosphere Model - CCMC](https://ccmc.gsfc.nasa.gov/modelweb/models/nrlmsise00.php)
- [NRLMSISE-00 empirical model of the atmosphere: Statistical comparisons and scientific issues](http://onlinelibrary.wiley.com/doi/10.1029/2002JA009430/pdf)
- [ATMOSPHERIC MODELS](http://www.braeunig.us/space/atmmodel.htm)
- [poliastro-Atmosphere module](https://docs.poliastro.space/en/latest/autoapi/poliastro/earth/atmosphere/index.html?highlight=poliastro.earth.atmosphere)
- [ATMOSPHERE API](https://amentum.com.au/atmosphere)
- [COSPAR International Reference Atmosphere - 2012](https://spacewx.com/wp-content/uploads/2021/03/chapters_1_3.pdf)


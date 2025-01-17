.. $Id$
   pyFprime documentation master file, created by
   sphinx-quickstart on Sat Aug 20 11:11:54 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pyFPRIME and ABSORB 
====================================

This project contains two python GUI programs used for computing 
approximate x-ray scattering cross sections (f, f' and f") for individual 
elements using the Cromer & Liberman algorithm 
(reference: `Acta Cryst. 1981 v.A37, p.267 <http://dx.doi.org/10.1107/S0567739481000600>`_). 

* pyFPRIME computes and plots elemental scattering factors. 
* ABSORB computes scattering and absorption for a given
   composition and makes an attempt to estimate density as well. 
   ABSORB can be also accessed as a web utility 
   (see http://11bm.xor.aps.anl.gov/absorb/absorb.php).

Note that these computations are performed for elements between 
Li - Cf and in the X-ray wavelength range 0.05 - 3.0 :math:`\AA` (4.13-248 keV) 
using the Cromer & Liberman algorithm and orbital cross-section tables. 
Note that the Cromer - Liberman algorithm fails in computing f' for 
wavelengths < 0.16 :math:`\AA` (> 77.48 keV) for the heaviest elements (Au-Cf) 
and fails to correctly compute f', f" and mu for 
wavelengths > 2.67 :math:`\AA` (< 4.64 keV) for very heavy elements (Am-Cf).

To obtain a copy of the files see the trunk directory in Trac or use 
subversion to download from 
https://subversion.xor.aps.anl.gov/pyFprime/trunk/. 
This software runs in Windows, Linux and Mac OS X, provided a working 
python interpreter with WxPython and Matplotlib is installed. 
We have used the Enthought Python Distribution.

Contact: `Robert B. Von Dreele <vondreele@anl.gov>`_


Table of Contents:

.. toctree::
   :maxdepth: 1
   :glob:
   
   toc

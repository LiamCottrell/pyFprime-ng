#!/usr/bin/env python

########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

from distutils.core import setup
import os
import sys

#  http://docs.python.org/distutils/setupscript.html
#  http://docs.python.org/install/index.html

data_files = [
    ('.', ['*.dat', 'readme.txt']),
]

long_description = '''For calculating real and resonant X-ray scattering factors to 250keV;       
based on Fortran program of Cromer & Liberman corrected for 
Kissel & Pratt energy term; Jensen term not included'''

setup(name = 'pyFprime',
      version = '0.2.0',
      author = 'Robert B. Von Dreele (Argonne National Laboratory)',
      author_email = 'vondreele@anl.gov',
      url         = 'https://subversion.xor.aps.anl.gov/trac/pyFprime',
      license = '(c) 2008',
      description = 'calculate real and resonant X-ray scattering factors',
      long_description = long_description,
      packages=['pyFprime',],
      package_dir={'pyFprime': 'src/pyFprime'},
      package_data = {'pyFprime': ['*.dat', 'readme.txt']},
)

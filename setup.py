# -*- coding: utf-8 -*-
# Copyright © 2018 Clark Germany GmbH
"""
.. module:: TODO
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann aljosha.friemann@clark.de

"""

import os, sys
from subprocess import Popen, PIPE

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

from kinja import __version__

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), 'r').read()

setup(name             = "kinja",
      author           = "Aljosha Friemann",
      author_email     = "aljosha.friemann@clark.de",
      description      = "Script to template files",
      url              = "https://www.github.com/ClarkSource/kinja.git",
      download_url     = "https://github.com/ClarkSource/kinja/archive/{}.tar.gz".format(__version__),
      keywords         = [],
      version          = __version__,
      # license          = read('LICENSE.txt'),
      # long_description = read('README.rst'),
      install_requires = ['click', 'Jinja2', 'PyYAML'],
      extras_require   = {':python_version == "2.7"': ['futures']},
      entry_points     = { 'console_scripts': ['kinja=kinja.cli:root'] },
      classifiers      = [],
      packages         = find_packages(),
      platforms        = 'linux'
)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8

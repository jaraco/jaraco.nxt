# -*- coding: UTF-8 -*-

""" Setup script for building jaraco.nxt distribution

Copyright © 2008 Jason R. Coombs
"""

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

__author__ = 'Jason R. Coombs <jaraco@jaraco.com>'
__version__ = '$Rev$'[6:-2]
__svnauthor__ = '$Author$'[9:-2]
__date__ = '$Date$'[7:-2]

setup (name = 'jaraco.nxt',
		version = '1.0',
		description = 'Logo Mindstorms NXT Routines',
		author = 'Jason R. Coombs',
		author_email = 'jaraco@jaraco.com',
		url = 'http://www.jaraco.com/',
		packages = find_packages('src'),
		package_dir = {'':'src'},
		namespace_packages = ['jaraco',],
		license = 'MIT',
		classifiers = [
			"Development Status :: 4 - Beta",
			"Intended Audience :: Developers",
			"Programming Language :: Python",
		],
		entry_points = {
		},
		install_requires=[
#			'pyserial>=2.2',
		],
		extras_require = {
		},
		dependency_links = [
			"http://www.jaraco.com/ASP/eggs",
		],
		tests_require=[
			'nose>=0.10',
		],
		test_suite = "nose.collector",
	)

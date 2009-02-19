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
		version = '1.2',
		description = 'Logo Mindstorms NXT Routines',
		author = 'Jason R. Coombs',
		author_email = 'jaraco@jaraco.com',
		url = 'http://www.jaraco.com/projects/jaraco.nxt',
		packages = find_packages(exclude=['ez_setup', 'tests', 'examples']),
		zip_safe=True,
		namespace_packages = ['jaraco',],
		license = 'MIT',
		classifiers = [
			"Development Status :: 4 - Beta",
			"Intended Audience :: Developers",
			"Programming Language :: Python",
		],
		entry_points = dict(
			console_scripts = [
				'nxt-control = jaraco.nxt.controller:serve_forever',
			],
		),
		install_requires=[
			'pyserial>=2.2',
			'enum>=0.4.3',
			'jaraco.util>=2.0',
		],
		extras_require = {
			'input': 'jaraco.input>=1.0dev',
		},
		dependency_links = [
		],
		tests_require=[
			'nose>=0.10',
		],
		test_suite = "nose.collector",
	)

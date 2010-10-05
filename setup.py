# -*- coding: UTF-8 -*-

""" Setup script for building jaraco.nxt distribution

Copyright © 2008-2010 Jason R. Coombs
"""

from setuptools import find_packages

name = 'jaraco.nxt'

setup_params = dict(
	name = name,
	use_hg_version=True,
	description = 'Logo Mindstorms NXT Routines',
	long_description = open('docs/index.txt').read().strip(),
	author = 'Jason R. Coombs',
	author_email = 'jaraco@jaraco.com',
	url = 'http://pypi.python.org/pypi/'+name,
	packages = find_packages(),
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
	],
	extras_require = {
		'input': 'jaraco.input>=1.1dev',
	},
	dependency_links = [
	],
	tests_require=[
		'nose>=0.10',
	],
	test_suite = "nose.collector",
	setup_requires = [
		'hgtools >= 0.4.7',
	],
)

if __name__ == '__main__':
	from setuptools import setup
	setup(**setup_params)

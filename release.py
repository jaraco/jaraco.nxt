import os
import sys

# a quick little fix for PyPI
if sys.platform in ('win32',):
	if not os.environ.has_key('HOME'):
		drivepath = map(os.environ.get, ('HOMEDRIVE', 'HOMEPATH'))
		os.environ['HOME'] = os.path.join(*drivepath)

sys.argv[1:] = ['egg_info', '-RDb', '', 'sdist', 'upload']
setup_file = os.path.join(os.path.dirname(__file__), 'setup.py')
execfile(setup_file)
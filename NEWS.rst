v2.2.1
======

No significant changes.


v2.2.0
======

Features
--------

- Require Python 3.8 or later.


v2.1.0
======

Refreshed package. Use PEP 420 for namespace package.

2.0
===

Switch to `pkgutil namespace technique
<https://packaging.python.org/guides/packaging-namespace-packages/#pkgutil-style-namespace-packages>`_
for the ``jaraco`` namespace.

1.5
===

* Added Python 3 support. Tests pass, but many operations are untested.
* Moved hosting to Git and Github.
* Fixed bug in InputPort where port 4 could not be indicated.

1.4
===

* Fixed issue in discovery when PyBluez is not installed.
* Added a writeTimeout to the device discovery.
* Now requires pyserial 2.4 or later.
* Fixed read_input example. Fixes #1.

1.3.2
=====

* Move to Mercurial repository and bitbucket hosting.
* Added example of reading from a sensor port.

1.3.1
=====

* Bug fixes in messages.MessageWrite.

1.3
===

* Added device discovery and support for Bluetooth Sockets using the
  PyBluez package.

1.2.2
=====

* Removed dependence on enum and jaraco.util

1.2
===

* Added this documentation
* Updated the project website to use PYPI directly.
* Moved joystick functionality to its own project - `jaraco.input
  <http://pypi.python.org/pypi/jaraco.input>`_

1.1
===

* Updated dependency on jaraco.util, removing many secondary dependencies.

1.0
===

* Initial release
* Implements complete protocol
* Includes support for XBox 360 controller on Windows

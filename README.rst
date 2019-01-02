.. image:: https://img.shields.io/pypi/v/skeleton.svg
   :target: https://pypi.org/project/skeleton

.. image:: https://img.shields.io/pypi/pyversions/skeleton.svg

.. image:: https://img.shields.io/travis/jaraco/skeleton/master.svg
   :target: https://travis-ci.org/jaraco/skeleton

.. .. image:: https://img.shields.io/appveyor/ci/jaraco/skeleton/master.svg
..    :target: https://ci.appveyor.com/project/jaraco/skeleton/branch/master

.. .. image:: https://readthedocs.org/projects/skeleton/badge/?version=latest
..    :target: https://skeleton.readthedocs.io/en/latest/?badge=latest

.. -*- restructuredtext -*-

LEGO Mindstorms NXT Bluetooth API in Python

Overview
--------

``jaraco.nxt`` implements the LEGO Mindstorms NXT Bluetooth API in Python.

The ``jaraco.nxt`` library also can take advantage of the `jaraco input
<https://pypi.org/project/jaraco.input>`_
package.  To include it as part of the install, use the command
``pip install jaraco.nxt[input]``.

Getting Started
---------------

``jaraco.nxt`` provides a message class for sending and receiving messages
with the Lego NXT device.  First pair the device with your PC by following
the instructions included with the device.  Then, determine the COM port
to which it is connected.  The `hello world example
<https://github.com/jaraco/jaraco.nxt/tree/master/examples/get_battery_voltage.py>`_
is to retrieve the battery
voltage.  `Browse the other examples
<https://github.com/jaraco/jaraco.nxt/tree/master/examples/>`_ for
more inspiration.

For more information, read the docstrings of the modules in the packages.

Modules of interest are

* jaraco.nxt.messages: implements the messages defined by
  the NXT Bluetooth protocol.
* jaraco.nxt.controller: demonstrates how to link input from
  a joystick to messages controlling the motors.  Uses jaraco.input.

.. -*- restructuredtext -*-

``jaraco.nxt`` - LEGO Mindstorms NXT Bluetooth API in Python
============================================================

.. contents::

Overview
--------

``jaraco.nxt`` implements the LEGO Mindstorms NXT Bluetooth API in Python.

``jaraco.nxt`` is written by Jason R. Coombs.  It is licensed under an
MIT-style permissive license.

You can install it with ``easy_install jaraco.nxt``, or checkout the source
from the
`Github repository <https://github.com/jaraco/jaraco.nxt/>`_.

The ``jaraco.nxt`` library also can take advantage of the `jaraco input
<https://pypi.python.org/pypi/jaraco.input>`_
package.  To include it as part of the install, use the command
``easy_install jaraco.nxt[input]``.

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

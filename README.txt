.. -*- restructuredtext -*-

``jaraco.nxt`` - LEGO Mindstorms NXT Bluetooth API in Python
============================================================

.. contents::

Status and License
------------------

``jaraco.nxt`` implements the LEGO Mindstorms NXT Bluetooth API in Python.

``jaraco.nxt`` is written by Jason R. Coombs.  It is licensed under an
`MIT-style permissive license
<http://bitbucket.org/jaraco/jaraco.nxt/raw/tip/docs/license.txt>`_.

You can install it with ``easy_install jaraco.nxt``, or from the
`bitbucket repository
<http://bitbucket.org/jaraco/jaraco.nxt/get/tip.zip#egg=jaraco.nxt-dev>`_ with
``easy_install jaraco.nxt==dev``.

The ``jaraco.nxt`` library also can take advantage of the `jaraco input
<http://pypi.python.org/pypi/jaraco.input>`_
package.  To include it as part of the install, use the command
``easy_install jaraco.nxt[input]``.

Getting Started
---------------

``jaraco.nxt`` provides a message class for sending and receiving messages
with the Lego NXT device.  First pair the device with your PC by following
the instructions included with the device.  Then, determine the COM port
to which it is connected.  The hello world example is to retrieve the battery
voltage.  You can `download the source
<http://bitbucket.org/jaraco/jaraco.nxt/raw/tip/examples/get_battery_voltage.py>`_
for that example.  You may also `browse the other examples
<http://bitbucket.org/jaraco/jaraco.nxt/src/tip/examples/>`_.

For more information, read the docstrings of the modules in the packages.

Modules of interest are

* jaraco.nxt.messages: implements the messages defined by
  the NXT Bluetooth protocol.
* jaraco.nxt.controller: demonstrates how to link input from
  a joystick to messages controlling the motors.  Uses jaraco.input.

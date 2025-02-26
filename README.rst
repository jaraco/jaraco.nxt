.. image:: https://img.shields.io/pypi/v/jaraco.nxt.svg
   :target: https://pypi.org/project/jaraco.nxt

.. image:: https://img.shields.io/pypi/pyversions/jaraco.nxt.svg

.. image:: https://github.com/jaraco/jaraco.nxt/actions/workflows/main.yml/badge.svg
   :target: https://github.com/jaraco/jaraco.nxt/actions?query=workflow%3A%22tests%22
   :alt: tests

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff

.. .. image:: https://readthedocs.org/projects/PROJECT_RTD/badge/?version=latest
..    :target: https://PROJECT_RTD.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/badge/skeleton-2025-informational
   :target: https://blog.jaraco.com/skeleton

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
<https://github.com/jaraco/jaraco.nxt/tree/main/examples/get_battery_voltage.py>`_
is to retrieve the battery
voltage.  `Browse the other examples
<https://github.com/jaraco/jaraco.nxt/tree/main/examples/>`_ for
more inspiration.

For more information, read the docstrings of the modules in the packages.

Modules of interest are

* jaraco.nxt.messages: implements the messages defined by
  the NXT Bluetooth protocol.
* jaraco.nxt.controller: demonstrates how to link input from
  a joystick to messages controlling the motors.  Uses jaraco.input.

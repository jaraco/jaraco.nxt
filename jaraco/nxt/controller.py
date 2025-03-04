"""
functions to facilitate input
"""

import argparse
from collections import defaultdict

import jaraco.nxt

try:
    from jaraco.input import Joystick
except ImportError:
    from textwrap import dedent

    msg = dedent(
        """
        %s module requires jaraco.input.
        Unable to import jaraco.input.
        Consider installing with easy_install jaraco.input.
        """.strip()
        % __name__
    )
from jaraco.nxt import Connection
from jaraco.nxt.messages import OutputPort, RunState, SetOutputState


class MotorController:
    """
    Interfaces a jaraco.input Joystick with the NXT motors

    Maps the left thumb y axis to output port B
    Maps the right thumb y axis to output port C
    Maps the left and right triggers to output port A
    """

    motor_map = dict(
        l_thumb_y=OutputPort.b,
        r_thumb_y=OutputPort.c,
    )
    scale_exponent = 0.3
    scale_a = 1
    scale_b = 1
    scale_c = 1

    def __init__(self, options):
        self.conn = Connection(options.port)
        if options.scale_a:
            self.scale_a = options.scale_a
        if options.scale_b:
            self.scale_b = options.scale_b
        if options.scale_c:
            self.scale_c = options.scale_c
        try:
            self.input = Joystick.enumerate_devices()[0]
        except IndexError:
            raise RuntimeError("Could not find any joystick controllers.")
        # keep track of the state of the controller (initial state
        #  assumes all values are zero).
        self.controller_state = defaultdict(lambda: 0)

        # register the joystick on_axis event
        self.input.event(self.on_axis)

    def on_axis(self, axis, value):
        self.controller_state[axis] = value
        self.on_state_changed()

    def on_state_changed(self):
        st = self.controller_state

        # let the left trigger be reverse and the right trigger be forward,
        # use the difference to determine the motor power.
        a_reverse = st['left_trigger']
        a_forward = st['right_trigger']
        a_power = a_forward - a_reverse
        a_power *= self.scale_a

        # note a_power in [-1, 1]
        self.set_port(OutputPort.a, a_power)

        # multiply by 2 because it's a signed value [-0.5,0.5]
        b_power = st['l_thumb_y'] * 2
        b_power *= self.scale_b
        self.set_port(OutputPort.b, b_power)

        c_power = st['r_thumb_y'] * 2
        c_power *= self.scale_c
        self.set_port(OutputPort.c, c_power)

    def set_port(self, port, power):
        "Set the output port to the specified power"

        # first, scale the power using the provided exponent
        #  A scale_exponent < 1 makes the sensor less sensitive near
        #  the origin (0) and thus more sensitive toward the extremes
        scaled_power = abs(power) ** self.scale_exponent
        if power < 0:
            power = -scaled_power
        else:
            power = scaled_power

        # NXT expects a power between -100 and 100.
        power *= 100
        # with rounding errors, sometimes the power is greater than 100
        #  or less than -100.
        # TODO: should I just round here?
        #  i.e. power = int(round(power))
        power = max(min(power, 100), -100)
        # here, I'm disabling the motor if the output is less than 50, because
        #  those levels of power don't seem to be able to do much to actuate
        #  movement.
        # I note now that the regulation mode may be useful to actuate movement when
        #  the load is preventing movement at that power level.
        if abs(power) > 50:
            cmd = SetOutputState(
                port, motor_on=True, set_power=power, run_state=RunState.running
            )
        else:
            cmd = SetOutputState(port)
        self.conn.send(cmd)

    @staticmethod
    def add_arguments(parser):
        parser.add_argument('--scale_a', type=float)
        parser.add_argument('--scale_b', type=float)
        parser.add_argument('--scale_c', type=float)


def _get_options():
    """
    Get options for the NXT device as well as the MotorController.

    >>> import sys; getfixture('monkeypatch').setattr(sys, 'argv', sys.argv[:1])
    >>> options = _get_options()

    Note that the test above will fail with optparse.OptionConflictError
    if the options
    ever conflict between the NXT device and the MotorController.
    """
    parser = argparse.ArgumentParser()
    jaraco.nxt.add_arguments(parser)
    MotorController.add_arguments(parser)
    return parser.parse_args


def print_voltage(controller):
    from jaraco.nxt.routine import get_voltage

    voltage = get_voltage(controller.conn)
    print('Successfully connected to device; battery voltage is %f' % voltage)


def serve_forever():
    controller = MotorController(_get_options())
    print_voltage(controller)
    while True:
        try:
            controller.input.dispatch_events()
        except KeyboardInterrupt:
            break
    controller.conn.close()


if __name__ == '__main__':
    serve_forever()

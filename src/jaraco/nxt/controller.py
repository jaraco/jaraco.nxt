#!python

# $Id$

"""
jaraco.nxt.controller module

functions to facilitate input
"""

__author__='Jason R. Coombs <jaraco@jaraco.com>'
__svnauthor__='$Author$'[9:-2]

from jaraco.nxt.xinput import XInputJoystick
from jaraco.nxt.messages import SetOutputState, OutputPort, RunState

from pyglet import event

class MotorController(object):
	"""
	Interfaces an XInput controller with the NXT motors
	
	Maps the left thumb y axis to output port B
	Maps the right thumb y axis to output port C
	Maps the left and right triggers to output port A
	"""
	
	motor_map = dict(
		l_thumb_y = OutputPort.b,
		r_thumb_y = OutputPort.c,
		)
	scale_exponent = .3
		
	def __init__(self, conn):
		self.conn = conn
		self.input = XInputJoystick.enumerate_devices()[0]
		self.input.event(self.on_state_changed)

	def on_state_changed(self, state):
		# let the left trigger be reverse and the right trigger be forward,
		# use the difference to determine the motor power.
		a_reverse = self.input.translate(state.gamepad.left_trigger, 1)
		a_forward = self.input.translate(state.gamepad.right_trigger, 1)
		a_power = a_forward - a_reverse
		# note a_power in [-1, 1]
		self.set_port(OutputPort.a, a_power)
		
		b_power = self.input.translate(state.gamepad.r_thumb_y, 2)*2
		self.set_port(OutputPort.b, b_power)
		
		c_power = self.input.translate(state.gamepad.l_thumb_y, 2)*2
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
		if abs(power) > 50:
			cmd = SetOutputState(port, motor_on=True, set_power=power, run_state=RunState.running)
		else:
			cmd = SetOutputState(port)
		self.conn.send(cmd)

def _get_options():
	from optparse import OptionParser
	from jaraco.nxt import add_options
	parser = OptionParser()
	add_options(parser)
	options, args = parser.parse_args()
	return options

def serve_forever():
	from jaraco.nxt import Connection
	options = _get_options()
	controller = MotorController(Connection(options.port))
	while True:
		try:
			controller.input.dispatch_events()
		except KeyboardInterrupt:
			break
	controller.conn.close()

if __name__ == '__main__':
	serve_forever()
	
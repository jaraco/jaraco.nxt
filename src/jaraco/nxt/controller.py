#!python

# $Id$

"""
jaraco.nxt.controller module

functions to facilitate input
"""

__author__='Jason R. Coombs <jaraco@jaraco.com>'
__svnauthor__='$Author$'[9:-2]

import jaraco.nxt
from jaraco.nxt.xinput import XInputJoystick
from jaraco.nxt import Connection
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
			self.input = XInputJoystick.enumerate_devices()[0]
		except IndexError:
			raise RuntimeError, "Could not find any connected controllers"
		self.input.event(self.on_state_changed)

	def on_state_changed(self, state):
		# let the left trigger be reverse and the right trigger be forward,
		# use the difference to determine the motor power.
		a_reverse = self.input.translate(state.gamepad.left_trigger, 1)
		a_forward = self.input.translate(state.gamepad.right_trigger, 1)
		a_power = a_forward - a_reverse
		a_power *= self.scale_a
		
		# note a_power in [-1, 1]
		self.set_port(OutputPort.a, a_power)
		
		b_power = self.input.translate(state.gamepad.l_thumb_y, 2)*2
		b_power *= self.scale_b
		self.set_port(OutputPort.b, b_power)
		
		c_power = self.input.translate(state.gamepad.r_thumb_y, 2)*2
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
		if abs(power) > 50:
			cmd = SetOutputState(port, motor_on=True, set_power=power, run_state=RunState.running)
		else:
			cmd = SetOutputState(port)
		self.conn.send(cmd)

	@staticmethod
	def add_options(parser):
		parser.add_option('--scale_a', type="float")
		parser.add_option('--scale_b', type="float")
		parser.add_option('--scale_c', type="float")

def _get_options():
	"""
	Get options for the NXT device as well as the MotorController.

	>>> options = _get_options()
	
	Note that the test above will fail with optparse.OptionConflictError if the options
	ever conflict between the NXT device and the MotorController.
	"""
	from optparse import OptionParser
	parser = OptionParser()
	jaraco.nxt.add_options(parser)
	MotorController.add_options(parser)
	options, args = parser.parse_args()
	return options

def print_voltage(controller):
	from routine import get_voltage
	voltage = get_voltage(controller.conn)
	print 'Successfully connected to device; battery voltage is %f' % voltage

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
	
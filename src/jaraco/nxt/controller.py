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
	"Interfaces an XInput controller with the NXT motors"
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
		a_reverse = self.input.translate(state.gamepad.left_trigger, 1)
		a_forward = self.input.translate(state.gamepad.right_trigger, 1)
		a_power = a_forward - a_reverse
		self.set_port(OutputPort.a, a_power)
		
		b_power = self.input.translate(state.gamepad.r_thumb_y, 2)*2
		self.set_port(OutputPort.b, b_power)
		
		c_power = self.input.translate(state.gamepad.l_thumb_y, 2)*2
		self.set_port(OutputPort.c, c_power)

	def set_port(self, port, power):
		scaled_power = abs(power) ** self.scale_exponent
		if power < 0:
			power = -scaled_power
		else:
			power = scaled_power
		power *= 100
		power = max(min(power, 100), -100)
		if abs(power) > 50:
			cmd = SetOutputState(port, motor_on=True, set_power=power, run_state=RunState.running)
		else:
			cmd = SetOutputState(port)
		self.conn.send(cmd)


if __name__ == '__main__':
	from jaraco.nxt import Connection
	
	controller = MotorController(Connection('COM4'))
	while True:
		try:
			controller.input.dispatch_events()
		except KeyboardInterrupt:
			break

	controller.conn.close()
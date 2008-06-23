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
	motor_map = dict(
		l_thumb_y = OutputPort.b,
		r_thumb_y = OutputPort.c,
		)
		
	def __init__(self, conn):
		self.conn = conn
		self.input = XInputJoystick.enumerate_devices()[0]
		self.input.event(self.on_state_changed)

	def on_state_changed(self, state):
		a_reverse = self.input.translate(state.gamepad.left_trigger, 1)
		a_forward = self.input.translate(state.gamepad.right_trigger, 1)
		a_power = (a_forward - a_reverse) * 100
		if abs(a_power) > 50:
			cmd = SetOutputState(OutputPort.a, motor_on=True, set_power=a_power, run_state=RunState.running)
		else:
			cmd = SetOutputState(OutputPort.a)
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
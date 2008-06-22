#!/usr/bin/env python

import ctypes

class XINPUT_GAMEPAD(ctypes.Structure):
	_fields_ = [
		('wButtons', ctypes.c_ushort),
		('bLeftTrigger', ctypes.c_ubyte),
		('bRightTrigger', ctypes.c_ubyte),
		('sThumbLX', ctypes.c_short),
		('sThumbLY', ctypes.c_short),
		('sThumbRX', ctypes.c_short),
		('sThumbRY', ctypes.c_short),
	]

class XINPUT_STATE(ctypes.Structure):
	_fields_ = [
		('dwPacketNumber', ctypes.c_ulong),
		('Gamepad', XINPUT_GAMEPAD),
	]

lib = ctypes.windll.xinput1_2

state = XINPUT_STATE()

def struct_dict(struct):
	get_pair = lambda (field, type): (field, getattr(struct, field))
	return dict(map(get_pair, struct._fields_))
		
res = lib.XInputGetState(0, ctypes.byref(state))

ERROR_DEVICE_NOT_CONNECTED = 1167
ERROR_SUCCESS = 0

from pyglet import event

class XInputJoystick(event.EventDispatcher):
	def __init__(self, device_number):
		self.device_number = device_number
		super(XInputJoystick, self).__init__()
		self._last_state = XINPUT_STATE()

	def dispatch_events(self):
		state = XINPUT_STATE()
		res = lib.XInputGetState(self.device_number, ctypes.byref(state))
		if res != ERROR_SUCCESS:
			return # or should i raise an exception?
		if state.dwPacketNumber != self._last_state.dwPacketNumber:
			# state has changed, handle the change
			self.handle_changed_state(state)
		self._last_state = state

	def handle_changed_state(self, state):
		self.dispatch_event('on_state_changed', state)
		#self.dispatch_event('on_axis', number, value)

	def on_state_changed(self, state):
		pass
	
	def on_axis(self, axis, value):
		pass

	def on_button(self, button, pressed):
		pass

XInputJoystick.register_event_type('on_axis')
XInputJoystick.register_event_type('on_button')
XInputJoystick.register_event_type('on_state_changed')

if __name__ == "__main__":
	j = XInputJoystick(0)
	@j.event
	def on_button(button, pressed):
		print 'button', button, pressed

	@j.event
	def on_axis(axis, value):
		print 'axis', axis, value

	@j.event
	def on_state_changed(state):
		print 'state has changed', state.dwPacketNumber
		print struct_dict(state.Gamepad)

	import time
	while True:
		j.dispatch_events()
		time.sleep(.01)
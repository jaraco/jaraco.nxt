#!/usr/bin/env python

import ctypes
import sys
from operator import itemgetter, attrgetter

class XINPUT_GAMEPAD(ctypes.Structure):
	_fields_ = [
		('buttons', ctypes.c_ushort), # wButtons
		('left_trigger', ctypes.c_ubyte), # bLeftTrigger
		('right_trigger', ctypes.c_ubyte), # bLeftTrigger
		('l_thumb_x', ctypes.c_short), # sThumbLX
		('l_thumb_y', ctypes.c_short), # sThumbLY
		('r_thumb_x', ctypes.c_short), # sThumbRx
		('r_thumb_y', ctypes.c_short), # sThumbRy
	]

class XINPUT_STATE(ctypes.Structure):
	_fields_ = [
		('packet_number', ctypes.c_ulong), # dwPacketNumber
		('gamepad', XINPUT_GAMEPAD), # Gamepad
	]

# todo: is this the right DLL?  Should I also try others?
lib = ctypes.windll.xinput9_1_0
# others I've encountered:
# xinput1_2, xinput1_1 (32-bit Vista SP1)
# xinput1_3 (64-bit Vista SP1)

def struct_dict(struct):
	"""
	take a ctypes.Structure and return its field/value pairs
	as a dict.
	"""
	get_pair = lambda (field, type): (field, getattr(struct, field))
	return dict(map(get_pair, struct._fields_))
		
ERROR_DEVICE_NOT_CONNECTED = 1167
ERROR_SUCCESS = 0

from pyglet import event

class XInputJoystick(event.EventDispatcher):
	max_devices = 4
	
	def __init__(self, device_number):
		self.device_number = device_number
		super(XInputJoystick, self).__init__()
		self._last_state = self.get_state()
		self.received_packets = 0
		self.missed_packets = 0

	def get_state(self):
		state = XINPUT_STATE()
		res = lib.XInputGetState(self.device_number, ctypes.byref(state))
		if res == ERROR_SUCCESS:
			return state
		if res != ERROR_DEVICE_NOT_CONNECTED:
			raise RuntimeError, "Unknown error %d attempting to get state of device %d" % (res, self.device_number)
		# else return None

	def is_connected(self):
		return bool(self._last_state)

	@staticmethod
	def enumerate_devices():
		"Returns the devices that are connected"
		devices = map(XInputJoystick, range(XInputJoystick.max_devices))
		return filter(lambda d: d.is_connected(), devices)

	def dispatch_events(self):
		state = self.get_state()
		if not state:
			raise RuntimeError, "Joystick %d is not connected" % self.device_number
		if state.packet_number != self._last_state.packet_number:
			self.update_packet_count(state)
			# state has changed, handle the change
			self.handle_changed_state(state)
		self._last_state = state

	def update_packet_count(self, state):
		self.received_packets += 1
		missed_packets = state.packet_number - self._last_state.packet_number - 1
		self.dispatch_event('on_missed_packet', missed_packets)
		self.missed_packets += missed_packets

	def handle_changed_state(self, state):
		self.dispatch_event('on_state_changed', state)
		self.dispatch_axis_events(state)
		self.dispatch_button_events(state)
		
	def dispatch_axis_events(self, state):
		axis_fields = map(itemgetter(0), XINPUT_GAMEPAD._fields_)
		axis_fields.remove('buttons')
		for axis in axis_fields:
			old_val = getattr(self._last_state.gamepad, axis)
			new_val = getattr(state.gamepad, axis)
			# todo: implement some tolerance and deadzones to dampen noise
			if old_val != new_val:
				self.dispatch_event('on_axis', axis, new_val)

	def dispatch_button_events(self, state):
		# todo: implement this
		pass
		
	def on_state_changed(self, state):
		pass
	
	def on_axis(self, axis, value):
		pass

	def on_button(self, button, pressed):
		pass

	def on_missed_packet(self, number):
		pass

map(XInputJoystick.register_event_type, [
	'on_state_changed',
	'on_axis',
	'on_button',
	'on_missed_packet',
])

if __name__ == "__main__":
	joysticks = XInputJoystick.enumerate_devices()
	device_numbers = map(attrgetter('device_number'), joysticks)
	
	print 'found %d devices %s' % (len(joysticks), device_numbers)
	
	if not joysticks:
		sys.exit(0)
	
	j = joysticks[0]
		
	@j.event
	def on_button(button, pressed):
		print 'button', button, pressed

	@j.event
	def on_axis(axis, value):
		print 'axis', axis, value

	#@j.event
	#def on_state_changed(state):
	#	print 'state has changed', state.packet_number
	#	print struct_dict(state.gamepad)

	import time
	while True:
		j.dispatch_events()
		time.sleep(.01)
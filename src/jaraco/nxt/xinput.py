#!/usr/bin/env python

import ctypes
import sys
import time
from operator import itemgetter, attrgetter
from itertools import count, starmap

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

def get_bit_values(number, size=32):
	res = list(gen_bit_values(number))
	res.reverse()
	# 0-pad the most significant bit
	res = [0]*(size-len(res)) + res
	return res

def gen_bit_values(number):
	"""
	Return a zero or one for each bit of a numeric value up to the most
	significant 1 bit, beginning with the least significant bit.
	"""
	number = long(number)
	while number:
		yield number & 0x1
		number >>= 1

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
		if missed_packets:
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
		changed = state.gamepad.buttons ^ self._last_state.gamepad.buttons
		changed = get_bit_values(changed, 16)
		buttons_state = get_bit_values(state.gamepad.buttons, 16)
		changed.reverse()
		buttons_state.reverse()
		button_numbers = count(1)
		changed_buttons = filter(itemgetter(0), zip(changed, button_numbers, buttons_state))
		tuple(starmap(self.dispatch_button_event, changed_buttons))

	def dispatch_button_event(self, changed, number, pressed):
		self.dispatch_event('on_button', number, pressed)
		
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

def determine_optimal_sample_rate(joystick=None):
	# in my experience, you want to probe at 200-2000Hz for optimal
	#  performance
	if joystick is None: joystick = XInputJoystick.enumerate_devices()[0]
	
	j = joystick
	
	print "Move the joystick or generate button events characteristic of your app"
	print "Hit Ctrl-C or press button 6 (<, Back) to quit."
	
	# begin at 1Hz and work up until missed messages are eliminated
	j.probe_frequency = 1 #Hz
	j.quit = False
	j.target_reliability = .99 # okay to lose 1 in 100 messages
	
	@j.event
	def on_button(button, pressed):
		j.quit = (button == 6 and pressed)

	@j.event
	def on_missed_packet(number):
		print 'missed %(number)d packets' % vars()
		total = j.received_packets + j.missed_packets
		reliability = j.received_packets / float(total)
		if reliability < j.target_reliability:
			j.missed_packets = j.received_packets = 0
			j.probe_frequency *= 1.5
	
	while not j.quit:
		j.dispatch_events()
		time.sleep(1.0/j.probe_frequency)
	print "final probe frequency was %s Hz" % j.probe_frequency

def sample_first_joystick():
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

	#@j.event
	#def on_missed_packet(number):
	#	print 'missed %(number)d packets' % vars()

	while True:
		j.dispatch_events()
		time.sleep(.01)

if __name__ == "__main__":
	sample_first_joystick()
	#determine_optimal_sample_rate()

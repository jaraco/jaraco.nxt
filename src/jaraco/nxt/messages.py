#!python

# $Id$

"""
jaraco.nxt.messages
"""

__author__='Jason R. Coombs <jaraco@jaraco.com>'
__svnauthor__='$Author$'[9:-2]

import struct
import re
import operator
from enum import Enum

CommandTypes = Enum('direct', 'system')

class Message(object):
	"A raw message to or from the NXT"
	
	_expects_reply = False
	
	def __init__(self, payload):
		self.payload = payload
		self.parse_payload()

	def parse_payload(self):
		if hasattr(self, 'fields') and hasattr(self, 'structure'):
			values = struct.unpack(self.structure, self.payload)
			map(lambda f,v: setattr(self, f, v), self.fields, self.values)

	def __str__(self):
		assert len(self) <= 64
		return struct.pack('H', len(self)) + self.payload

	def __len__(self):
		return len(self.payload)

	@property
	def expects_reply(self):
		return [0x80, 0][self._expects_reply]

	@classmethod
	def read(cls, stream):
		len, ver = struct.unpack('2B', stream.read(2))
		assert ver == cls._version
		assert len > 0
		return cls(stream.read(len))

class Command(Message):
	_expects_reply = False
	_command_type = CommandTypes.direct
	
	def __init__(self, **kwargs):
		self.set(kwargs)
		
	def set(self, dict):
		for attr, value in dict.items():
			setattr(self, attr, value)

	@property
	def command_type(self):
		return self.expects_reply | self._command_type

	@property
	def payload(self):
		header = struct.pack('2B', self.expects_reply, self.command)
		message = header + self.get_telegram()

	def get_telegram(self):
		return ''

class StartProgram(Command):
	command = 0x00
	
	@staticmethod
	def validate_filename(filename):
		filename_pattern = re.compile('\w{1,15}(\.\w{0,3})?')
		assert filename_pattern.match(filename), 'invalid filename %s' % filename
		
	def __init__(self, filename, **kwargs):
		self.validate_filename(filename)
		kwargs['filename'] = filename
		super(StartProgram, self).__init__(**kwargs)
		
	def get_telegram(self):
		return self.filename + '\x00'

class SpecEnum(object):

	@classmethod
	def dictionary(cls):
		from jaraco.util.dictlib import DictFilter
		return dict(DictFilter(cls.__dict__, include_pattern='[^_].*'))

	@classmethod
	def keys(cls):
		return cls.dictionary().keys()
		
	@classmethod
	def values(cls):
		return cls.dictionary().values()

class OutputPort(SpecEnum):
	a = 0
	b = 1
	c = 2
	all = 0xff

class OutputMode(SpecEnum):
	motor_on = 1
	brake = 2
	regulated = 4

# RegulationMode = Enum('idle', 'motor_speed', 'motor_sync')
class RegulationMode(SpecEnum):
	idle = 0
	motor_speed = 1
	motor_sync = 2

class RunState(SpecEnum):
	idle = 0x00
	rampup = 0x10
	running = 0x20
	rampdown = 0x40

class SetOutputState(Command):
	"""
	>>> msg = SetOutputState(OutputPort.a)
	"""
	command = 0x04
	
	def __init__(
		self,
		port,
		set_power=0,
		motor_on=False,
		use_brake=False,
		use_regulation=False,
		regulation_mode=RegulationMode.idle,
		turn_ratio=0,
		run_state=RunState.idle,
		tacho_limit=0, # run forever
	):
		assert port in OutputPort.values(), "Invalid output port %d" % port
		assert -100 <= set_power <= 100, "Invalid power set point %s" % set_power
		assert isinstance(motor_on, bool)
		assert isinstance(use_brake, bool)
		assert isinstance(use_regulation, bool)
		assert regulation_mode in RegulationMode.values(), "Invalid regulation mode %s" % regulation_mode
		assert -100 <= turn_ratio <= 100
		assert run_state in RunState.values(), "Invalid run state %s" % run_state
		assert tacho_limit >= 0, "Invalid Tachometer Limit %s" % tacho_limit
		
		values = vars()
		values.pop('self')
		
		self.set(values)

	@property
	def mode_byte(self):
		mode_byte = reduce(operator.or_, (
			# todo, this is probably incorrect
			self.motor_on & OutputMode.motor_on,
			self.use_brake & OutputMode.brake,
			self.use_regulation & OutputMode.regulated,
			))
		return mode_byte
		
	def get_telegram(self):
		return struct.pack('BbBBbBL',
			self.port,
			self.set_power,
			self.mode_byte,
			self.regulation_mode,
			self.turn_ratio,
			self.run_state,
			self.tacho_limit,
			)

class SensorType(SpecEnum):
	no_sensor = 0
	switch = 1
	temperature = 2
	reflection = 3
	angle = 4
	light_active = 5
	light_inactive = 6
	sound_db = 7
	sound_dba = 8
	custom = 9
	lowspeed = 0xa
	lowspeed_9v = 0xb
	no_of_sensor_types = 0xc

class SensorMode(SpecEnum):
	raw = 0
	boolean = 0x20
	transition_count = 0x40
	period_counter = 0x60
	pct_full_scale = 0x80
	celcius = 0xA0
	fahrenheit = 0xC0
	angle_steps = 0xE0
	slope_mask = 0x1F
	mode_mask = 0xE0
	
class SetInputMode(Command):
	command = 0x5
	
	def __init__(self, port, type, mode):
		assert port in range(4)
		assert type in SensorType.values()
		assert mode in SensorMode.values()

		values = vars()
		values.pop('self')
		
		self.set(values)

	def get_telegram(self):
		return struct.pack('BBB', self.port, self.type, self.mode)

class OutputState(Message):
	fields = (
		'status', 'port', 'power_set', 'mode', 'regulation_mode',
		'turn_ratio', 'run_state', 'tacho_limit', 'tacho_count',
		'block_tacho_count', 'rotation_count',
		)
	structure = 'BBbBBbBLlll'

	@property
	def motor_on(self):
		return bool(self.mode & OutputMode.motor_on)

	@property
	def use_brake(self):
		return bool(self.mode & OutputMode.use_break)

	@property
	def use_regulation(self):
		return bool(self.mode & OutputMode.regulated)

class GetOutputState(Command):
	command = 0x6
	_expects_reply = OutputState
	
	def __init__(self, port):
		assert port in OutputPort.values()
		self.port = port
		
	def get_telegram(self):
		return struct.pack('B', self.port)

class InputValues(Message):
	fields = (
		'status', 'port', 'valid', 'calibrated',
		'type', 'mode', 'value', 'normalized_value',
		'scaled_value', 'calibrated_value',
		)
	structure = 'BBBBBBHHhh'

class GetInputValues(Command):
	command = 0x7
	_expects_reply = InputValues
	
	def __init__(self, port):
		assert port in InputPorts.values()
		self.port = port

	def get_telegram(self):
		return struct.pack('B', self.port)

class GetVersion(Command):
	_expects_reply = True
	command = 0x88

class GetInfo(Command):
	_expects_reply = True
	command = 0x9B
	
class QueryBattery(Command):
	_expects_reply = True
	command = 0xB

class BatteryResponse(Message):
	def get_voltage(self):
		millivolts = struct.unpack('H', self.payload[3:5])[0]
		return millivolts/1000.0

class PlayTone(Command):
	command = 0x3
	
	def __init__(self, frequency, duration = 100):
		assert 200 <= frequency <= 3000
		self.frequency = frequency
		self.duration = duration

	def get_telegram(self):
		return struct.pack('2H', self.frequency, self.duration)

class CurrentProgramName(Message):
	def parse_values(self):
		self.status = self.payload[0]
		self.filename = self.payload[1:]

class GetCurrentProgramName(Command):
	command = 0x11
	_expects_reply = CurrentProgramName
	
class SleepTimeout(Message):
	"value is the timeout in milliseconds"
	fields = 'status', 'value'
	structure = 'BL'

class KeepAlive(Command):
	command = 0xD
	_expects_reply = SleepTimeout

class MessageWrite(Command):
	command = 0x9
	
	def __init__(self, message, box_number=1):
		assert 0 < box_number <= 10, 'invalid box number %s' % box_number
		self.box = box_number-1
		self.message = message

	def get_telegram(self):
		message = message + '\x00'
		return struct.pack('BB', self.box, len(message)) + message

class ReadMailboxMessage(Command):
	_expects_reply = True
	command = 0x13
	
	def __init__(self, box_number=1):
		box_index = box_number - 1
		self.box_indicator = box_index + 10
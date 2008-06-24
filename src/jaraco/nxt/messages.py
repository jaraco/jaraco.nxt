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
from jaraco.nxt._enum import *

class Message(object):
	"A raw message to or from the NXT"
	
	_expects_reply = False
	fields = ()
	structure = ''
	
	def __init__(self, payload):
		self.payload = payload
		self.parse_payload()

	def parse_payload(self):
		values = struct.unpack(self.structure, self.payload)
		map(lambda f,v: setattr(self, f, v), self.fields, values)

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
	
	def __init__(self, *args):
		assert len(args) == len(self.fields)
		self.set(dict(zip(self.fields, args)))
		
	def set(self, dict):
		for attr, value in dict.items():
			setattr(self, attr, value)
		self.validate_settings()

	def validate_settings(self):
		return

	@property
	def command_type(self):
		return self.expects_reply | self._command_type

	@property
	def payload(self):
		header = struct.pack('2B', self.expects_reply, self.command)
		message = header + self.get_telegram()
		return message

	def get_telegram(self):
		self.validate_settings()
		values = map(lambda f: getattr(self, f), self.fields)
		return struct.pack(self.structure, *values)

class StartProgram(Command):
	command = 0x00
	
	fields = ('filename',)

	@staticmethod
	def validate_filename(filename):
		filename_pattern = re.compile('\w{1,15}(\.\w{0,3})?')
		assert filename_pattern.match(filename), 'invalid filename %s' % filename
		
	def validate_settings(self):
		self.validate_filename(self.filename)
		
	def get_telegram(self):
		return self.filename + '\x00'

class SetOutputState(Command):
	"""
	>>> msg = SetOutputState(OutputPort.a)
	"""
	command = 0x04
	fields = (
		'port', 'set_power', 'mode_byte', 'regulation_mode',
		'turn_ratio', 'run_state', 'tacho_limit',
		)
	structure = 'BbBBbBL'
	
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

class SetInputMode(Command):
	command = 0x5
	fields = 'port', 'type', 'mode'
	structure = 'BBB'
	
	def validate_settings(self):
		assert self.port in range(4)
		assert self.type in SensorType.values()
		assert self.mode in SensorMode.values()

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
	fields = ('port',)
	structure = 'B'

	def validate_settings(self):
		assert self.port in OutputPort.values()

class InputValues(Message):
	fields = (
		'status', 'port', 'valid', 'calibrated',
		'type', 'mode', 'value', 'normalized_value',
		'scaled_value', 'calibrated_value',
		)
	structure = 'BBBBBBHHhh'

class ResetInputScaledValue(Command):
	command = 0x8
	fields = ('port',)
	structure = 'B'
	
	def validate_settings(self):
		assert self.port in InputPort.values()

class GetInputValues(Command):
	command = 0x7
	_expects_reply = InputValues
	fields = ('port',)
	structure = 'B'
	
	def validate_settings(self):
		assert self.port in InputPort.values()

class GetVersion(Command):
	_expects_reply = True
	command = 0x88

class GetInfo(Command):
	_expects_reply = True
	command = 0x9B
	
class BatteryResponse(Message):
	fields = 'status', 'millivolts'
	structure = 'BH'
	
	def get_voltage(self):
		return self.millivolts/1000.0

class GetBatteryLevel(Command):
	_expects_reply = BatteryResponse
	# _B_attery command is B... coincidence?
	command = 0xb

class PlayTone(Command):
	command = 0x3
	fields = 'frequency', 'duration'
	structure = '2H'
	
	def validate_settings(self):
		assert 200 <= self.frequency <= 3000

	def __init__(self, frequency, duration = 100):
		values = vars()
		values.pop('self')
		self.set(values)

class CurrentProgramName(Message):
	fields = 'status', 'filename'
	
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
	fields = 'box', 'message_len', 'Zmessage'

	def __init__(self, message, box_number=1):
		values = vars()
		values.pop('self')
		self.set(values)

	@property
	def structure(self):
		return 'BB%ds' % self.message_len

	@property
	def Zmessage(self):
		return ''.join(self.message, '\x00')

	@property
	def message_len(self):
		return len(self.message)
		
	def validate_settings(self):
		assert 0 <= self.box < 10, 'invalid box number %(box_number)s' % self.__dict__
		assert self.message_len <= 0xFF

	@property
	def box(self):
		return self.box_number-1
	
class ResetMotorPosition(Command):
	command = 0xa
	fields = 'port', 'relative'
	structure = 'BB'
	
	def validate_settings(self):
		assert self.port in OutputPort.values()

	def __init__(self, port, relative=True):
		self.set(port=port, relative=relative)

class StopSoundPlayback(Command):
	command = 0xc

class LSStatus(Message):
	fields = ('status', 'num_bytes')
	structure = 'BB'

class LSGetStatus(Command):
	command = 0xe
	_expects_reply = LSStatus
	fields = ('port',)
	structure = 'B'
	
	def validate_settings(self):
		assert self.port in InputPort.values()

class LSWrite(Command):
	command = 0xf
	fields = 'port', 'data_length', 'response_length', 'data'
	
	@property
	def structure(self):
		return 'BBB%ds' % self.data_length

	data_length = property(lambda self: len(self.data))
	
	def validate_settings(self):
		assert self.data_length <= 16
		assert self.response_length <= 16
		assert self.port in OutputPort.values()
	
	def __init__(self, port, data, response_length = 0):
		values = vars()
		values.pop('self')
		self.set(values)

class StatusResponse(Message):
	fields = ('status',)
	structure = 'B'

class LSReadResponse(Message):
	fields = ('status', 'data')
	structure = 'B17p'

class LSRead(Command):
	command = 0x10
	_expects_reply = LSReadResponse
	fields = ('port',)
	structure = 'B'
	
	def validate_settings(self):
		assert self.port in InputPort.values()

class MessageReadResponse(Message):
	fields = 'status', 'box', 'message'
	structure = 'BB60p'
	
class MessageRead(Command):
	_expects_reply = MessageReadResponse
	command = 0x13
	fields = 'remote_box', 'local_box', 'remove'
	structure = 'BBB'

	def validate_settings(self):
		assert 0 <= self.box < 10, 'invalid box number %(box_number)s' % self.__dict__
		assert self.message_len <= 0xFF

	remote_box = property(lambda self: self.local_box + 0xa)
	local_box = property(lambda self: self.box_number - 1)

	def __init__(self, box_number=1, remove=True):
		self.set(box_number=box_number, remove=remove)

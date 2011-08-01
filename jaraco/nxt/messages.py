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
import logging
from _enum import *

log = logging.getLogger(__name__)

class MetaMessage(type):
	"""
	A metaclass for message that collects meta information about each
	of the Message classes.
	"""

	"A map of message classes by byte code"
	_messages = {}

	def __init__(cls, name, bases, attrs):
		"Store the command classes here for reference"
		if 'command' in attrs:
			code = attrs['command']
			cls._messages[code] = cls

class Message(object):
	"""
	A raw message to or from the NXT

	Attributes
	fields: a collection of string names of the fields contained in this
	  message.
	structure: A Python struct format string describing the structure of
	  the payload of this message (not including the header bytes).
	expected_reply: The class of the expected reply message or None if
	  no reply is to be solicited. (Can this be relegated to Command?)
	"""

	__metaclass__ = MetaMessage

	expected_reply = None
	fields = ()
	structure = ''

	def __init__(self, payload):
		"""
		Normally, instantiate a subclass of Command, but it is
		possible to create a base Message
		>>> m = Message('\x03\x04')
		"""
		self.payload = payload
		self.parse_payload()

	def parse_payload(self):
		try:
			values = struct.unpack('<'+self.structure, self.payload[2:])
			map(lambda f,v: setattr(self, f, v), self.fields, values)
		except struct.error:
			log.warning("Payload does not match structure")
			log.debug("Payload is %r", self.payload)
			log.debug("Structure is %r", self.structure)

	def __str__(self):
		assert len(self) <= 64
		return struct.pack('<H', len(self)) + self.payload

	def __len__(self):
		return len(self.payload)

	@property
	def _expect_reply_value(self):
		"""
		determine the code to transmit for
		the reply bit
		>>> bat_msg = GetBatteryLevel()
		>>> bat_msg.expected_reply is not None
		True
		>>> bat_msg._expect_reply_value
		0
		"""
		suppress_reply = 0x80
		expect_reply = 0x00
		selector = int(bool(self.expected_reply))
		return [suppress_reply, expect_reply][selector]

	@staticmethod
	def read(stream):
		"Read a message out of the data stream"

		# The first two characters in the stream indicate the length
		#  of the message
		len = struct.unpack('<H', stream.read(2))[0]

		# The header of every message must contain two bytes
		assert len >= 2

		# read the rest of the message (can't be more than 64k)
		payload = stream.read(len)

		# read the command type and command byte
		command_type, command = struct.unpack('<BB', payload[:2])

		# ascertain the reply class based on the header
		cls = Message.determine_reply_class(command_type, command)

		# create a new message of the appropriate type from the data
		return cls(payload)

	@staticmethod
	def determine_reply_class(command_type, command):
		try:
			cls = Message._messages[command]
			is_reply = command_type == CommandTypes.reply
			if is_reply:
				if issubclass(cls.expected_reply, Message):
					cls = cls.expected_reply
		except KeyError, e:
			log.error("Unrecognized command 0x%02x encountered; using generic message class", command)
			cls = Message
		return cls


class Command(Message):
	"""
	Base class for commands to be sent to a NXT device

	Attributes:
	expected_reply: set to None to indicate no reply is expected.  Otherwise, set to
	                the class of the expected reply message (i.e. a Reply).
	command: A numeric value between 0 and 255 representing the comma
	"""

	expected_reply = None
	# so far, the only command type implemented is 'direct'
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
		return self._expect_reply_value | self._command_type

	@property
	def payload(self):
		"""
		Assemble the payload (the portion of the message following the two-byte size).
		The first two bytes are the command_type and command.
		The remaining bytes, if any, are called the telegram.
		"""
		header = struct.pack('<2B', self.command_type, self.command)
		message = header + self.get_telegram()
		return message

	def get_telegram(self):
		"""
		The telegram is the possibly empty remainder of the message
		following the header (command type and command).
		"""
		# by default, validate the settings, then pack the fields according to the structure.
		self.validate_settings()
		values = map(lambda f: getattr(self, f), self.fields)
		return struct.pack('<'+self.structure, *values)

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

	Separate boolean parameters are supplied to create the mode_byte
	>>> msg = SetOutputState(OutputPort.a, motor_on=True, use_regulation=True)
	>>> msg.mode_byte
	5

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
		assert not (turn_ratio and regulation_mode != RegulationMode.motor_sync), "Turn ratio is only valid when regulation_mode is motor_sync"
		assert not (turn_ratio and port == OutputPort.all), "Turn ratio is not valid for 'all' output ports"
		assert run_state in RunState.values(), "Invalid run state %s" % run_state
		assert tacho_limit >= 0, "Invalid Tachometer Limit %s" % tacho_limit

		values = vars()
		values.pop('self')

		self.set(values)

	@property
	def mode_byte(self):
		"Assemble the 'mode' byte from instance attributes"
		# assemble a tuple of bits that are set only
		#  if the corresponding flag is set.
		# For example, if self.motor_on is True, the first
		#  bit is set to OutputMode.motor_on. Otherwise,
		#  the first bit is set to False (0).
		mode_bits = (
			self.motor_on and OutputMode.motor_on,
			self.use_brake and OutputMode.brake,
			self.use_regulation and OutputMode.regulated,
		)
		mode_byte = reduce(operator.or_, mode_bits)
		return mode_byte

class Reply(Message):
	"A simple status response"
	fields = ('status',)
	structure = 'B'

class PlaySoundFile(Command):
	command = 0x2
	fields = 'loop', 'filename'
	structure = 'B19p'

	def validate_settings(self):
		assert type(loop) is bool

class SetInputMode(Command):
	command = 0x5
	fields = 'port', 'type', 'mode'
	structure = 'BBB'

	def validate_settings(self):
		assert self.port in range(4)
		assert self.type in SensorType.values()
		assert self.mode in SensorMode.values()

class OutputState(Reply):
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
	expected_reply = OutputState
	fields = ('port',)
	structure = 'B'

	def validate_settings(self):
		assert self.port in OutputPort.values()

class InputValues(Reply):
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
	expected_reply = InputValues
	fields = ('port',)
	structure = 'B'

	def validate_settings(self):
		assert self.port in InputPort.values()

class GetVersion(Command):
	expected_reply = Message
	command = 0x88

class GetInfo(Command):
	expected_reply = Message
	command = 0x9B

class BatteryResponse(Reply):
	fields = 'status', 'millivolts'
	structure = 'BH'

	def get_voltage(self):
		return self.millivolts/1000.0

class GetBatteryLevel(Command):
	expected_reply = BatteryResponse
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

class CurrentProgramName(Reply):
	fields = 'status', 'filename'

	def parse_values(self):
		"Override because standard structure is inadequate"
		self.status = self.payload[0]
		self.filename = self.payload[1:]

class GetCurrentProgramName(Command):
	command = 0x11
	expected_reply = CurrentProgramName

class SleepTimeout(Reply):
	"value is the timeout in milliseconds"
	fields = 'status', 'value'
	structure = 'BL'

class KeepAlive(Command):
	command = 0xD
	expected_reply = SleepTimeout

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
		return ''.join([self.message, '\x00'])

	@property
	def message_len(self):
		"message size must include null byte"
		return len(self.Zmessage)

	def validate_settings(self):
		assert 0 <= self.box < 10, 'invalid box number %(box_number)s' % self.__dict__
		assert self.message_len <= 0xFF

	@property
	def box(self):
		return self.box_number-1

class ResetMotorPosition(Command):
	"""
	>>> msg = ResetMotorPosition(OutputPort.b)
	>>> msg = ResetMotorPosition(OutputPort.c, relative=False)
	"""
	command = 0xa
	fields = 'port', 'relative'
	structure = 'BB'

	def validate_settings(self):
		assert self.port in OutputPort.values()

	def __init__(self, port, relative=True):
		values = vars()
		values.pop('self')
		self.set(values)

class StopSoundPlayback(Command):
	command = 0xc

class LSStatus(Reply):
	fields = ('status', 'num_bytes')
	structure = 'BB'

class LSGetStatus(Command):
	command = 0xe
	expected_reply = LSStatus
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

class StatusResponse(Reply): pass

class LSReadResponse(Reply):
	fields = ('status', 'data')
	structure = 'B17p'

class LSRead(Command):
	command = 0x10
	expected_reply = LSReadResponse
	fields = ('port',)
	structure = 'B'

	def validate_settings(self):
		assert self.port in InputPort.values()

class MessageReadResponse(Reply):
	fields = 'status', 'box', 'message'
	structure = 'BB60p'

class MessageRead(Command):
	expected_reply = MessageReadResponse
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

#!python

# $Id$

"""
jaraco.nxt.messages
"""

__author__='Jason R. Coombs <jaraco@jaraco.com>'
__svnauthor__='$Author$'[9:-2]

import struct
import re

class Message(object):
	_expects_reply = False
	_version = 0
	
	def __init__(self, payload):
		self.payload = payload

	def __str__(self):
		return struct.pack('2B', len(self), self._version) + self.payload

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

	def __init__(self):
		pass

	@property
	def payload(self):
		return struct.pack('2B', self.expects_reply, self.command)
	
class QueryBattery(Command):
	_expects_reply = True
	command = 0xB

class BatteryResponse(Message):
	def get_voltage(self):
		voltage = struct.unpack('H', self.payload[3:5])
		return voltage

class PlayTone(Command):
	command = 0x3
	
	def __init__(self, frequency, duration = 100):
		assert 200 <= frequency <= 3000
		self.frequency = frequency
		self.duration = duration

	@property
	def payload(self):
		additional_payload = struct.pack('2H', self.frequency, self.duration)
		return super(PlayTone, self).payload + additional_payload

class SendMailboxMessage(Command):
	command = 0x9
	
	def __init__(self, message, box_number=1):
		self.box = box_number-1
		self.message = message

	@property
	def payload(self):
		additional_payload = struct.pack('B', self.box) + self.message + '\x00'
		return super(SendMailboxMessage, self).payload + additional_payload
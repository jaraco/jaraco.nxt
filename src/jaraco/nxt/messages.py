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
		struct.pack('4b', len(self), self._version, self.payload)

	def __len__(self):
		return len(self.payload)

	@property
	def expects_reply(self):
		return [0x80, 0][self._expects_reply]

	@classmethod
	def read(cls, stream):
		len, ver = struct.unpack('2b', stream.read(2))
		assert ver == cls._version
		assert len > 0
		return cls(stream.read(len))

class Command(Message):
	_expects_reply = False

	def __init__(self):
		pass

	@property
	def payload(self):
		return struct.pack('2b', self.expects_reply, self.command)
	
class QueryBattery(Command):
	_expects_reply = True
	command = 0xB

class BatteryResponse(Message):
	def get_voltage(self):
		voltage = struct.unpack('h', self.payload[3:5])
		return voltage

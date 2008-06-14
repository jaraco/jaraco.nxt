#!python

# $Id$

"""
jaraco.nxt package

Modules suitable for interacting with the Lego Mindstorms NXT
products.

Requires a bluetooth connection (and utilizes serial protocol).
"""

__author__='Jason R. Coombs <jaraco@jaraco.com>'
__svnauthor__='$Author$'[8:-2]

import serial
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

class Connection(object):
	"A low-level connection to an NXT brick"
	huh = struct.pack('h', 2432) # don't really know what this is

	def __init__(self, comport, timeout=1):
		comport = self.__adapt_comport_string(comport)
		self._conn = serial.Serial(comport, timeout=timeout)

	@staticmethod
	def __adapt_comport_string(comport):
		pattern = re.compile('COM(%d+)')
		matcher = pattern.match(comport)
		if matcher:
			comport = int(matcher.group(1))-1
		return comport

	def receive(self, cls=Message):
		'return Message'
		msg = cls.read(self._conn)
		return msg

	def send(self, message):
		"Send a message to the NXT"
		self._conn.write(str(message))

	def __del__(self):
		try:
			self.close()
		except:
			pass
			
	def close(self):
		self._conn.close()
		
def get_voltage(conn):
	cmd = QueryBattery()
	conn.send(cmd)
	response = conn.receive(BatteryResponse)
	return response.get_voltage()

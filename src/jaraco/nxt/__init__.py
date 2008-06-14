#!python

# $Id$

"""
jaraco.nxt package

Modules suitable for interacting with the Lego Mindstorms NXT
products.

Requires a bluetooth connection (and utilizes serial protocol).
"""

__author__='Jason R. Coombs <jaraco@jaraco.com>'
__svnauthor__='$Author$'[9:-2]

import serial
import struct
import re

from messages import *

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

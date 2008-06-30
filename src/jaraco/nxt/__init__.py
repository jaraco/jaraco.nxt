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
import time

import messages

def add_options(parser):
	parser.add_option("-p", "--port")

class Connection(serial.Serial):
	"""
	A low-level connection to an NXT brick
	
	Requires that the brick is already paired with this device using
	Bluetooth.
	
	Example usage:
	conn = Connection('COM3')
	"""
	def receive(self):
		'Receive a message from the NXT'
		return messages.Message.read(self)

	def send(self, message):
		"Send a message to the NXT"
		self.write(str(message))

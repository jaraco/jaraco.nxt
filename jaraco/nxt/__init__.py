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

import traceback
import logging

import serial

from jaraco.nxt import messages

try:
	import bluetooth
except ImportError:
	import types
	bluetooth = types.ModuleType('bluetooth')
	bluetooth.BluetoothSocket = type('BluetoothSocket', (object,), dict())
	bluetooth.discover_devices = lambda *args, **kwargs: []

log = logging.getLogger(__name__)

def add_options(parser):
	parser.add_option("-p", "--port")

class Device:
	def receive(self):
		'Receive a message from the NXT'
		return messages.Message.read(self)

	def send(self, message):
		"Send a message to the NXT"
		self.write(str(message))

class Connection(serial.Serial, Device):
	"""
	A low-level connection to an NXT brick

	Requires that the brick is already paired with this device using
	Bluetooth.

	Example usage:
	conn = Connection('COM3')
	"""

class BluetoothDevice(Device, bluetooth.BluetoothSocket):
	port = 1

	def __init__(self, host):
		bluetooth.BluetoothSocket.__init__(self, bluetooth.RFCOMM)
		hp = (host, self.port)
		self.connect(hp)

	def read(self, nbytes):
		return self.recv(nbytes)

	def write(self, bytes):
		bluetooth.BluetoothSocket.send(self, bytes)

class DeviceNotFoundException(Exception): pass

class Locator:
	def find_brick(self):
		try:
			return next(self.find_bricks())
		except StopIteration:
			raise DeviceNotFoundException()

	def find_bricks(self):
		for candidate in self.find_candidates():
			try:
				candidate.send(messages.GetBatteryLevel())
				resp = candidate.receive()
			except Exception:
				traceback.print_exc()
			except IOError:
				pass
			yield candidate

	def find_candidates(self):
		for host, name in bluetooth.discover_devices(lookup_names=True):
			log.debug('Attempting to connect to bluetooth host %s (%s)', host, name)
			try:
				yield BluetoothDevice(host)
			except IOError:
				pass
		for serial_port in range(10):
			log.debug('Attempting to connect to serial port %d', serial_port)
			try:
				yield Connection(serial_port, writeTimeout=1)
			except serial.SerialException:
				pass

locator = Locator()

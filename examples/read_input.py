"""
This example demonstrates how one might read sensor values from the brick.
"""

import sys

from jaraco.nxt import messages
from jaraco.nxt import locator
from jaraco.nxt import _enum as enum

def run():
	dev = locator.find_brick()

	# read the values form this port
	port = enum.InputPort(1)

	# configure the input mode
	dev.send(messages.SetInputMode(
		port,
		messages.SensorType.switch,
		messages.SensorMode.boolean,
	))

	# print out the field names once
	print(', '.join(field[:4] for field in messages.InputValues.fields))

	try:
		while True: query_status(dev, port)
	except KeyboardInterrupt:
		sys.stdout.write('\n')

def query_status(dev, port):
	"""
	Send the GetInputValues message, then process the
	jaraco.nxt.messages.InputValues reply, printing each
	of the fields in a CSV format.
	"""

	# query for the input values and re-write the line
	dev.send(messages.GetInputValues(port))
	input_res = dev.receive()
	# print each of the fields
	values = ', '.join('%4d' % getattr(input_res, field) for field in input_res.fields)
	# carriage return but no line feed so we write over the previous line
	sys.stdout.write('\r')
	sys.stdout.write(values)

__name__ == '__main__' and run()

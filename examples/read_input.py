"""
This example demonstrates how one might read sensor values from the brick.
"""

import sys

from jaraco.nxt import Connection
from jaraco.nxt import messages
from jaraco.nxt import locator

dev = locator.find_brick()

# read the values form this port
port = 1
# send the GetInputValues message, which returns a
#  jaraco.nxt.messages.InputValues reply
dev.send(messages.SetInputMode(
	1,
	messages.SensorType.switch,
	messages.SensorMode.boolean,
))

# print out the field names once
print ', '.join(field[:4] for field in messages.InputValues.fields)

def query_status():
	# query for the input values and re-write the line
	dev.send(messages.GetInputValues(port))
	input_res = dev.receive()
	# print each of the fields
	values = ', '.join('%4d' % getattr(input_res, field) for field in input_res.fields)
	# carriage return but no line feed so we write over the previous line
	sys.stdout.write('\r')
	sys.stdout.write(values)

try:
	while True: query_status()
except KeyboardInterrupt:
	sys.stdout.write('\n')

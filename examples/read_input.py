"""
This example demonstrates how one might read sensor values from the brick.

Caution: this module has not been tested. Please report your experience
with it.
"""

from jaraco.nxt import Connection
from jaraco.nxt.messages import GetInputValues
from jaraco.nxt import locator

dev = locator.find_brick()

# read the values form this port
port = 1
# send the GetInputValues message, which returns a
#  jaraco.nxt.messages.InputValues reply
input_values = dev.send(GetInputValues(port))
# print each of the fields
for field in input_value.fields:
	value = getattr(input_values, field)
	print("%(field)s:\t%(value)s" % vars())

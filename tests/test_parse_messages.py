import struct
import logging

from jaraco.nxt.messages import Message, BatteryResponse
from StringIO import StringIO


logging.basicConfig(level=logging.DEBUG)

def test_sample_battery_message():
	sample_battery_response = '\x02\x0b\x00\x50\x00'
	sample = sample_battery_response
	msg_len = struct.pack('H', len(sample))
	s = StringIO(msg_len+sample)
	msg = Message.read(s)
	assert isinstance(msg, BatteryResponse), type(msg)

def run():
	test_sample_battery_message()

if __name__ == '__main__':
	run()

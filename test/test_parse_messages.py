#!python

import logging
logging.basicConfig(level=logging.DEBUG)

from jaraco.nxt.messages import *
from StringIO import StringIO
sample_battery_response = '\x02\x0b\x00\x50\x00'
sample = sample_battery_response
len = struct.pack('H', len(sample))
s = StringIO(len+sample)
msg = Message.read(s)


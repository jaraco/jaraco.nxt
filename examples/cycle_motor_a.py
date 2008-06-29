#!python

from jaraco.nxt import *
from jaraco.nxt.routine import cycle_motor_a

conn = Connection('COM4')
cycle_motor_a(conn)

conn.close()
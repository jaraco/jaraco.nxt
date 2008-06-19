#!python

from jaraco.nxt import *
from jaraco.nxt.routine import cycle_motor

conn = Connection('COM4')
cycle_motor(conn, 'b')

conn.close()
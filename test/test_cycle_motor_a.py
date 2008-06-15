#!python

from jaraco.nxt import *
conn = Connection('COM4')
cycle_motor_a(conn)
conn.close()
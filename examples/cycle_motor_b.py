#!python

from jaraco.nxt import Connection
from jaraco.nxt.routine import cycle_motor

def run():
	conn = Connection('COM4')
	cycle_motor(conn, 'b')

	conn.close()

__name__ == '__main__' and run()

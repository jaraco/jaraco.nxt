#!python

from jaraco.nxt import Connection
from jaraco.nxt.routine import cycle_motor_a


def run():
    conn = Connection('COM4')
    cycle_motor_a(conn)

    conn.close()


__name__ == '__main__' and run()

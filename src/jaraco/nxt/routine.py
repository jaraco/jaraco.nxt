#!python

# $Id$

"""
jaraco.nxt.routine module
"""

__author__='Jason R. Coombs <jaraco@jaraco.com>'
__svnauthor__='$Author$'[9:-2]

import time

from jaraco.nxt.messages import *

def get_voltage(conn):
	cmd = QueryBattery()
	conn.send(cmd)
	response = conn.receive(BatteryResponse)
	return response.get_voltage()

def get_port(port, cls):
	if isinstance(port, basestring):
		port = getattr(cls, port)
	assert port in cls.values()
	return port

def cycle_motor(conn, port):
	"Turn the motor one direction, then the other, then stop it"
	port = get_port(port, OutputPort)
	cmd = SetOutputState(port, motor_on=True, set_power=60, run_state=RunState.running)
	conn.send(cmd)
	time.sleep(2)
	cmd = SetOutputState(port, motor_on=True, set_power=-60, run_state=RunState.running)
	conn.send(cmd)
	time.sleep(2)
	cmd = SetOutputState(port)
	conn.send(cmd)
	
def cycle_motor_a(conn):
	cycle_motor(conn, 'a')

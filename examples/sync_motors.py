#!python

# $Id$

from jaraco.nxt import Connection
from jaraco.nxt.messages import *
import time

conn = Connection(5)

synced_port = OutputPort.c
cmd = SetOutputState(
	synced_port,
	turn_ratio=0,
	regulation_mode=RegulationMode.motor_sync,
	motor_on=True,
	set_power=100,
	)
conn.send(cmd)

cmd = SetOutputState(OutputPort.b,
	regulation_mode=RegulationMode.motor_sync,
	turn_ratio=20,
	run_state=RunState.running,
	motor_on=True,
	set_power=100,
	)
conn.send(cmd)

time.sleep(2)

stop_cmd = SetOutputState(OutputPort.b)

conn.send(stop_cmd)

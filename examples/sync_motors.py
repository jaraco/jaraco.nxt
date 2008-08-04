#!python

# $Id$

# http://forums.nxtasy.org/index.php?showtopic=2553&st=20&start=20

from jaraco.nxt import Connection
from jaraco.nxt.messages import *
import time

conn = Connection(5)

reg_cmd = SetOutputState(
	OutputPort.b,
	use_regulation=True,
	regulation_mode=RegulationMode.motor_sync,
	)
conn.send(reg_cmd)
reg_cmd.port = OutputPort.c
conn.send(reg_cmd)

run_cmd = reg_cmd
#run_cmd.port = OutputPort.b
run_cmd.run_state = RunState.running
run_cmd.set_power = 100
run_cmd.motor_on = True

conn.send(run_cmd)

time.sleep(2)

stop_cmd = SetOutputState(OutputPort.b)
conn.send(stop_cmd)
stop_cmd = SetOutputState(OutputPort.c)
conn.send(stop_cmd)

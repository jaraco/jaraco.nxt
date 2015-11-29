#!python

# http://forums.nxtasy.org/index.php?showtopic=2553&st=20&start=20

from jaraco.nxt import Connection
from jaraco.nxt.messages import (
	SetOutputState, OutputPort, RegulationMode, RunState
)
import time

def run():
	conn = Connection(5)

	conn.send(SetOutputState(OutputPort.b))
	conn.send(SetOutputState(OutputPort.c))

	regulation_params = dict(
		use_regulation=True,
		regulation_mode=RegulationMode.motor_sync,
		turn_ratio=100,
		)
	run_params = dict(
		run_state = RunState.running,
		set_power = 75,
		motor_on=True,
		)
	all_params = dict(regulation_params)
	all_params.update(run_params)
	reg_cmd = SetOutputState(OutputPort.b, **all_params)
	conn.send(reg_cmd)
	time.sleep(2)
	run_cmd = SetOutputState(OutputPort.c, **all_params)
	run_cmd.turn_ratio=5
	conn.send(run_cmd)

	time.sleep(5)

	stop_cmd = SetOutputState(OutputPort.b)
	conn.send(stop_cmd)
	stop_cmd = SetOutputState(OutputPort.c)
	conn.send(stop_cmd)

__name__ == '__main__' and run()

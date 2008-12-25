#!python
# -*- coding: utf-8 -*-

# This is a port of %% Example 3: Drive Around Table
#  from the Matlab rwth libraries
# In this little demo, our bot drives a square on the floor around a well known table.

from jaraco.nxt import Connection
from jaraco.nxt.messages import *
import time

# Constants
table_length	 = 2850	 # in degrees of motor rotations :-)
quarter_turn_ticks = 245	 # in motor degrees, how much is a 90° turn of the bot?

power_mul = 1 # my motors are upside down

# Open NXT connection
connection = Connection(3)


def initialize():
	# Initialize Motors...
	# we send this in case they should still be spinning or something...
	connection.send(SetOutputState(OutputPort.all))
	# and we also "clean up" before we start:
	ports = (OutputPort.b, OutputPort.c)
	for port in ports:
		connection.send(ResetMotorPosition(port))

initialize()

#todo - port this to the library
def wait_for_motor(conn, port):
	cmd = GetOutputState(port)
	status = RunState.running
	while status == RunState.running:
		conn.send(cmd)
		status = conn.receive().run_state
		print 'run_state is', status
		time.sleep(.1)
	print 'exiting wait for motor'

# Start the engines, main loop begins (repeated 4 times)
# 4 times because we got 4 equal sides of the table :-)
for j in range(4):
	j += 1

	# Build Drive commands
	cmds = [
		SetOutputState(
			OutputPort.b,
			motor_on = True,
			regulation_mode = RegulationMode.motor_sync,
			run_state = RunState.running,
			set_power = power_mul*75,
			tacho_limit = table_length,
			turn_ratio = 0, # straight ahead
		),
		SetOutputState(
			OutputPort.c,
			motor_on = True,
			regulation_mode = RegulationMode.motor_sync,
			run_state = RunState.running,
			set_power = power_mul*75,
			tacho_limit = table_length,
			turn_ratio = 0, # straight ahead
		),
	]
	map(connection.send, cmds)
		
	# let the robot start:
	time.sleep(1)

	# Check for the end end of table
	wait_for_motor(connection, OutputPort.b)
	
	# give it a little time to correct its mistakes (hey synchronisation
	# mode :-)
	time.sleep(2)
	
	# apparently we've stopped!
	# then release the motors
	initialize()
	# if we don't do that, syncing again doesn't work
	
	# and again, if we don't rest relative counters, synced turning etc doesnt work...
	

	# Now please turn
	
	# Build Drive commands
	cmds = [
		SetOutputState(
			OutputPort.b,
			motor_on = True,
			regulation_mode = RegulationMode.motor_sync,
			run_state = RunState.running,
			set_power = power_mul*75,  # slower is more accurate
			tacho_limit = quarter_turn_ticks,
			turn_ratio = 100, # turn right
		),
		SetOutputState(
			OutputPort.c,
			motor_on = True,
			regulation_mode = RegulationMode.motor_sync,
			run_state = RunState.running,
			set_power = power_mul*75,  # slower is more accurate
			tacho_limit = quarter_turn_ticks,
			turn_ratio = 100, # turn right
		),
	]
	
	map(connection.send, cmds)
		
	# leave the bot time to start turning
	time.sleep(1)

	# Check for the end of rotation
	wait_for_motor(connection, OutputPort.b)
	
	# give it a little time to correct its mistakes (hey synchronisation
	# mode :-)
	time.sleep(2)
	
	# apparently we've stopped!
	# then release the motors
	initialize()

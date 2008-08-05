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
QuarterTurnTicks = 245	 # in motor degrees, how much is a 90° turn of the bot?


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
			set_power = 75,
			tacho_limit = table_length,
			turn_ratio = 0, # straight ahead
		),
		SetOutputState(
			OutputPort.c,
			motor_on = True,
			regulation_mode = RegulationMode.motor_sync,
			run_state = RunState.running,
			set_power = 75,
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
	
	
"""
%% Now please turn 

	SetMotor(MOTOR_B);
		SyncToMotor(MOTOR_C); % this means we have to set parameters only once
		SetPower(30) % slower is more acurate
		SetAngleLimit(QuarterTurnTicks);
		SetTurnRatio(100) % turn right
	SendMotorSettings();  % and GO!

	% leave the bot time to start turning
	pause(1);
	
%% Check for the end of rotation

	WaitForMotor(GetMotor);
	
	% give it a little time to correct its mistakes (hey synchronisation mode :-)
	pause(2);
	
	% apparently we've stopped!
	% then release the motors
	StopMotor('all', 'off');
	% if we don't do that, syncing again doesn't work
	
	% and again, if we don't rest relative counters, synced turning etc doesnt work...
	ResetMotorAngle(MOTOR_B);
	ResetMotorAngle(MOTOR_C);
	
%% Thats it. Repeat 4 times....
end%for


% Hey! End of a hard day's work
% Just to show good style, we close down our motors again:
StopMotor('all', 'off');
% although this was completely unnecessary....

% nice


%% Close Bluetooth

COM_CloseNXT(handle);
"""

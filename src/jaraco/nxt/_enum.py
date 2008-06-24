#!python

# $Id$

from enum import Enum

CommandTypes = Enum('direct', 'system')

class SpecEnum(object):

	@classmethod
	def dictionary(cls):
		from jaraco.util.dictlib import DictFilter
		return dict(DictFilter(cls.__dict__, include_pattern='[^_].*'))

	@classmethod
	def keys(cls):
		return cls.dictionary().keys()
		
	@classmethod
	def values(cls):
		return cls.dictionary().values()

class OutputPort(SpecEnum):
	a = 0
	b = 1
	c = 2
	all = 0xff

class OutputMode(SpecEnum):
	motor_on = 1
	brake = 2
	regulated = 4

# RegulationMode = Enum('idle', 'motor_speed', 'motor_sync')
class RegulationMode(SpecEnum):
	idle = 0
	motor_speed = 1
	motor_sync = 2

class RunState(SpecEnum):
	idle = 0x00
	rampup = 0x10
	running = 0x20
	rampdown = 0x40

class SensorType(SpecEnum):
	no_sensor = 0
	switch = 1
	temperature = 2
	reflection = 3
	angle = 4
	light_active = 5
	light_inactive = 6
	sound_db = 7
	sound_dba = 8
	custom = 9
	lowspeed = 0xa
	lowspeed_9v = 0xb
	no_of_sensor_types = 0xc

class SensorMode(SpecEnum):
	raw = 0
	boolean = 0x20
	transition_count = 0x40
	period_counter = 0x60
	pct_full_scale = 0x80
	celcius = 0xA0
	fahrenheit = 0xC0
	angle_steps = 0xE0
	slope_mask = 0x1F
	mode_mask = 0xE0
	

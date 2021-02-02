import time

from .messages import SetOutputState, GetBatteryLevel, OutputPort, RunState


def get_voltage(conn):
    cmd = GetBatteryLevel()
    conn.send(cmd)
    response = conn.receive()
    return response.get_voltage()


def get_port(port, cls):
    if isinstance(port, str):
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

import importlib.util
import pathlib
import types

import pytest

examples = pathlib.Path(__file__).parent.parent / 'examples'


def load(name):
    spec = importlib.util.spec_from_file_location(name, examples / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeDevice:
    def __init__(self, reply):
        self.reply = reply
        self.sent = []

    def send(self, msg):
        self.sent.append(msg)

    def receive(self):
        return self.reply


@pytest.fixture
def battery_voltage():
    return load('get_battery_voltage')


def test_get_battery_voltage(battery_voltage, monkeypatch, capsys):
    reply = types.SimpleNamespace(millivolts=7800)
    monkeypatch.setattr(battery_voltage, 'Connection', lambda port: FakeDevice(reply))
    battery_voltage.run()
    assert 'battery voltage is 7800 mV.' in capsys.readouterr().out


def test_read_input_query_status(capsys):
    read_input = load('read_input')
    reply = types.SimpleNamespace(fields=('a', 'b'), a=1, b=22)
    read_input.query_status(FakeDevice(reply), read_input.enum.InputPort(1))
    assert capsys.readouterr().out == '\r   1,   22'

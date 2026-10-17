import serial

import jaraco.nxt


class Candidate:
    def __init__(self, exc=None):
        self.exc = exc

    def send(self, msg):
        if self.exc:
            raise self.exc

    def receive(self):
        pass


def test_find_bricks(monkeypatch, capsys):
    candidates = [Candidate(), Candidate(OSError('unreachable'))]
    monkeypatch.setattr(jaraco.nxt.Locator, 'find_candidates', lambda self: candidates)
    assert list(jaraco.nxt.Locator().find_bricks()) == candidates
    assert 'unreachable' in capsys.readouterr().err


def test_find_candidates_none_available(monkeypatch):
    def fail(*args, **kwargs):
        raise OSError()

    def no_serial(*args, **kwargs):
        raise serial.SerialException()

    monkeypatch.setattr(
        jaraco.nxt.bluetooth,
        'discover_devices',
        lambda **kwargs: [('00:11:22:33:44:55', 'NXT')],
    )
    monkeypatch.setattr(jaraco.nxt, 'BluetoothDevice', fail)
    monkeypatch.setattr(jaraco.nxt, 'Connection', no_serial)
    assert list(jaraco.nxt.Locator().find_candidates()) == []

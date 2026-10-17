from jaraco.nxt import controller, routine


def test_print_voltage(monkeypatch, capsys):
    monkeypatch.setattr(routine, 'get_voltage', lambda conn: 7.5)
    controller.print_voltage(type('Controller', (), dict(conn=None)))
    assert 'battery voltage is 7.500000' in capsys.readouterr().out

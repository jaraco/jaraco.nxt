from jaraco.nxt import Connection, messages


def run():
    conn = Connection(3)
    msg = messages.GetBatteryLevel()
    conn.send(msg)
    resp = conn.receive()
    print(f'received response: {type(resp)}')
    print(f'battery voltage is {resp.millivolts:d} mV.')


__name__ == '__main__' and run()

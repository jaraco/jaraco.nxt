from jaraco.nxt import Connection, messages
conn = Connection(3)
msg = messages.GetBatteryLevel()
conn.send(msg)
resp = conn.receive()
print 'received response: %s' % type(resp)
print 'battery voltage is %d mV.' % resp.millivolts
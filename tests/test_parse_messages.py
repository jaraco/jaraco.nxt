import struct
import logging
import io

from jaraco.nxt.messages import Message, BatteryResponse


logging.basicConfig(level=logging.DEBUG)


def test_sample_battery_message():
    sample_battery_response = b'\x02\x0b\x00\x50\x00'
    sample = sample_battery_response
    msg_len = struct.pack('H', len(sample))
    s = io.BytesIO(msg_len + sample)
    msg = Message.read(s)
    assert isinstance(msg, BatteryResponse), type(msg)


def run():
    test_sample_battery_message()


if __name__ == '__main__':
    run()

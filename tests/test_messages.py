import pytest

from jaraco.nxt.messages import MessageRead


def test_message_read_payload():
    msg = MessageRead(box_number=2, remove=True)
    assert msg.payload == bytes([0x00, 0x13, 0x0B, 0x01, 0x01])


def test_message_read_invalid_box():
    with pytest.raises(AssertionError, match='invalid box number 11'):
        MessageRead(box_number=11)

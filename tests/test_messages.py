import pytest

from jaraco.nxt.messages import (
    LSWrite,
    MessageRead,
    MessageWrite,
    OutputPort,
    StartProgram,
)


def test_message_read_payload():
    msg = MessageRead(box_number=2, remove=True)
    assert msg.payload == bytes([0x00, 0x13, 0x0B, 0x01, 0x01])


def test_message_read_invalid_box():
    with pytest.raises(AssertionError, match='invalid box number 11'):
        MessageRead(box_number=11)


def test_start_program_invalid_filename():
    with pytest.raises(AssertionError, match='invalid filename !'):
        StartProgram.validate_filename('!')


def test_message_write():
    msg = MessageWrite('hi', box_number=2)
    assert msg.Zmessage == 'hi\x00'
    assert msg.structure == 'BB3s'


def test_message_write_invalid_box():
    with pytest.raises(AssertionError, match='invalid box number 11'):
        MessageWrite('hi', box_number=11)


def test_ls_write_structure():
    msg = LSWrite(port=OutputPort.a, data=b'\x01\x02')
    assert msg.structure == 'BBB2s'

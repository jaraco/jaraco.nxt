"""
jaraco.nxt package

Modules suitable for interacting with the Lego Mindstorms NXT
products.

Requires a bluetooth connection (and utilizes serial protocol).
"""

import logging
import traceback

import serial

from jaraco.nxt import messages

try:
    import bluetooth
except ImportError:
    import types

    bluetooth = types.ModuleType('bluetooth')
    bluetooth.BluetoothSocket = type('BluetoothSocket', (), {})
    bluetooth.discover_devices = lambda *args, **kwargs: []

log = logging.getLogger(__name__)


def add_arguments(parser):
    parser.add_argument("-p", "--port")


class Device:
    def receive(self):
        'Receive a message from the NXT'
        return messages.Message.read(self)

    def send(self, message):
        "Send a message to the NXT"
        self.write(str(message))


class Connection(serial.Serial, Device):
    """
    A low-level connection to an NXT brick

    Requires that the brick is already paired with this device using
    Bluetooth.

    Example usage:
    conn = Connection('COM3')
    """


class BluetoothDevice(Device, bluetooth.BluetoothSocket):
    port = 1

    def __init__(self, host):
        bluetooth.BluetoothSocket.__init__(self, bluetooth.RFCOMM)
        hp = (host, self.port)
        self.connect(hp)

    def read(self, nbytes):
        return self.recv(nbytes)

    def write(self, bytes):
        bluetooth.BluetoothSocket.send(self, bytes)


class DeviceNotFoundException(Exception):
    pass


class Locator:
    def find_brick(self):
        try:
            return next(self.find_bricks())
        except StopIteration:
            raise DeviceNotFoundException()

    def find_bricks(self):
        for candidate in self.find_candidates():
            try:
                candidate.send(messages.GetBatteryLevel())
                candidate.receive()
            except Exception:  # noqa: BLE001 # report any failure probing a candidate
                traceback.print_exc()
            yield candidate

    def find_candidates(self):
        for host, name in bluetooth.discover_devices(lookup_names=True):
            log.debug('Attempting to connect to bluetooth host %s (%s)', host, name)
            try:
                yield BluetoothDevice(host)
            except OSError:
                pass
        for serial_port in range(10):
            log.debug('Attempting to connect to serial port %d', serial_port)
            try:
                yield Connection(serial_port, writeTimeout=1)
            except serial.SerialException:
                pass


locator = Locator()

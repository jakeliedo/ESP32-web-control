# XPT2046 Touch Controller Driver for MicroPython
# Basic version for SPI touch panel (TFT)

from machine import Pin, SPI
import time

class XPT2046:
    def __init__(self, spi, cs, irq=None):
        self.spi = spi
        self.cs = cs
        self.irq = irq
        self.cs.init(Pin.OUT, value=1)
        if self.irq:
            self.irq.init(Pin.IN)

    def touched(self):
        if self.irq:
            return self.irq.value() == 0  # Active low
        # If no IRQ, always try to read
        return True

    def get_touch(self):
        # Read X and Y position from XPT2046
        self.cs.value(0)
        time.sleep_us(2)
        x = self._read_value(0xD0)  # X position command
        y = self._read_value(0x90)  # Y position command
        self.cs.value(1)
        # Convert raw to screen coordinates (calibration may be needed)
        x = max(0, min(240, int((x - 200) * 240 / 3800)))
        y = max(0, min(320, int((y - 200) * 320 / 3800)))
        return x, y

    def _read_value(self, command):
        buf = bytearray(3)
        buf[0] = command
        self.spi.write(buf[:1])
        data = self.spi.read(2)
        value = ((data[0] << 8) | data[1]) >> 3
        return value

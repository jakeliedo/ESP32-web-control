"""
ST7789P3 Display Driver for ESP32
3.2 inch TFT Display Controller
"""

from machine import Pin, SPI
import time

class ST7789P3:
    """ST7789P3 3.2" TFT Display Driver"""
    # Display dimensions
    WIDTH = 240
    HEIGHT = 320
    # ST7789P3 Commands
    CMD_SWRESET = 0x01  # Software Reset
    CMD_SLPOUT = 0x11   # Sleep Out
    CMD_DISPOFF = 0x28  # Display Off
    CMD_DISPON = 0x29   # Display On
    CMD_CASET = 0x2A    # Column Address Set
    CMD_RASET = 0x2B    # Row Address Set
    CMD_RAMWR = 0x2C    # Memory Write
    CMD_MADCTL = 0x36   # Memory Data Access Control
    CMD_COLMOD = 0x3A   # Interface Pixel Format
    # Colors (RGB565)
    BLACK = 0x0000
    WHITE = 0xFFFF
    RED = 0xF800
    GREEN = 0x07E0
    BLUE = 0x001F
    YELLOW = 0xFFE0
    CYAN = 0x07FF
    MAGENTA = 0xF81F
    GRAY = 0x8410
    ORANGE = 0xFD20
    def __init__(self, spi, cs, dc, rst, bl=None):
        self.spi = spi
        self.cs = Pin(cs, Pin.OUT)
        self.dc = Pin(dc, Pin.OUT)
        self.rst = Pin(rst, Pin.OUT)
        self.bl = Pin(bl, Pin.OUT) if bl else None
        self.cs.on()
        self.dc.off()
        self.rst.on()
        if self.bl:
            self.bl.on()
        self.init_display()
    def write_cmd(self, cmd):
        self.dc.off()
        self.cs.off()
        self.spi.write(bytes([cmd]))
        self.cs.on()
    def write_data(self, data):
        self.dc.on()
        self.cs.off()
        if isinstance(data, int):
            self.spi.write(bytes([data]))
        else:
            self.spi.write(data)
        self.cs.on()
    def init_display(self):
        self.rst.off()
        time.sleep_ms(10)
        self.rst.on()
        time.sleep_ms(10)
        self.write_cmd(self.CMD_SWRESET)
        time.sleep_ms(120)
        self.write_cmd(self.CMD_SLPOUT)
        time.sleep_ms(120)
        self.write_cmd(self.CMD_MADCTL)
        self.write_data(0x00)
        self.write_cmd(self.CMD_COLMOD)
        self.write_data(0x55)
        self.write_cmd(self.CMD_DISPON)
        time.sleep_ms(120)
    def set_window(self, x0, y0, x1, y1):
        self.write_cmd(self.CMD_CASET)
        self.write_data(x0 >> 8)
        self.write_data(x0 & 0xFF)
        self.write_data(x1 >> 8)
        self.write_data(x1 & 0xFF)
        self.write_cmd(self.CMD_RASET)
        self.write_data(y0 >> 8)
        self.write_data(y0 & 0xFF)
        self.write_data(y1 >> 8)
        self.write_data(y1 & 0xFF)
        self.write_cmd(self.CMD_RAMWR)
    def fill(self, color):
        self.set_window(0, 0, self.WIDTH - 1, self.HEIGHT - 1)
        color_high = color >> 8
        color_low = color & 0xFF
        line_data = bytes([color_high, color_low] * self.WIDTH)
        self.dc.on()
        self.cs.off()
        for _ in range(self.HEIGHT):
            self.spi.write(line_data)
        self.cs.on()
    def text(self, text, x, y, color, bg_color=None, scale=1):
        for i, char in enumerate(text):
            char_x = x + i * 8 * scale
            if char_x >= self.WIDTH:
                break
            for row in range(8):
                if y + row * scale >= self.HEIGHT:
                    break
                for col in range(8):
                    if char_x + col * scale >= self.WIDTH:
                        break
                    if ord(char) >= 32 and ord(char) <= 127:
                        bitmap = self.FONT_8X8[ord(char) - 32]
                    else:
                        bitmap = self.FONT_8X8[0]
                    if bitmap[row] & (1 << (7 - col)):
                        if scale == 1:
                            self.pixel(char_x + col, y + row, color)
                        else:
                            for sy in range(scale):
                                for sx in range(scale):
                                    self.pixel(char_x + col * scale + sx, y + row * scale + sy, color)
    def pixel(self, x, y, color):
        if 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT:
            self.set_window(x, y, x, y)
            self.write_data(color >> 8)
            self.write_data(color & 0xFF)
    def rect(self, x, y, w, h, color, fill=False):
        if fill:
            for i in range(h):
                self.hline(x, y + i, w, color)
        else:
            self.hline(x, y, w, color)
            self.hline(x, y + h - 1, w, color)
            self.vline(x, y, h, color)
            self.vline(x + w - 1, y, h, color)
    def hline(self, x, y, w, color):
        if y >= 0 and y < self.HEIGHT:
            x = max(0, x)
            w = min(w, self.WIDTH - x)
            if w > 0:
                self.set_window(x, y, x + w - 1, y)
                color_high = color >> 8
                color_low = color & 0xFF
                line_data = bytes([color_high, color_low] * w)
                self.dc.on()
                self.cs.off()
                self.spi.write(line_data)
                self.cs.on()
    def vline(self, x, y, h, color):
        if x >= 0 and x < self.WIDTH:
            y = max(0, y)
            h = min(h, self.HEIGHT - y)
            if h > 0:
                for i in range(h):
                    self.pixel(x, y + i, color)
    FONT_8X8 = [
        [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00], # space
        [0x18,0x3C,0x3C,0x18,0x18,0x00,0x18,0x00], # !
        [0x6C,0x6C,0x48,0x00,0x00,0x00,0x00,0x00], # "
        [0x6C,0x6C,0xFE,0x6C,0xFE,0x6C,0x6C,0x00], # #
        [0x18,0x3E,0x60,0x3C,0x06,0x7C,0x18,0x00], # $
        [0x00,0xC6,0xCC,0x18,0x30,0x66,0xC6,0x00], # %
        [0x38,0x6C,0x38,0x76,0xDC,0xCC,0x76,0x00], # &
        [0x18,0x18,0x30,0x00,0x00,0x00,0x00,0x00], # '
        [0x0C,0x18,0x30,0x30,0x30,0x18,0x0C,0x00], # (
        [0x30,0x18,0x0C,0x0C,0x0C,0x18,0x30,0x00], # )
        [0x00,0x66,0x3C,0xFF,0x3C,0x66,0x00,0x00], # *
        [0x00,0x18,0x18,0x7E,0x18,0x18,0x00,0x00], # +
        [0x00,0x00,0x00,0x00,0x18,0x18,0x30,0x00], # ,
        [0x00,0x00,0x00,0x7E,0x00,0x00,0x00,0x00], # -
        [0x00,0x00,0x00,0x00,0x18,0x18,0x00,0x00], # .
        [0x06,0x0C,0x18,0x30,0x60,0xC0,0x80,0x00], # /
        # ... (bạn có thể bổ sung thêm font nếu cần)
    ]

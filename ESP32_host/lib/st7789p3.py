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
        """Initialize ST7789P3 display"""
        self.spi = spi
        self.cs = Pin(cs, Pin.OUT)
        self.dc = Pin(dc, Pin.OUT)
        self.rst = Pin(rst, Pin.OUT)
        self.bl = Pin(bl, Pin.OUT) if bl else None
        
        self.cs.on()
        self.dc.off()
        self.rst.on()
        
        if self.bl:
            self.bl.on()  # Turn on backlight
        
        self.init_display()
    
    def write_cmd(self, cmd):
        """Write command to display"""
        self.dc.off()  # Command mode
        self.cs.off()
        self.spi.write(bytes([cmd]))
        self.cs.on()
    
    def write_data(self, data):
        """Write data to display"""
        self.dc.on()  # Data mode
        self.cs.off()
        if isinstance(data, int):
            self.spi.write(bytes([data]))
        else:
            self.spi.write(data)
        self.cs.on()
    
    def init_display(self):
        """Initialize display registers"""
        print("🔧 Initializing ST7789P3 display...")
        
        # Hardware reset
        self.rst.off()
        time.sleep_ms(10)
        self.rst.on()
        time.sleep_ms(10)
        
        # Software reset
        self.write_cmd(self.CMD_SWRESET)
        time.sleep_ms(120)
        
        # Sleep out
        self.write_cmd(self.CMD_SLPOUT)
        time.sleep_ms(120)
        
        # Memory Data Access Control
        self.write_cmd(self.CMD_MADCTL)
        self.write_data(0x00)  # RGB order, normal scan
        
        # Interface Pixel Format (16-bit color)
        self.write_cmd(self.CMD_COLMOD)
        self.write_data(0x55)  # 16-bit RGB565
        
        # Display on
        self.write_cmd(self.CMD_DISPON)
        time.sleep_ms(120)
        
        print("✅ ST7789P3 display initialized")
    
    def set_window(self, x0, y0, x1, y1):
        """Set drawing window"""
        # Column address set
        self.write_cmd(self.CMD_CASET)
        self.write_data(x0 >> 8)
        self.write_data(x0 & 0xFF)
        self.write_data(x1 >> 8)
        self.write_data(x1 & 0xFF)
        
        # Row address set
        self.write_cmd(self.CMD_RASET)
        self.write_data(y0 >> 8)
        self.write_data(y0 & 0xFF)
        self.write_data(y1 >> 8)
        self.write_data(y1 & 0xFF)
        
        # Memory write
        self.write_cmd(self.CMD_RAMWR)
    
    def fill(self, color):
        """Fill entire screen with color"""
        self.set_window(0, 0, self.WIDTH - 1, self.HEIGHT - 1)
        
        # Prepare color data
        color_high = color >> 8
        color_low = color & 0xFF
        line_data = bytes([color_high, color_low] * self.WIDTH)
        
        # Write color data for all pixels
        self.dc.on()  # Data mode
        self.cs.off()
        for _ in range(self.HEIGHT):
            self.spi.write(line_data)
        self.cs.on()
    
    def pixel(self, x, y, color):
        """Draw single pixel"""
        if 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT:
            self.set_window(x, y, x, y)
            self.write_data(color >> 8)
            self.write_data(color & 0xFF)
    
    def hline(self, x, y, w, color):
        """Draw horizontal line"""
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
        """Draw vertical line"""
        if x >= 0 and x < self.WIDTH:
            y = max(0, y)
            h = min(h, self.HEIGHT - y)
            if h > 0:
                for i in range(h):
                    self.pixel(x, y + i, color)
    
    def rect(self, x, y, w, h, color, fill=False):
        """Draw rectangle"""
        if fill:
            for i in range(h):
                self.hline(x, y + i, w, color)
        else:
            self.hline(x, y, w, color)          # Top
            self.hline(x, y + h - 1, w, color) # Bottom
            self.vline(x, y, h, color)          # Left
            self.vline(x + w - 1, y, h, color) # Right
    
    def text(self, text, x, y, color, bg_color=None, scale=1):
        """Draw text using 8x8 bitmap font"""
        char_width = 8 * scale
        char_height = 8 * scale
        
        for i, char in enumerate(text):
            char_x = x + i * char_width
            if char_x >= self.WIDTH:
                break
            
            # Get character bitmap
            char_upper = char.upper()
            if char_upper in self.FONT_8X8:
                bitmap = self.FONT_8X8[char_upper]
            else:
                bitmap = self.FONT_8X8[' ']  # Default to space
            
            # Draw character background if specified
            if bg_color is not None:
                self.rect(char_x, y, char_width, char_height, bg_color, fill=True)
            
            # Draw character pixels
            for row in range(8):
                if y + row * scale >= self.HEIGHT:
                    break
                for col in range(8):
                    if char_x + col * scale >= self.WIDTH:
                        break
                    if bitmap[row] & (1 << (7 - col)):
                        # Draw pixel(s) for this bit
                        if scale == 1:
                            self.pixel(char_x + col, y + row, color)
                        else:
                            # Scale up the pixel
                            for sy in range(scale):
                                for sx in range(scale):
                                    self.pixel(char_x + col * scale + sx, 
                                             y + row * scale + sy, color)
    
    def brightness(self, level):
        """Set display brightness (0-100)"""
        if self.bl:
            # Simple on/off for now
            # Real PWM implementation would provide smooth brightness control
            if level > 50:
                self.bl.on()
            else:
                self.bl.off()
    
    def sleep(self):
        """Put display to sleep"""
        self.write_cmd(self.CMD_DISPOFF)
        time.sleep_ms(10)
    
    def wake(self):
        """Wake display from sleep"""
        self.write_cmd(self.CMD_DISPON)
        time.sleep_ms(10)
    
    def init(self):
        """Initialize display (alias for init_display)"""
        self.init_display()
    
    # Simple 8x8 font bitmap for basic characters
    FONT_8X8 = {
        ' ': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
        'A': [0x18, 0x3C, 0x66, 0x66, 0x7E, 0x66, 0x66, 0x00],
        'B': [0x7C, 0x66, 0x66, 0x7C, 0x66, 0x66, 0x7C, 0x00],
        'C': [0x3C, 0x66, 0x60, 0x60, 0x60, 0x66, 0x3C, 0x00],
        'D': [0x78, 0x6C, 0x66, 0x66, 0x66, 0x6C, 0x78, 0x00],
        'E': [0x7E, 0x60, 0x60, 0x7C, 0x60, 0x60, 0x7E, 0x00],
        'F': [0x7E, 0x60, 0x60, 0x7C, 0x60, 0x60, 0x60, 0x00],
        'G': [0x3C, 0x66, 0x60, 0x6E, 0x66, 0x66, 0x3C, 0x00],
        'H': [0x66, 0x66, 0x66, 0x7E, 0x66, 0x66, 0x66, 0x00],
        'I': [0x3C, 0x18, 0x18, 0x18, 0x18, 0x18, 0x3C, 0x00],
        'J': [0x1E, 0x0C, 0x0C, 0x0C, 0x0C, 0x6C, 0x38, 0x00],
        'K': [0x66, 0x6C, 0x78, 0x70, 0x78, 0x6C, 0x66, 0x00],
        'L': [0x60, 0x60, 0x60, 0x60, 0x60, 0x60, 0x7E, 0x00],
        'M': [0x63, 0x77, 0x7F, 0x6B, 0x63, 0x63, 0x63, 0x00],
        'N': [0x66, 0x76, 0x7E, 0x7E, 0x6E, 0x66, 0x66, 0x00],
        'O': [0x3C, 0x66, 0x66, 0x66, 0x66, 0x66, 0x3C, 0x00],
        'P': [0x7C, 0x66, 0x66, 0x7C, 0x60, 0x60, 0x60, 0x00],
        'Q': [0x3C, 0x66, 0x66, 0x66, 0x66, 0x3C, 0x0E, 0x00],
        'R': [0x7C, 0x66, 0x66, 0x7C, 0x78, 0x6C, 0x66, 0x00],
        'S': [0x3C, 0x66, 0x60, 0x3C, 0x06, 0x66, 0x3C, 0x00],
        'T': [0x7E, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x00],
        'U': [0x66, 0x66, 0x66, 0x66, 0x66, 0x66, 0x3C, 0x00],
        'V': [0x66, 0x66, 0x66, 0x66, 0x66, 0x3C, 0x18, 0x00],
        'W': [0x63, 0x63, 0x63, 0x6B, 0x7F, 0x77, 0x63, 0x00],
        'X': [0x66, 0x66, 0x3C, 0x18, 0x3C, 0x66, 0x66, 0x00],
        'Y': [0x66, 0x66, 0x66, 0x3C, 0x18, 0x18, 0x18, 0x00],
        'Z': [0x7E, 0x06, 0x0C, 0x18, 0x30, 0x60, 0x7E, 0x00],
        '0': [0x3C, 0x66, 0x6E, 0x76, 0x66, 0x66, 0x3C, 0x00],
        '1': [0x18, 0x18, 0x38, 0x18, 0x18, 0x18, 0x7E, 0x00],
        '2': [0x3C, 0x66, 0x06, 0x0C, 0x30, 0x60, 0x7E, 0x00],
        '3': [0x3C, 0x66, 0x06, 0x1C, 0x06, 0x66, 0x3C, 0x00],
        '4': [0x06, 0x0E, 0x1E, 0x66, 0x7F, 0x06, 0x06, 0x00],
        '5': [0x7E, 0x60, 0x7C, 0x06, 0x06, 0x66, 0x3C, 0x00],
        '6': [0x3C, 0x66, 0x60, 0x7C, 0x66, 0x66, 0x3C, 0x00],
        '7': [0x7E, 0x66, 0x0C, 0x18, 0x18, 0x18, 0x18, 0x00],
        '8': [0x3C, 0x66, 0x66, 0x3C, 0x66, 0x66, 0x3C, 0x00],
        '9': [0x3C, 0x66, 0x66, 0x3E, 0x06, 0x66, 0x3C, 0x00],
        ':': [0x00, 0x00, 0x18, 0x00, 0x00, 0x18, 0x00, 0x00],
        '.': [0x00, 0x00, 0x00, 0x00, 0x00, 0x18, 0x18, 0x00],
        '-': [0x00, 0x00, 0x00, 0x7E, 0x00, 0x00, 0x00, 0x00],
        '>': [0x18, 0x3C, 0x66, 0xC3, 0x66, 0x3C, 0x18, 0x00],
    }

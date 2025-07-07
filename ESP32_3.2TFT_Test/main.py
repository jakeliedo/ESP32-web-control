# ESP32 3.2" TFT ST7789P3 Test Code
# Mapping chân:
# SPI_SCLK = 14
# SPI_MOSI = 13
# SPI_CS   = 15
# DC_PIN   = 2
# RST_PIN  = 3

from machine import Pin, SPI
import time
from lib.st7789p3 import ST7789P3

# Khởi tạo SPI cho màn hình
spi = SPI(2, baudrate=40000000, sck=Pin(14), mosi=Pin(13))

# Khởi tạo màn hình
# Không truyền BL_PIN vì backlight đã nối nguồn
lcd = ST7789P3(spi, 15, 2, 3)
lcd.init()

# Test fill màu
colors = [ST7789P3.RED, ST7789P3.GREEN, ST7789P3.BLUE, ST7789P3.WHITE, ST7789P3.BLACK]
for color in colors:
    lcd.fill(color)
    time.sleep(0.5)

# Test vẽ text
lcd.fill(ST7789P3.BLACK)
lcd.text("ST7789P3 OK!", 40, 100, ST7789P3.GREEN)
lcd.text("ESP32 3.2\" TFT", 30, 130, ST7789P3.CYAN)
lcd.text("Mapping OK!", 50, 160, ST7789P3.YELLOW)

# Test vẽ hình chữ nhật
lcd.rect(20, 200, 200, 40, ST7789P3.MAGENTA, fill=True)
lcd.text("Test Done!", 60, 215, ST7789P3.WHITE)

while True:
    pass

#include <Arduino.h>

#include <Arduino_GFX_Library.h>
#include <XPT2046_Touchscreen.h>
#define TFT_BL 27
#define screenWidth 320
#define screenHeight 240

Arduino_DataBus *bus = new Arduino_ESP32SPI(2, 15, 14, 13, GFX_NOT_DEFINED);
Arduino_GFX *gfx = new Arduino_ST7789(bus, -1, 1, true);

const uint16_t rainbowColors[7] = {
    0xF800, // Red
    0xFC00, // Orange
    0xFFE0, // Yellow
    0x07E0, // Green
    0x001F, // Blue
    0x4810, // Indigo
    0x901F  // Violet
};

unsigned long lastColorChange = 0;
uint8_t currentColorIndex = 0;
uint8_t nextColorIndex = 1;
float t = 0.0; // Tiến trình chuyển màu (0.0 -> 1.0)

uint16_t blendColor(uint16_t c1, uint16_t c2, float t) {
    // Tách RGB565 thành RGB888
    uint8_t r1 = ((c1 >> 11) & 0x1F) << 3;
    uint8_t g1 = ((c1 >> 5) & 0x3F) << 2;
    uint8_t b1 = (c1 & 0x1F) << 3;
    uint8_t r2 = ((c2 >> 11) & 0x1F) << 3;
    uint8_t g2 = ((c2 >> 5) & 0x3F) << 2;
    uint8_t b2 = (c2 & 0x1F) << 3;
    // Nội suy và giảm sáng 50%
    uint8_t r = ((1-t)*r1 + t*r2) * 0.5;
    uint8_t g = ((1-t)*g1 + t*g2) * 0.5;
    uint8_t b = ((1-t)*b1 + t*b2) * 0.5;
    // Ghép lại RGB565
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3);
}

void draw_gradient(uint16_t c1, uint16_t c2, float t) {
    uint16_t lineBuf[screenWidth];
    for (int y = 0; y < screenHeight; y++) {
        float ratio = (float)y / (screenHeight - 1);
        // Có thể dùng ratio để tạo hiệu ứng gradient dọc nếu muốn
        uint16_t color = blendColor(c1, c2, t);
        for (int x = 0; x < screenWidth; x++) {
            lineBuf[x] = color;
        }
        gfx->draw16bitRGBBitmap(0, y, lineBuf, screenWidth, 1);
    }
}

void setup() {
    Serial.begin(115200);
    gfx->begin(80000000);

#ifdef TFT_BL
    pinMode(TFT_BL, OUTPUT);
    digitalWrite(TFT_BL, HIGH);
    ledcSetup(0, 2000, 8);
    ledcAttachPin(TFT_BL, 0);
    ledcWrite(0, 128); // 50% độ sáng backlight
#endif

    draw_gradient(rainbowColors[currentColorIndex], rainbowColors[nextColorIndex], t);
}

void loop() {
    unsigned long now = millis();
    if (now - lastColorChange >= 20) {
        lastColorChange = now;
        t += 0.01;
        if (t >= 1.0) {
            t = 0.0;
            currentColorIndex = (currentColorIndex + 1) % 7;
        }
        nextColorIndex = (currentColorIndex + 1) % 7;
        draw_gradient(rainbowColors[currentColorIndex], rainbowColors[nextColorIndex], t);
    }
    delay(5);
}

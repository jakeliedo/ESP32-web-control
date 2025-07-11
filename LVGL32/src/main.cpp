#include <Arduino.h>
#include <lvgl.h>
#include <Arduino_GFX_Library.h>

#define TFT_BL 27
#define screenWidth 320
#define screenHeight 240

#if defined(DISPLAY_DEV_KIT)
Arduino_GFX *gfx = create_default_Arduino_GFX();
#else
Arduino_DataBus *bus = new Arduino_ESP32SPI(2 /* DC */, 15 /* CS */, 14 /* SCK */, 13 /* MOSI */, GFX_NOT_DEFINED /* MISO */);
Arduino_GFX *gfx = new Arduino_ST7789(bus, -1 /* RST */, 1 /* rotation */, true /* IPS */);
#endif

static lv_color_t buf1[screenWidth * 10]; // Buffer cho 10 dòng

void my_flush_cb(lv_display_t *disp, const lv_area_t *area, uint8_t *px_map) {
    uint32_t w = area->x2 - area->x1 + 1;
    uint32_t h = area->y2 - area->y1 + 1;
#if (LV_COLOR_16_SWAP != 0)
    gfx->draw16bitBeRGBBitmap(area->x1, area->y1, (uint16_t *)px_map, w, h);
#else
    gfx->draw16bitRGBBitmap(area->x1, area->y1, (uint16_t *)px_map, w, h);
#endif
    lv_display_flush_ready(disp);
}

lv_obj_t *scr = nullptr;
lv_obj_t *dummy_label = nullptr;
unsigned long lastColorChange = 0;
uint8_t currentColorIndex = 0;

// 7 màu sắc cầu vồng
const uint32_t rainbowColors[7] = {
    0xFF0000, // Red
    0xFF7F00, // Orange
    0xFFFF00, // Yellow
    0x00FF00, // Green
    0x0000FF, // Blue
    0x4B0082, // Indigo
    0x8B00FF  // Violet
};

void setup() {
    Serial.begin(115200);
    lv_init();
    gfx->begin(80000000);
    gfx->fillScreen(BLACK);

#ifdef TFT_BL
    pinMode(TFT_BL, OUTPUT);
    digitalWrite(TFT_BL, HIGH);
    ledcSetup(0, 2000, 8);
    ledcAttachPin(TFT_BL, 0);
    ledcWrite(0, 255);
#endif

    lv_display_t *disp = lv_display_create(screenWidth, screenHeight);
    lv_display_set_flush_cb(disp, my_flush_cb);
    lv_display_set_buffers(disp, buf1, NULL, sizeof(buf1), LV_DISPLAY_RENDER_MODE_PARTIAL);

    scr = lv_screen_active();
    lv_obj_set_style_bg_color(scr, lv_color_hex(rainbowColors[0]), LV_PART_MAIN);
    lv_obj_set_style_bg_opa(scr, LV_OPA_COVER, LV_PART_MAIN);

    // Thêm dummy label để đảm bảo LVGL cập nhật màn hình
    dummy_label = lv_label_create(scr);
    lv_label_set_text(dummy_label, "");
}

void loop() {
    lv_timer_handler();

    unsigned long now = millis();
    if (now - lastColorChange >= 500) {
        lastColorChange = now;
        currentColorIndex = (currentColorIndex + 1) % 7;

        lv_obj_set_style_bg_color(scr, lv_color_hex(rainbowColors[currentColorIndex]), LV_PART_MAIN);
        lv_obj_invalidate(scr); // Đánh dấu cần vẽ lại

        // Cập nhật dummy label để kích LVGL redraw
        lv_label_set_text_fmt(dummy_label, " "); // Nội dung không quan trọng
    }

    delay(5);
}

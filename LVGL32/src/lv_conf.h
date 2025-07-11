/**
 * LVGL v9.x Configuration for ESP32 + TFT_eSPI
 */
#ifndef LV_CONF_H
#define LV_CONF_H

/*====================
   COLOR SETTINGS
 *====================*/
#define LV_COLOR_DEPTH     16

/*=========================
   MEMORY SETTINGS
 *=========================*/
#define LV_MEM_SIZE    (64 * 1024U)
#define LV_MEM_ADR          0
#define LV_MEM_CUSTOM       0

/*====================
   HAL SETTINGS
 *====================*/
#define LV_TICK_CUSTOM       0
#define LV_USE_OS            LV_OS_NONE

/*====================
   RENDERING SETTINGS
 *====================*/
#define LV_USE_DRAW_SW       1
#define LV_DRAW_SW_COMPLEX   1

/*=================
   LOGGING
 *=================*/
#define LV_USE_LOG      1
#if LV_USE_LOG
  #define LV_LOG_LEVEL  LV_LOG_LEVEL_WARN
  #define LV_LOG_PRINTF 1
#endif

/*=================
   ASSERTS
 *=================*/
#define LV_USE_ASSERT_NULL          1
#define LV_USE_ASSERT_MALLOC        1
#define LV_USE_ASSERT_STYLE         0
#define LV_USE_ASSERT_MEM_INTEGRITY 0
#define LV_USE_ASSERT_OBJ           0

/*=================
   WIDGETS
 *=================*/
#define LV_USE_LABEL     1
#define LV_USE_BTN       1
#define LV_USE_IMG       1
#define LV_USE_SLIDER    1
#define LV_USE_SWITCH    1
#define LV_USE_ARC       1
#define LV_USE_TEXTAREA  1
#define LV_USE_DROPDOWN  1
#define LV_USE_ROLLER    1
#define LV_USE_SPINBOX   1
#define LV_USE_SPINNER   1
#define LV_USE_CHART     1
#define LV_USE_TABLE     1
#define LV_USE_MSGBOX    1

#endif /*LV_CONF_H*/

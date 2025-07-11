#ifndef LV_CONF_H
#define LV_CONF_H

/*====================
   COLOR SETTINGS
 *====================*/
#define LV_COLOR_DEPTH     16
#define LV_COLOR_16_SWAP   0

/*=========================
   MEMORY SETTINGS
 *=========================*/
#define LV_MEM_SIZE    (48U * 1024U)
#define LV_MEM_CUSTOM  0

/*====================
   HAL SETTINGS
 *====================*/
#define LV_TICK_CUSTOM       1
#if LV_TICK_CUSTOM
    #define LV_TICK_CUSTOM_INCLUDE "Arduino.h"
    #define LV_TICK_CUSTOM_SYS_TIME_EXPR (millis())
#endif

/*====================
   LOGGING
 *====================*/
#define LV_USE_LOG      1
#if LV_USE_LOG
  #define LV_LOG_LEVEL  LV_LOG_LEVEL_WARN
  #define LV_LOG_PRINTF 1
#endif

/*=================
   FONT
 *=================*/
#define LV_FONT_DEFAULT &lv_font_montserrat_14

//#define LV_USE_FS_STDIO 1
//#define LV_USE_PNG 1
//#define LV_USE_BMP 1
//#define LV_USE_JPG 1

#endif /*LV_CONF_H*/
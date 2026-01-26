[app]
title = Lut Orifice Flow Calc
package.name = lut_orifice_flow_calc
package.domain = org.lutfi
source.dir = .
source.include_exts = py,json,txt,png,jpg
version = 1.0
requirements = python3,kivy==2.2.1
orientation = portrait

# ANDROID İZİNLERİ - DÜZELTME
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True
android.skip_update = False

# İKON AYARI - YOL DÜZELTMESİ
icon.filename = icon.png

# SPLASH SCREEN AYARI - YOL DÜZELTMESİ
presplash.filename = splash.png
# Splash arka plan rengi (main.py'daki COLORS['bg_dark'] ile aynı)
presplash.color = #0D1117

log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1

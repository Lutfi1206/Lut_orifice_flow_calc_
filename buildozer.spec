[app]
title = Lut Orifice Flow Calc
package.name = lut_orifice_flow_calc
package.domain = org.lutfi
source.dir = .
source.include_exts = py,json,txt,png,jpg
version = 1.0
requirements = python3,kivy==2.2.1
orientation = portrait
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True
android.skip_update = False
# İKON AYARI:
icon.filename = %(source.dir)s/icon.png
# SPLASH SCREEN AYARI:
presplash.filename = %(source.dir)s/splash.png
presplash.color = #FFFFFF
log_level = 2

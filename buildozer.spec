[app]
title = Orifis
package.name = orifisapp
package.domain = org.lutfi
source.dir = .
source.include_exts = py,png,jpg,json,txt
version = 1.0
requirements = python3,kivy==2.2.1

# 👇 SADECE BUNU DEĞİŞTİR 👇
android.archs = armeabi-v7a  # Sadece tek arch
android.api = 30  # Daha düşük API
android.ndk = 23b  # Daha eski NDK
# 👆 DAHA HIZLI İNDİRİR 👆

orientation = portrait
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.minapi = 21
android.sdk = 30
android.accept_sdk_license = True

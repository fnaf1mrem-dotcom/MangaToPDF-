[app]
title = MangaToPDF
package.name = mangatopdf
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,txt,md
version = 1.0
requirements = python3,kivy,pillow,natsort
orientation = portrait
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 24
presplash.filename =
icon.filename = %(source.dir)s/icon.png

# buildozer settings
log_level = 2
[app]

# (str) Título de tu aplicación
title = MangaToPDF

# (str) Nombre del paquete, usa minúsculas y sin espacios
package.name = mangatopdf

# (str) Dominio del paquete (necesario para Android/iOS)
package.domain = org.ejemplo

# (str) Versión de la aplicación
version = 0.1

# (list) Requisitos de Python. Añade cualquier librería que uses.
# Por ejemplo, si usas `requests` para descargar mangas, añádelo aquí.
requirements = python3,kivy,pillow,reportlab,requests # Ejemplo: añade lo que uses

# (str) Versión de Kivy a usar (opcional, si quieres una específica)
# kivy_version = 2.2.1

# (str) El directorio donde se encuentra tu archivo principal (main.py)
# Si tu main.py está en la raíz, usa '.'
source.dir = .

# (str) El archivo de entrada principal de tu aplicación
main.py = main.py

# --- Configuración Específica de Android ---
android.enable = True

# (int) Nivel mínimo de API de Android (ej. 21, 24).
# A menudo se usa un nivel más bajo para asegurar compatibilidad con dispositivos antiguos.
android.minapi = 21

# (int) Nivel de API de Android al que se apunta. ¡Debe coincidir con GitHub Actions!
android.api = 33

# (str) Versión del NDK de Android. ¡Debe coincidir con GitHub Actions!
android.ndk = 25b # Esta es la versión de Buildozer para 25.2.9519653

# (str) Versión de las Build Tools de Android. ¡Debe coincidir con GitHub Actions!
android.build_tools_version = 33.0.2

# (bool) Modo debug (True para desarrollo, False para lanzamiento)
android.debug = True

# (list) Permisos necesarios para tu aplicación (ajusta según lo que necesite MangaToPDF)
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (list) Arquitecturas de CPU para Android (arm64-v8a es lo más común hoy en día)
p4a.arch = arm64-v8a

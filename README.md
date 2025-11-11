MangaToPDF (Kivy) - proyecto
============================

Archivos importantes:
- main.py
- buildozer.spec

Qué hace:
- Procesa /storage/emulated/0/Mangas
- Convierte cada carpeta-capítulo a PDF
- Soporta .webp, .jpg, .png
- Guarda PDFs en /storage/emulated/0/Mangas/PDFs
- Muestra logs en vivo y barra de progreso
- Borra carpeta de capítulo tras generar PDF

Cómo compilar (PC con Linux recomendado):
1) Instalar dependencias:
   sudo apt update
   sudo apt install -y python3-pip python3-venv build-essential autoconf libtool pkg-config git \
       libjpeg-dev zlib1g-dev libfreetype6-dev libssl-dev

2) Instalar buildozer:
   pip install --user buildozer
   python3 -m pip install --user cython

3) Inicializar (si necesario):
   buildozer init

4) Compilar (esto descargará SDK y requerirá ~several GB):
   buildozer -v android debug

   El APK quedará en bin/<appname>-debug.apk o similar.

Alternativa (sin PC): Subir repo a GitHub y usar un runner de CI configurado para buildozer (requiere setup).
# main.py
import os
import threading
import traceback
from functools import partial

from kivy.config import Config
# Preferencias para modo oscuro y tamaño
Config.set('kivy', 'keyboard_mode', 'systemandmulti')

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import mainthread
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout

# Dependencias que debe instalar Buildozer: pillow, natsort
from PIL import Image, ExifTags
from natsort import natsorted

# ---------- CONFIG ----------
BASE_DIR = "/storage/emulated/0/Mangas"  # ruta por defecto
VALID_EXT = (".jpg", ".jpeg", ".png", ".webp")
OUTPUT_SUBFOLDER = "PDFs"
TMP_SUBFOLDER = "tmp_img_kivy"
# ----------------------------

KV = '''
<RootWidget>:
    orientation: 'vertical'
    padding: dp(8)
    spacing: dp(8)
    BoxLayout:
        size_hint_y: None
        height: dp(56)
        canvas.before:
            Color:
                rgba: .07, .07, .07, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "📘 MangaToPDF"
            color: 1,1,1,1
            bold: True
    BoxLayout:
        size_hint_y: None
        height: dp(48)
        spacing: dp(8)
        Button:
            id: btn_start
            text: root.btn_text
            on_release: root.on_start_btn()
        Button:
            text: "Seleccionar carpeta (opcional)"
            on_release: root.on_select_folder()
    ProgressBar:
        id: pb
        max: 100
        value: root.progress
        size_hint_y: None
        height: dp(12)
    ScrollView:
        do_scroll_x: False
        do_scroll_y: True
        BoxLayout:
            id: logs_box
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            padding: dp(6)
            spacing: dp(6)
    BoxLayout:
        size_hint_y: None
        height: dp(32)
        Label:
            text: root.status
            color: .8,.8,.8,1
            font_size: '12sp'
'''

# ---------- Helpers ----------
def sanitize_filename(name: str) -> str:
    import re
    return re.sub(r'[\\/*?:"<>|]', '', name).strip()

def correct_exif_orientation(img: Image.Image) -> Image.Image:
    try:
        exif = img._getexif()
        if not exif:
            return img
        orientation_key = next((k for k, v in ExifTags.TAGS.items() if v == "Orientation"), None)
        if not orientation_key:
            return img
        orientation = exif.get(orientation_key, 1)
        methods = {
            1: lambda x: x,
            2: lambda x: x.transpose(Image.FLIP_LEFT_RIGHT),
            3: lambda x: x.rotate(180, expand=True),
            4: lambda x: x.transpose(Image.FLIP_TOP_BOTTOM),
            5: lambda x: x.transpose(Image.FLIP_LEFT_RIGHT).rotate(90, expand=True),
            6: lambda x: x.rotate(270, expand=True),
            7: lambda x: x.transpose(Image.FLIP_LEFT_RIGHT).rotate(270, expand=True),
            8: lambda x: x.rotate(90, expand=True)
        }
        return methods.get(orientation, lambda x: x)(img)
    except Exception:
        return img

# ---------- App root ----------
class RootWidget(BoxLayout):
    log_text = StringProperty("")
    status = StringProperty("Esperando...")
    progress = NumericProperty(0)
    btn_text = StringProperty("Empezar conversión")
    chosen_dir = StringProperty(BASE_DIR)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._stop_flag = False

    @mainthread
    def append_log(self, text, color=(1,1,1,1)):
        from kivy.uix.label import Label
        lbl = Label(text=str(text), size_hint_y=None, height=dp(20), halign='left', valign='middle')
        lbl.text_size = (self.width - 32, None)
        lbl.color = color
        self.ids.logs_box.add_widget(lbl)
        # autoscroll: ensure the scrollview scrolls down
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.ids.logs_box.parent.scroll_to(lbl), 0.05)

    @mainthread
    def set_status(self, text):
        self.status = text

    @mainthread
    def set_progress(self, val):
        try:
            self.progress = float(val)
        except:
            self.progress = 0

    def on_start_btn(self):
        # start worker thread
        self.ids.logs_box.clear_widgets()
        self.set_status("Iniciando...")
        self.set_progress(0)
        t = threading.Thread(target=self.worker_process_all, daemon=True)
        t.start()

    def on_select_folder(self):
        # Optional: in Kivy we keep default path; show info log
        self.append_log("Si necesitas otra ruta, edita BASE_DIR en el app (por ahora usa /storage/emulated/0/Mangas).")

    # ---------- Worker ----------
    def worker_process_all(self):
        try:
            mangas = [os.path.join(self.chosen_dir, d) for d in natsorted(os.listdir(self.chosen_dir)) if os.path.isdir(os.path.join(self.chosen_dir, d))]
        except Exception as e:
            self.append_log(f"Error accediendo a {self.chosen_dir}: {e}", (1,0.4,0.4,1))
            self.set_status("Error acceso")
            return

        total = len(mangas)
        if total == 0:
            self.append_log("No se encontraron mangas en la carpeta.", (1,0.8,0.2,1))
            self.set_status("Nada que hacer")
            return

        processed = 0
        for manga_dir in mangas:
            if self._stop_flag:
                break
            name = os.path.basename(manga_dir)
            self.append_log(f"🔍 Procesando: {name}")
            self.set_status(f"Procesando: {name}")
            self.worker_process_manga(manga_dir)
            processed += 1
            self.set_progress( (processed/total)*100 )
        self.set_status("Finalizado")
        self.append_log("🎉 Conversión completada para todos los mangas.", (0.6,1,0.6,1))
        self.set_progress(100)

    def worker_process_manga(self, manga_dir):
        # find chapter folders that match Capítulo N pattern, else any directory
        chapters = []
        ignored = []
        import re
        for name in os.listdir(manga_dir):
            path = os.path.join(manga_dir, name)
            if os.path.isdir(path):
                if re.search(r"Cap[ií]tulo\s*\d+(?:\.\d+)?", name, re.IGNORECASE):
                    chapters.append(path)
                else:
                    ignored.append(name)
        if not chapters:
            self.append_log(f"⚠️ No se detectaron capítulos formales en {os.path.basename(manga_dir)} - intento automático por subcarpetas.")
            # fallback: take all subdirs
            chapters = [os.path.join(manga_dir, d) for d in os.listdir(manga_dir) if os.path.isdir(os.path.join(manga_dir, d))]

        chapters = natsorted(chapters)
        output_dir = os.path.join(manga_dir, OUTPUT_SUBFOLDER)
        os.makedirs(output_dir, exist_ok=True)

        for cap in chapters:
            try:
                cap_name = os.path.basename(cap)
                self.append_log(f"  📘 Capítulo: {cap_name}")
                # collect images (walk single level, sorted)
                images = [os.path.join(cap, f) for f in os.listdir(cap) if f.lower().endswith(VALID_EXT)]
                images = natsorted(images)
                if not images:
                    self.append_log(f"    ⚠️ No hay imágenes en {cap_name}", (1,0.6,0.4,1))
                    continue

                # assemble name like "Capítulo 1" from folder
                nombre_pdf = self.simplify_name(cap_name)
                salida = os.path.join(output_dir, f"{nombre_pdf}.pdf")

                if os.path.exists(salida):
                    self.append_log(f"    ⏭️ Ya existe {os.path.basename(salida)}, saltando.")
                    continue

                # process images one by one to avoid mem usage
                pil_images = []
                for i, p in enumerate(images):
                    try:
                        img = Image.open(p)
                        img = correct_exif_orientation(img)
                        img = img.convert("RGB")
                        pil_images.append(img)
                        self.append_log(f"    └─ {os.path.basename(p)}")
                        # If too many images, save to reduce memory? We keep list modest.
                    except Exception as e:
                        self.append_log(f"    ❌ Falló abrir {p}: {e}", (1,0.5,0.5,1))

                if pil_images:
                    # save PDF
                    pil_images[0].save(salida, save_all=True, append_images=pil_images[1:])
                    self.append_log(f"    ✅ PDF creado: {os.path.basename(salida)}", (0.6,1,0.6,1))
                    # close images and free
                    for im in pil_images:
                        try:
                            im.close()
                        except: pass
                    pil_images = []
                    # delete folder after success
                    try:
                        import shutil
                        shutil.rmtree(cap)
                        self.append_log(f"    🧹 Carpeta eliminada: {cap_name}")
                    except Exception as e:
                        self.append_log(f"    ⚠️ No se pudo borrar carpeta: {e}", (1,0.6,0.4,1))
                else:
                    self.append_log("    ❌ No se generó PDF (no se pudieron abrir imágenes).", (1,0.5,0.5,1))

            except Exception as e:
                self.append_log(f"    ERROR inesperado: {e}\n{traceback.format_exc()}", (1,0.4,0.4,1))

    def simplify_name(self, raw):
        # remove subtitle: "Título ... Capítulo 1: Nombre" -> "Capítulo 1"
        import re
        m = re.search(r"Cap[ií]tulo\s*(\d+(?:\.\d+)?)", raw, re.IGNORECASE)
        if m:
            num = m.group(1)
            # convert decimals like 1.00 to 1
            if num.endswith(".00"):
                num = str(int(float(num)))
            return f"Capítulo {num}"
        # fallback: take first two words
        parts = raw.split()
        return " ".join(parts[:2]) if len(parts) >= 2 else raw

# small helper dp import
def dp(x): 
    from kivy.metrics import dp as _dp
    return _dp(x)

class MangaApp(App):
    def build(self):
        Builder.load_string(KV)
        root = RootWidget()
        return root

if __name__ == "__main__":
    MangaApp().run()
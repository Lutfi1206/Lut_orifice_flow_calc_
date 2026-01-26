import os
import json
import math
from pathlib import Path
import platform  # BU SATIRI KORU!
from datetime import datetime

# Kivy Imports
os.environ['KIVY_NO_CONSOLELOG'] = '0'
from kivy.config import Config

Config.set('kivy', 'keyboard_mode', 'system')
Config.set('kivy', 'keyboard_layout', 'qwerty')
Config.set('graphics', 'multisamples', '0')
Config.set('kivy', 'exit_on_escape', '0')
Config.set('kivy', 'log_level', 'debug')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.slider import Slider
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.animation import Animation
from kivy.core.text import LabelBase

current_platform = platform.system()  # platform'u saklamak için farklı isim kullan

if current_platform == "Android":
    try:
        from android.permissions import request_permissions, Permission
        
        def request_android_permissions():
            try:
                # Android 10+ için MANAGE_EXTERNAL_STORAGE izni gerekebilir
                request_permissions([
                    Permission.WRITE_EXTERNAL_STORAGE, 
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.INTERNET
                ])
            except Exception as e:
                print(f"İzin hatası: {e}")
        
        # Permissions'ı ana thread'de çağır (2 saniye sonra)
        Clock.schedule_once(lambda dt: request_android_permissions(), 2)
        
    except ImportError as e:
        print(f"Android modülü yüklenemedi: {e}")
    
    try:
        from android.storage import primary_external_storage_path
        from android import mActivity
        # Android 11+ için scoped storage
        BASE_DIR = Path(primary_external_storage_path()) / "OrifisApp"
    except Exception as e:
        print(f"Android storage hatası: {e}")
        BASE_DIR = Path("/storage/emulated/0/OrifisApp")
else:
    BASE_DIR = Path(".")

# Dizin oluşturmayı garanti altına al
try:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ana dizin: {BASE_DIR}")
except Exception as e:
    print(f"Dizin oluşturma hatası: {e}")
    BASE_DIR = Path(".")

SAVE_DIR = BASE_DIR / "orifis_kayitlar"
CUSTOM_GASES_FILE = BASE_DIR / "custom_gases.json"

try:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Kayıt dizini: {SAVE_DIR}")
except Exception as e:
    print(f"Kayıt dizini oluşturma hatası: {e}")

# Yazı tipi kaydı - DÜZELTİLMİŞ HALİ
try:
    # Windows'ta font yükle
    if current_platform == "Windows":
        # Windows font yolları
        possible_fonts = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/tahoma.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "./DejaVuSans.ttf"
        ]
        for font_path in possible_fonts:
            if os.path.exists(font_path):
                LabelBase.register(name='DejaVuSans', fn_regular=font_path)
                print(f"Font yüklendi: {font_path}")
                break
        else:
            print("Font bulunamadı, sistem fontu kullanılacak")
    elif current_platform == "Android":
        # Android'de Roboto fontunu kullan
        LabelBase.register(name='DejaVuSans', fn_regular='/system/fonts/Roboto-Regular.ttf')
    else:
        # Linux/Mac için
        LabelBase.register(name='DejaVuSans', fn_regular='DejaVuSans.ttf')
except Exception as e:
    print(f"Font yükleme hatası: {e}")
    # Font yüklenemezse sistem fontunu kullan
    pass

# Dizin oluşturmayı garanti altına al
try:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ana dizin: {BASE_DIR}")
except Exception as e:
    print(f"Dizin oluşturma hatası: {e}")
    BASE_DIR = Path(".")

SAVE_DIR = BASE_DIR / "orifis_kayitlar"
CUSTOM_GASES_FILE = BASE_DIR / "custom_gases.json"

try:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Kayıt dizini: {SAVE_DIR}")
except Exception as e:
    print(f"Kayıt dizini oluşturma hatası: {e}")

# Yazı tipi kaydı
try:
    # Android'de assets içindeki fontları kullan
    if platform.system() == "Android":
        LabelBase.register(name='DejaVuSans', fn_regular='/system/fonts/Roboto-Regular.ttf')
    else:
        LabelBase.register(name='DejaVuSans', fn_regular='DejaVuSans.ttf')
except Exception as e:
    print(f"Font yükleme hatası: {e}")
    # Font yüklenemezse sistem fontunu kullan
    pass

# MODERN UI RENK PALETİ
COLORS = {
    'bg_dark': (0.051, 0.067, 0.090, 1),
    'bg_card': (0.086, 0.106, 0.133, 1),
    'border_dark': (0.188, 0.212, 0.239, 1),
    'text_white': (0.788, 0.820, 0.855, 1),
    'text_gray': (0.545, 0.580, 0.620, 1),
    'text_light_gray': (0.431, 0.463, 0.506, 1),
    'primary_blue': (0.345, 0.651, 1.0, 1),
    'primary_blue_dark': (0.122, 0.435, 0.922, 1),
    'success_green': (0.139, 0.525, 0.212, 1),
    'success_green_dark': (0.098, 0.424, 0.180, 1),
    'success_light': (0.494, 0.906, 0.529, 1),
    'error_red': (0.855, 0.212, 0.200, 1),
    'error_red_dark': (0.620, 0.110, 0.098, 1),
    'warning_orange': (0.824, 0.663, 0.133, 1),
    'warning_orange_dark': (0.620, 0.416, 0.012, 1),
    'purple': (0.537, 0.341, 0.898, 1),
    'purple_dark': (0.353, 0.196, 0.639, 1),
    'disabled_gray': (0.129, 0.149, 0.176, 1),
    'input_bg': (0.051, 0.067, 0.090, 1),
    'scroll_dark': (0.545, 0.580, 0.620, 0.5),
}

GAZLAR = {
    "Amonyak (NH₃)": {
        "mol_agirligi": 17.03,
        "cp_cv": 1.29,
        "viskozite_293": 1.16e-05,
        "formula": "NH₃",
        "aciklama": "Soğutma gazı, gübre üretimi",
        "tip": "gaz",
        "atmosferik_yogunluk": 0.771,
        "atmosferik_viskozite": 1.16e-05,
        "yogunluk_293": 0.73
    },
    "Hava": {
        "mol_agirligi": 28.97,
        "cp_cv": 1.4,
        "viskozite_293": 1.81e-05,
        "formula": "N₂+O₂",
        "aciklama": "Atmosferik hava",
        "tip": "gaz",
        "atmosferik_yogunluk": 1.293,
        "atmosferik_viskozite": 1.81e-05,
        "yogunluk_293": 1.204
    },
    "Azot (N₂)": {
        "mol_agirligi": 28.01,
        "cp_cv": 1.4,
        "viskozite_293": 1.78e-05,
        "formula": "N₂",
        "aciklama": "İnert atmosfer, gıda paketleme",
        "tip": "gaz",
        "atmosferik_yogunluk": 1.250,
        "atmosferik_viskozite": 1.78e-05
    },
    "Oksijen (O₂)": {
        "mol_agirligi": 32.00,
        "cp_cv": 1.4,
        "viskozite_293": 2.04e-05,
        "formula": "O₂",
        "aciklama": "Medikal, kaynak, yanma",
        "tip": "gaz",
        "atmosferik_yogunluk": 1.429,
        "atmosferik_viskozite": 2.04e-05
    },
    "Su (H₂O) - Sıvı": {
        "mol_agirligi": 18.02,
        "viskozite_293": 1.00e-03,
        "yogunluk_293": 998.2,
        "formula": "H₂O",
        "aciklama": "Sıvı su, 20°C",
        "tip": "sıvı",
        "atmosferik_yogunluk": 998.2,
        "atmosferik_viskozite": 1.00e-03
    },
    "Yağ - Endüstriyel": {
        "viskozite_293": 0.065,
        "yogunluk_293": 850.0,
        "formula": "Yağ",
        "aciklama": "Hidrolik yağ, 20°C",
        "tip": "sıvı",
        "atmosferik_yogunluk": 850.0,
        "atmosferik_viskozite": 0.065
    },
    "MANUEL GİRİŞ": {
        "mol_agirligi": 0,
        "viskozite_293": 0,
        "formula": "MANUEL",
        "aciklama": "Değerleri manuel girin",
        "tip": "manuel",
        "atmosferik_yogunluk": 0.771,
        "atmosferik_viskozite": 1.16e-05
    }
}

VARSAYILAN_DEGERLER = {
    "D": 0.2073,
    "d": 0.1282268,
    "L1": 0.03,
    "L2": 0.03,
    "C0_baslangic": 1e-9,
    "delta_p": 729.0,
    "p1": 285471.0,
    "p2": 278321.9522,
    "sicaklik": 293.15,
    "gaz_tipi": "Amonyak (NH₃)",
    "yogunluk_manuel": 0.771,
    "viskozite_manuel": 1.16e-05,
    "yogunluk_atmosferik": 0.771,
    "viskozite_atmosferik": 1.16e-05,
    "max_iter": 100,
    "epsilon": 0.000001,
    "basinc_mode": "delta",
    "yogunluk_mode": "manuel",
    "viskozite_mode": "manuel",
    "d_birim": "m",
    "D_birim": "m",
    "basinc_birim": "Pa",
    "sicaklik_birim": "K"
}

class CompactTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.background_normal = ''
        self.background_active = ''
        self.background_color = COLORS['input_bg']
        self.foreground_color = COLORS['text_white']
        self.hint_text_color = COLORS['text_gray']
        self.cursor_color = COLORS['primary_blue']
        self.font_size = dp(12)  # %20 küçültülmüş
        self.padding = [dp(12), dp(8)]  # %20 küçültülmüş (14->12, 10->8)
        self.multiline = False
        self.font_name = 'DejaVuSans'
        
        with self.canvas.after:
            Color(*COLORS['border_dark'])
            self._border = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(6)),  # %20 küçültülmüş
                width=1
            )
        
        self.bind(
            pos=lambda *args: self._update_border(),
            size=lambda *args: self._update_border(),
            focus=self._on_focus_change
        )
    
    def _update_border(self):
        if hasattr(self, '_border'):
            self._border.rounded_rectangle = (
                self.x, self.y, self.width, self.height, dp(6)  # %20 küçültülmüş
            )
    
    def _on_focus_change(self, instance, value):
        if not hasattr(self, '_border'):
            return
            
        self.canvas.after.clear()
        
        with self.canvas.after:
            if value:
                Color(*COLORS['primary_blue'])
                self._border = Line(
                    rounded_rectangle=(self.x, self.y, self.width, self.height, dp(6)),  # %20 küçültülmüş
                    width=2
                )
                self.background_color = (0.08, 0.10, 0.12, 1)
            else:
                Color(*COLORS['border_dark'])
                self._border = Line(
                    rounded_rectangle=(self.x, self.y, self.width, self.height, dp(6)),  # %20 küçültülmüş
                    width=1
                )
                self.background_color = COLORS['input_bg']

class CompactButton(Button):
    def __init__(self, text="", color_type="primary", icon="", **kwargs):
        if 'color' not in kwargs:
            kwargs['color'] = (1, 1, 1, 1)

        super().__init__(**kwargs)
        self.text = f"{icon}  {text}" if icon else text
        self.font_name = 'DejaVuSans'
        self.font_size = dp(13)  # %20 küçültülmüş
        self.bold = True
        self.size_hint_y = None
        self.height = dp(36)  # %20 küçültülmüş (40->32, düzeltildi 32->36)

        color_map = {
            "primary": COLORS['success_green'],
            "secondary": COLORS['primary_blue'],
            "warning": COLORS['warning_orange'],
            "danger": COLORS['error_red'],
            "purple": COLORS['purple'],
        }

        self.background_normal = ''
        self.background_down = ''
        self.background_color = color_map.get(color_type, COLORS['success_green'])

        with self.canvas.before:
            Color(*self.background_color)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(7)])  # %20 küçültülmüş (8->7)

        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def on_press(self):
        anim = Animation(opacity=0.8, duration=0.1)
        anim.start(self)

    def on_release(self):
        anim = Animation(opacity=1.0, duration=0.1)
        anim.start(self)

class CompactSpinner(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = COLORS['disabled_gray']
        self.color = COLORS['text_white']
        self.font_size = dp(12)  # %20 küçültülmüş (12->11)
        self.padding = [dp(12), dp(8)]  # %20 küçültülmüş (14->12, 10->8)
        self.size_hint_x = 0.25  # ENLERİ DÜŞÜRÜLDÜ (daha compact)

class OrifisHesap:
    def __init__(self):
        self.custom_gazlar = self.load_custom_gases()
    
    def get_save_dir(self):
        try:
            if current_platform == "Android":
                try:
                    # Önce app_storage_path dene
                    from android.storage import app_storage_path
                    base = Path(app_storage_path())
                except:
                    # Değilse context.getFilesDir() kullan
                    try:
                        from jnius import autoclass
                        PythonActivity = autoclass('org.kivy.android.PythonActivity')
                        context = PythonActivity.mActivity
                        files_dir = context.getFilesDir().getAbsolutePath()
                        base = Path(files_dir)
                    except:
                        base = Path(".")
            else:
                base = Path(".")
            
            save_dir = base / "orifis_kayitlar"
            save_dir.mkdir(parents=True, exist_ok=True)
            print(f"Save dir: {save_dir}")
            return save_dir
        except Exception as e:
            print(f"get_save_dir error: {e}")
            return Path(".")
    
    def get_gases_file(self):
        try:
            if current_platform == "Android":
                try:
                    from android.storage import primary_external_storage_path
                    base = Path(primary_external_storage_path()) / "OrifisApp"
                except:
                    base = Path(".")
            else:
                base = Path(".")
            return base / "custom_gases.json"
        except Exception:
            return Path("custom_gases.json")

    def load_custom_gases(self):
        try:
            dosya = self.get_gases_file()
            if dosya.exists():
                with open(dosya, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Gaz yükleme hatası: {e}")
        return {}

    def save_custom_gases(self):
        try:
            dosya = self.get_gases_file()
            with open(dosya, 'w', encoding='utf-8') as f:
                json.dump(self.custom_gazlar, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Gaz kaydetme hatası: {e}")
            return False

    def add_custom_gas(self, name, properties):
        self.custom_gazlar[name] = properties
        return self.save_custom_gases()

    def kaydet(self, data, dosya_adi=None):
        try:
            if not dosya_adi:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dosya_adi = f"orifis_{timestamp}.json"

            if not dosya_adi.endswith('.json'):
                dosya_adi += '.json'

            kayit_yolu = self.get_save_dir() / dosya_adi

            kayit_data = {
                "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "gaz": data.get("gaz", ""),
                "D": data.get("D", 0),
                "d": data.get("d", 0),
                "L1": data.get("L1", 0),
                "L2": data.get("L2", 0),
                "C0_baslangic": data.get("C0_baslangic", 0),
                "delta_p": data.get("delta_p", 0),
                "p1": data.get("p1_gauge", 0),
                "p2": data.get("p2_gauge", 0),
                "sicaklik": data.get("sicaklik_input", 293.15),
                "yogunluk_manuel": data.get("rho", 0),
                "viskozite_manuel": data.get("mu", 0),
                "max_iter": data.get("max_iter", 100),
                "epsilon": data.get("epsilon", 0.000001),
                "basinc_mode": data.get("basinc_mode", "delta"),
                "yogunluk_mode": data.get("yogunluk_mode", "manuel"),
                "viskozite_mode": data.get("viskozite_mode", "manuel"),
                "D_birim": data.get("D_birim", "m"),
                "d_birim": data.get("d_birim", "m"),
                "basinc_birim": data.get("basinc_birim", "Pa"),
                "sicaklik_birim": data.get("sicaklik_birim", "K")
            }

            with open(kayit_yolu, 'w', encoding='utf-8') as f:
                json.dump(kayit_data, f, ensure_ascii=False, indent=2)
            return kayit_yolu
        except Exception as e:
            print(f"Kayıt hatası: {e}")
            return None

    def yukle(self, dosya_adi):
        try:
            kayit_yolu = self.get_save_dir() / dosya_adi
            if kayit_yolu.exists():
                with open(kayit_yolu, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Yükleme hatası: {e}")
        return None

    def listele_kayitlar(self):
        try:
            kayitlar = []
            kayit_dir = self.get_save_dir()
            for dosya in kayit_dir.glob("*.json"):
                kayitlar.append(dosya.name)
            return sorted(kayitlar, reverse=True)
        except Exception as e:
            print(f"Listeleme hatası: {e}")
            return []

def convert_length(value, from_unit, to_unit="m"):
    if from_unit == to_unit:
        return value

    to_meter = {
        "mm": 0.001,
        "cm": 0.01,
        "inch": 0.0254,
        "m": 1.0
    }

    from_meter = {
        "mm": 1000.0,
        "cm": 100.0,
        "inch": 39.3701,
        "m": 1.0
    }

    try:
        if from_unit in to_meter and to_unit in from_meter:
            value_m = value * to_meter[from_unit]
            return value_m * from_meter[to_unit]
    except:
        pass
    return value

def convert_pressure(value, from_unit, to_unit="Pa"):
    if from_unit == to_unit:
        return value

    to_pascal = {
        "Pa": 1.0,
        "kPa": 1000.0,
        "bar": 100000.0,
        "atm": 101325.0,
        "mmH2O": 9.80665,
        "kg/cm2": 98066.5
    }

    from_pascal = {
        "Pa": 1.0,
        "kPa": 0.001,
        "bar": 0.00001,
        "atm": 0.00000986923,
        "mmH2O": 0.101971621,
        "kg/cm2": 0.0000101972
    }

    try:
        if from_unit in to_pascal and to_unit in from_pascal:
            value_pa = value * to_pascal[from_unit]
            return value_pa * from_pascal[to_unit]
    except:
        pass
    return value

def convert_temperature(value, from_unit, to_unit="K"):
    try:
        if from_unit == "K" and to_unit == "K":
            return value
        elif from_unit == "°C" and to_unit == "K":
            return value + 273.15
        elif from_unit == "°F" and to_unit == "K":
            return (value - 32) * 5/9 + 273.15
        elif from_unit == "K" and to_unit == "°C":
            return value - 273.15
        elif from_unit == "K" and to_unit == "°F":
            return (value - 273.15) * 9/5 + 32
        elif from_unit == "°C" and to_unit == "°F":
            return value * 9/5 + 32
        elif from_unit == "°F" and to_unit == "°C":
            return (value - 32) * 5/9
    except:
        pass
    return value

def excel_A1_hesapla(d):
    return 0.785 * (d ** 2)

def excel_A0_hesapla(D):
    return 0.785 * (D ** 2)

def excel_C_calc_hesapla(beta, Re, L1, L2, D):
    C_calc = (
        0.5959 +
        0.0312 * (beta ** 2.1) -
        0.184 * (beta ** 8) +
        0.0029 * (beta ** 2.5) * ((1e6 / Re) ** 0.75) +
        0.09 * (L1 / D) * ((beta ** 4) / (1 - beta ** 4)) -
        0.0337 * (L2 / D) * (beta ** 3)
    )
    return C_calc

def excel_Q_hesapla(C0, d, delta_p_pa, rho, beta):
    A1 = excel_A1_hesapla(d)
    Q = C0 * A1 * math.sqrt((2 * delta_p_pa) / (rho * (1 - beta ** 4)))
    return Q

def iteratif_C0_hesapla_excel(D_val, d_val, delta_p_pa, rho, mu, L1_val, L2_val, C0_baslangic_val, max_iter_val, epsilon_val):
    beta = d_val / D_val
    A0 = excel_A0_hesapla(D_val)
    A1 = excel_A1_hesapla(d_val)
    C0_current = C0_baslangic_val
    converged = False
    iter_count = 0
    Q_final = 0
    Re_final = 0
    v_final = 0
    C_calc_final = 0

    for i in range(max_iter_val):
        Q = excel_Q_hesapla(C0_current, d_val, delta_p_pa, rho, beta)
        v = Q / A0 if A0 > 0 else 0
        Re = (rho * v * D_val / mu) if mu > 0 else 1e6
        C_calc = excel_C_calc_hesapla(beta, Re, L1_val, L2_val, D_val)
        fark = C0_current - C_calc

        if abs(fark) < epsilon_val:
            converged = True
            iter_count = i + 1
            Q_final = Q
            Re_final = Re
            v_final = v
            C_calc_final = C_calc
            break

        C0_new = C0_current - (fark * 0.5)
        C0_new = max(0.1, min(1.0, C0_new))
        C0_current = C0_new
        iter_count = i + 1

        Q_final = Q
        Re_final = Re
        v_final = v
        C_calc_final = C_calc

    return C0_current, Q_final, Re_final, v_final, converged, iter_count, C_calc_final

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        self.orifis_kayit = OrifisHesap()
        self.current_values = {
            "D_m": VARSAYILAN_DEGERLER["D"],
            "d_m": VARSAYILAN_DEGERLER["d"],
            "L1": VARSAYILAN_DEGERLER["L1"],
            "L2": VARSAYILAN_DEGERLER["L2"],
            "C0_baslangic": VARSAYILAN_DEGERLER["C0_baslangic"],
            "delta_p": VARSAYILAN_DEGERLER["delta_p"],
            "p1_pa": VARSAYILAN_DEGERLER["p1"],
            "p2_pa": VARSAYILAN_DEGERLER["p2"],
            "sicaklik": VARSAYILAN_DEGERLER["sicaklik"],
            "gaz_tipi": VARSAYILAN_DEGERLER["gaz_tipi"],
            "yogunluk_manuel": VARSAYILAN_DEGERLER["yogunluk_manuel"],
            "viskozite_manuel": VARSAYILAN_DEGERLER["viskozite_manuel"],
            "yogunluk_atmosferik": VARSAYILAN_DEGERLER["yogunluk_atmosferik"],
            "viskozite_atmosferik": VARSAYILAN_DEGERLER["viskozite_atmosferik"],
            "max_iter": VARSAYILAN_DEGERLER["max_iter"],
            "epsilon": VARSAYILAN_DEGERLER["epsilon"],
            "basinc_mode": VARSAYILAN_DEGERLER["basinc_mode"],
            "yogunluk_mode": VARSAYILAN_DEGERLER["yogunluk_mode"],
            "viskozite_mode": VARSAYILAN_DEGERLER["viskozite_mode"],
            "d_birim": VARSAYILAN_DEGERLER["d_birim"],
            "D_birim": VARSAYILAN_DEGERLER["D_birim"],
            "basinc_birim": VARSAYILAN_DEGERLER["basinc_birim"],
            "sicaklik_birim": VARSAYILAN_DEGERLER["sicaklik_birim"]
        }
        self.basinc_mode_var = "ΔP Modu"
        self.yogunluk_mode_var = "Manuel"
        self.viskozite_mode_var = "Manuel"
        self.atmosferik_mode_var = False
        self.atmosferik_checked = False
        self.hesaplama_gecmisi = []
        self.anlik_hesap_data = None
        self.last_calculation_result = None
        self.current_anlik_popup = None
        
        # YENİ: Yazı boyutu ve yükseklik ayarları
        self.result_font_size = dp(13)  # Varsayılan yazı boyutu
        self.result_box_height = dp(1250)  # Varsayılan yükseklik
        self.anlik_result_font_size = dp(15)  # Anlık hesap için varsayılan
        
        self.setup_ui()
        self.setup_events()
        self.update_gaz_dropdown()
        self.calculate_beta()
        self.update_pressure_display()
        
        self.check_and_disable_atmosferic()

    def setup_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=0, spacing=0)
    
        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(6),
            bar_color=COLORS['scroll_dark'],
            bar_inactive_color=(0.5, 0.5, 0.5, 0.3),
            scroll_type=['bars', 'content'],
            effect_cls='ScrollEffect'
        )
    
        content = BoxLayout(orientation='vertical', spacing=dp(16), size_hint_y=None, padding=[dp(12), dp(12)])
        content.bind(minimum_height=content.setter('height'))
    
        # Header
        header = BoxLayout(orientation='vertical', padding=[dp(20), dp(20)],
                          size_hint_y=None, height=dp(80))
    
        with header.canvas.before:
            Color(*COLORS['bg_card'])
            header_bg = RoundedRectangle(pos=header.pos, size=header.size, radius=[dp(11)])
            Color(*COLORS['primary_blue'])
            header_top = Rectangle(pos=(header.x, header.y + header.height - dp(3)),
                                  size=(header.width, dp(3)))
            Color(*COLORS['border_dark'])
            header_border = Line(
                rounded_rectangle=(header.x, header.y, header.width, header.height, dp(11)),
                width=1
            )
    
        def update_header_graphics(instance, value):
            header_bg.pos = header.pos
            header_bg.size = header.size
            header_top.pos = (header.x, header.y + header.height - dp(3))
            header_top.size = (header.width, dp(3))
            header_border.rounded_rectangle = (header.x, header.y, header.width, header.height, dp(11))
    
        header.bind(pos=update_header_graphics, size=update_header_graphics)
    
        title = Label(
            text='⚡ ORİFİS DEBİ HESAPLAYICI',
            font_size=dp(21),
            bold=True,
            color=COLORS['primary_blue'],
            size_hint_y=None,
            height=dp(32),
            halign='center',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
    
        subtitle = Label(
            text='v9.8 • Modern UI • Designed by Lutfi',
            font_size=dp(9),
            color=COLORS['text_gray'],
            italic=True,
            size_hint_y=None,
            height=dp(20),
            halign='center',
            valign='middle'
        )
        subtitle.bind(size=subtitle.setter('text_size'))
    
        header.add_widget(title)
        header.add_widget(subtitle)
        content.add_widget(header)
    
        # Geometrik Ölçüler
        geo_card = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(6),
                            size_hint_y=None, height=dp(224))
    
        with geo_card.canvas.before:
            Color(*COLORS['bg_card'])
            geo_bg = RoundedRectangle(pos=geo_card.pos, size=geo_card.size, radius=[dp(8)])
            Color(*COLORS['border_dark'])
            geo_border = Line(
                rounded_rectangle=(geo_card.x, geo_card.y, geo_card.width, geo_card.height, dp(8)),
                width=1
            )
    
        def update_geo_graphics(instance, value):
            geo_bg.pos = geo_card.pos
            geo_bg.size = geo_card.size
            geo_border.rounded_rectangle = (geo_card.x, geo_card.y, geo_card.width, geo_card.height, dp(8))
    
        geo_card.bind(pos=update_geo_graphics, size=update_geo_graphics)
    
        geo_title = Label(
            text='📏 GEOMETRİK ÖLÇÜLER',
            font_size=dp(11),
            bold=True,
            color=COLORS['text_white'],
            size_hint_y=None,
            height=dp(22),
            halign='left',
            valign='middle'
        )
        geo_title.bind(size=geo_title.setter('text_size'))
    
        with geo_title.canvas.after:
            Color(*COLORS['success_green'])
            geo_underline = Line(points=[], width=2)
    
        def update_geo_underline(instance, value):
            geo_underline.points = [
                geo_title.x, geo_title.y,
                geo_title.x + geo_title.width, geo_title.y
            ]
    
        geo_title.bind(size=update_geo_underline, pos=update_geo_underline)
    
        geo_card.add_widget(geo_title)
    
        # D satırı
        D_row = BoxLayout(orientation='horizontal', spacing=dp(10),
                         size_hint_y=None, height=dp(32))
    
        D_label = Label(text='D:', size_hint_x=0.2, font_size=dp(10),
                       color=COLORS['text_gray'], halign='left', bold=True)
        D_label.bind(size=D_label.setter('text_size'))
    
        self.D_input = CompactTextInput(
            hint_text="0.207300",
            text=f"{VARSAYILAN_DEGERLER['D']:.4f}",
            size_hint_x=0.5
        )
    
        self.D_birim = CompactSpinner(
            text='m',
            values=('m', 'mm', 'cm', 'inch'),
            size_hint_x=0.3
        )
    
        D_row.add_widget(D_label)
        D_row.add_widget(self.D_input)
        D_row.add_widget(self.D_birim)
        geo_card.add_widget(D_row)
    
        # d satırı
        d_row = BoxLayout(orientation='horizontal', spacing=dp(10),
                         size_hint_y=None, height=dp(32))
    
        d_label = Label(text='d:', size_hint_x=0.2, font_size=dp(10),
                       color=COLORS['text_gray'], halign='left', bold=True)
        d_label.bind(size=d_label.setter('text_size'))
    
        self.d_input = CompactTextInput(
            hint_text="0.128227",
            text=f"{VARSAYILAN_DEGERLER['d']:.4f}",
            size_hint_x=0.5
        )
    
        self.d_birim = CompactSpinner(
            text='m',
            values=('m', 'mm', 'cm', 'inch'),
            size_hint_x=0.3
        )
    
        d_row.add_widget(d_label)
        d_row.add_widget(self.d_input)
        d_row.add_widget(self.d_birim)
        geo_card.add_widget(d_row)
    
        # L1, L2, C0 satırı
        l_grid = GridLayout(cols=3, spacing=dp(10), size_hint_y=None, height=dp(52))
    
        # L1
        l1_box = BoxLayout(orientation='vertical', spacing=dp(5))
        l1_label = Label(text='L1:', font_size=dp(9), color=COLORS['text_gray'],
                        size_hint_y=None, height=dp(13), halign='center', bold=True)
        l1_label.bind(size=l1_label.setter('text_size'))
        self.L1_input = CompactTextInput(
            hint_text="0.03",
            text=str(VARSAYILAN_DEGERLER['L1']),
            halign='center'
        )
        l1_box.add_widget(l1_label)
        l1_box.add_widget(self.L1_input)
    
        # L2
        l2_box = BoxLayout(orientation='vertical', spacing=dp(5))
        l2_label = Label(text='L2:', font_size=dp(9), color=COLORS['text_gray'],
                        size_hint_y=None, height=dp(13), halign='center', bold=True)
        l2_label.bind(size=l2_label.setter('text_size'))
        self.L2_input = CompactTextInput(
            hint_text="0.03",
            text=str(VARSAYILAN_DEGERLER['L2']),
            halign='center'
        )
        l2_box.add_widget(l2_label)
        l2_box.add_widget(self.L2_input)
    
        # C0
        c0_box = BoxLayout(orientation='vertical', spacing=dp(5))
        c0_label = Label(text='C0:', font_size=dp(9), color=COLORS['text_gray'],
                        size_hint_y=None, height=dp(13), halign='center', bold=True)
        c0_label.bind(size=c0_label.setter('text_size'))
        self.C0_input = CompactTextInput(
            hint_text="1e-09",
            text=str(VARSAYILAN_DEGERLER['C0_baslangic']),
            halign='center'
        )
        c0_box.add_widget(c0_label)
        c0_box.add_widget(self.C0_input)
    
        l_grid.add_widget(l1_box)
        l_grid.add_widget(l2_box)
        l_grid.add_widget(c0_box)
        geo_card.add_widget(l_grid)
    
        # Beta display
        beta_display = BoxLayout(orientation='vertical', padding=dp(10),
                                size_hint_y=None, height=dp(38))
    
        with beta_display.canvas.before:
            Color(*COLORS['success_green_dark'])
            beta_bg = RoundedRectangle(pos=beta_display.pos, size=beta_display.size, radius=[dp(5)])
            Color(*COLORS['success_green'])
            beta_border = Line(
                rounded_rectangle=(beta_display.x, beta_display.y, beta_display.width, beta_display.height, dp(5)),
                width=1
            )
    
        self.beta_label = Label(
            text='β = Hesaplanacak',
            font_size=dp(13),
            bold=True,
            color=COLORS['success_light'],
            halign='center',
            valign='middle'
        )
        self.beta_label.bind(size=self.beta_label.setter('text_size'))
    
        def update_beta_graphics(instance, value):
            beta_bg.pos = beta_display.pos
            beta_bg.size = beta_display.size
            beta_border.rounded_rectangle = (beta_display.x, beta_display.y, beta_display.width, beta_display.height, dp(5))
    
        beta_display.bind(pos=update_beta_graphics, size=update_beta_graphics)
        beta_display.add_widget(self.beta_label)
        geo_card.add_widget(beta_display)
    
        content.add_widget(geo_card)
    
        # Basınç Değerleri
        pressure_card = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(6),
                                 size_hint_y=None, height=dp(224))
    
        with pressure_card.canvas.before:
            Color(*COLORS['bg_card'])
            pressure_bg = RoundedRectangle(pos=pressure_card.pos, size=pressure_card.size, radius=[dp(8)])
            Color(*COLORS['border_dark'])
            pressure_border = Line(
                rounded_rectangle=(pressure_card.x, pressure_card.y, pressure_card.width, pressure_card.height, dp(8)),
                width=1
            )
    
        def update_pressure_graphics(instance, value):
            pressure_bg.pos = pressure_card.pos
            pressure_bg.size = pressure_card.size
            pressure_border.rounded_rectangle = (pressure_card.x, pressure_card.y, pressure_card.width, pressure_card.height, dp(8))
    
        pressure_card.bind(pos=update_pressure_graphics, size=update_pressure_graphics)
    
        pressure_title = Label(
            text='📊 BASINÇ DEĞERLERİ',
            font_size=dp(11),
            bold=True,
            color=COLORS['text_white'],
            size_hint_y=None,
            height=dp(22),
            halign='left',
            valign='middle'
        )
        pressure_title.bind(size=pressure_title.setter('text_size'))
    
        with pressure_title.canvas.after:
            Color(*COLORS['success_green'])
            pressure_underline = Line(points=[], width=2)
    
        def update_pressure_underline(instance, value):
            pressure_underline.points = [
                pressure_title.x, pressure_title.y,
                pressure_title.x + pressure_title.width, pressure_title.y
            ]
    
        pressure_title.bind(size=update_pressure_underline, pos=update_pressure_underline)
    
        pressure_card.add_widget(pressure_title)
    
        # Basınç modu toggle
        pressure_mode_group = BoxLayout(orientation='horizontal', spacing=0,
                                      size_hint_y=None, height=dp(32))
    
        with pressure_mode_group.canvas.before:
            Color(*COLORS['border_dark'])
            mode_border = Line(
                rounded_rectangle=(pressure_mode_group.x, pressure_mode_group.y, pressure_mode_group.width, pressure_mode_group.height, dp(5)),
                width=1
            )
    
        def update_mode_border(instance, value):
            mode_border.rounded_rectangle = (pressure_mode_group.x, pressure_mode_group.y, pressure_mode_group.width, pressure_mode_group.height, dp(5))
    
        pressure_mode_group.bind(pos=update_mode_border, size=update_mode_border)
    
        self.delta_p_btn = Button(
            text='ΔP Modu',
            font_size=dp(9),
            bold=True,
            background_normal='',
            background_down='',
            background_color=COLORS['primary_blue_dark'],
            color=(1, 1, 1, 1)
        )
        self.delta_p_btn.bind(on_press=lambda x: self.on_pressure_mode_change('ΔP Modu'))
    
        self.gc_btn = Button(
            text='G/Ç Modu',
            font_size=dp(9),
            bold=False,
            background_normal='',
            background_down='',
            background_color=COLORS['disabled_gray'],
            color=COLORS['text_gray']
        )
        self.gc_btn.bind(on_press=lambda x: self.on_pressure_mode_change('G/Ç Modu'))
    
        pressure_mode_group.add_widget(self.delta_p_btn)
        pressure_mode_group.add_widget(self.gc_btn)
        pressure_card.add_widget(pressure_mode_group)
    
        # ΔP satırı
        delta_p_row = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(32))
        delta_p_label = Label(text='ΔP:', size_hint_x=0.2, font_size=dp(10),
                             color=COLORS['text_gray'], halign='left', bold=True)
        delta_p_label.bind(size=delta_p_label.setter('text_size'))
    
        self.delta_p_input = CompactTextInput(
            hint_text="729.0000",
            text=f"{VARSAYILAN_DEGERLER['delta_p']:.2f}",
            size_hint_x=0.6
        )
    
        delta_p_unit = Label(text='mmH₂O', size_hint_x=0.2, font_size=dp(10),
                           color=COLORS['primary_blue'], halign='center', bold=True)
        delta_p_unit.bind(size=delta_p_unit.setter('text_size'))
    
        delta_p_row.add_widget(delta_p_label)
        delta_p_row.add_widget(self.delta_p_input)
        delta_p_row.add_widget(delta_p_unit)
        pressure_card.add_widget(delta_p_row)
    
        # p1 satırı
        p1_row = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(32))
        p1_label = Label(text='p1:', size_hint_x=0.2, font_size=dp(10),
                        color=COLORS['text_gray'], halign='left', bold=True)
        p1_label.bind(size=p1_label.setter('text_size'))
    
        self.p1_input = CompactTextInput(
            hint_text="285471.0000",
            text=f"{VARSAYILAN_DEGERLER['p1']:.2f}",
            size_hint_x=0.5
        )
    
        self.pressure_unit = CompactSpinner(
            text='Pa',
            values=('Pa', 'kPa', 'bar', 'atm', 'mmH2O', 'kg/cm2'),
            size_hint_x=0.3
        )
    
        p1_row.add_widget(p1_label)
        p1_row.add_widget(self.p1_input)
        p1_row.add_widget(self.pressure_unit)
        pressure_card.add_widget(p1_row)
    
        # p2 satırı
        p2_row = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(32))
        p2_label = Label(text='p2:', size_hint_x=0.2, font_size=dp(10),
                        color=COLORS['text_gray'], halign='left', bold=True)
        p2_label.bind(size=p2_label.setter('text_size'))
    
        self.p2_input = CompactTextInput(
            hint_text="278321.9522",
            text=f"{VARSAYILAN_DEGERLER['p2']:.2f}",
            size_hint_x=0.6,
            disabled=True
        )
        self.p2_input.background_color = COLORS['disabled_gray']
    
        p2_unit = Label(text='Pa', size_hint_x=0.2, font_size=dp(10),
                       color=COLORS['primary_blue'], halign='center', bold=True)
        p2_unit.bind(size=p2_unit.setter('text_size'))
    
        p2_row.add_widget(p2_label)
        p2_row.add_widget(self.p2_input)
        p2_row.add_widget(p2_unit)
        pressure_card.add_widget(p2_row)
    
        # p2 status
        self.p2_status = Label(
            text='(Çıkış basıncı otomatik hesaplanacak)',
            size_hint_y=None,
            height=dp(16),
            font_size=dp(8),
            color=COLORS['text_gray'],
            italic=True,
            halign='left'
        )
        self.p2_status.bind(size=self.p2_status.setter('text_size'))
        pressure_card.add_widget(self.p2_status)
    
        content.add_widget(pressure_card)
    
        # Akışkan Özellikleri
        fluid_card = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(6),
                              size_hint_y=None, height=dp(438))
    
        with fluid_card.canvas.before:
            Color(*COLORS['bg_card'])
            fluid_bg = RoundedRectangle(pos=fluid_card.pos, size=fluid_card.size, radius=[dp(8)])
            Color(*COLORS['border_dark'])
            fluid_border = Line(
                rounded_rectangle=(fluid_card.x, fluid_card.y, fluid_card.width, fluid_card.height, dp(8)),
                width=1
            )
    
        def update_fluid_graphics(instance, value):
            fluid_bg.pos = fluid_card.pos
            fluid_bg.size = fluid_card.size
            fluid_border.rounded_rectangle = (fluid_card.x, fluid_card.y, fluid_card.width, fluid_card.height, dp(8))
    
        fluid_card.bind(pos=update_fluid_graphics, size=update_fluid_graphics)
    
        fluid_title = Label(
            text='🌡️ AKIŞKAN ÖZELLİKLERİ',
            font_size=dp(11),
            bold=True,
            color=COLORS['text_white'],
            size_hint_y=None,
            height=dp(22),
            halign='left',
            valign='middle'
        )
        fluid_title.bind(size=fluid_title.setter('text_size'))
    
        with fluid_title.canvas.after:
            Color(*COLORS['success_green'])
            fluid_underline = Line(points=[], width=2)
    
        def update_fluid_underline(instance, value):
            fluid_underline.points = [
                fluid_title.x, fluid_title.y,
                fluid_title.x + fluid_title.width, fluid_title.y
            ]
    
        fluid_title.bind(size=update_fluid_underline, pos=update_fluid_underline)
    
        fluid_card.add_widget(fluid_title)
    
        # Gaz seçimi
        gas_row = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(32))
        gas_label = Label(text='Akışkan:', size_hint_x=0.25, font_size=dp(10),
                         color=COLORS['text_gray'], halign='left', bold=True)
        gas_label.bind(size=gas_label.setter('text_size'))
    
        all_gases = {**GAZLAR, **self.orifis_kayit.custom_gazlar}
        self.gaz_spinner = CompactSpinner(
            text=VARSAYILAN_DEGERLER['gaz_tipi'],
            values=list(all_gases.keys()),
            size_hint_x=0.75
        )
    
        gas_row.add_widget(gas_label)
        gas_row.add_widget(self.gaz_spinner)
        fluid_card.add_widget(gas_row)
    
        # Sıcaklık
        temp_row = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(32))
        temp_label = Label(text='Sıcaklık:', size_hint_x=0.25, font_size=dp(10),
                          color=COLORS['text_gray'], halign='left', bold=True)
        temp_label.bind(size=temp_label.setter('text_size'))
    
        self.temp_input = CompactTextInput(
            hint_text="293.15",
            text=f"{VARSAYILAN_DEGERLER['sicaklik']:.2f}",
            size_hint_x=0.5
        )
    
        self.temp_unit = CompactSpinner(
            text='K',
            values=('K', '°C', '°F'),
            size_hint_x=0.25
        )
    
        temp_row.add_widget(temp_label)
        temp_row.add_widget(self.temp_input)
        temp_row.add_widget(self.temp_unit)
        fluid_card.add_widget(temp_row)
    
        # Atmosferik checkbox
        atmosferik_box = BoxLayout(orientation='horizontal', spacing=dp(8),
                                  size_hint_y=None, height=dp(19))
    
        self.atmosferik_check = CheckBox(
            size_hint=(None, None),
            size=(dp(19), dp(19)),
            active=False
        )
        
        self.atmosferik_check.color = COLORS['success_green']
        self.atmosferik_check.background_color = COLORS['input_bg']
        self.atmosferik_check.bind(active=self.on_atmosferik_check)
    
        atmosferik_label = Label(
            text="Atmosferik (T=0°C, P=1 atm)",
            font_size=dp(9),
            color=COLORS['text_gray'],
            size_hint_x=1,
            halign='left',
            valign='middle'
        )
        atmosferik_label.bind(size=atmosferik_label.setter('text_size'))
    
        atmosferik_box.add_widget(self.atmosferik_check)
        atmosferik_box.add_widget(atmosferik_label)
    
        fluid_card.add_widget(atmosferik_box)
    
        # Yoğunluk modu
        density_title = Label(
            text='Yoğunluk Modu:',
            size_hint_y=None,
            height=dp(19),
            color=COLORS['text_white'],
            halign='left',
            font_size=dp(9)
        )
        density_title.bind(size=density_title.setter('text_size'))
        fluid_card.add_widget(density_title)
    
        yogunluk_mode_group = BoxLayout(orientation='horizontal', spacing=dp(10),
                                      size_hint_y=None, height=dp(32))
    
        self.yogunluk_otomatik_btn = Button(
            text='Otomatik',
            font_size=dp(9),
            bold=False,
            background_normal='',
            background_down='',
            background_color=COLORS['disabled_gray'],
            color=COLORS['text_gray']
        )
        self.yogunluk_otomatik_btn.bind(on_press=lambda x: self.on_yogunluk_mode_change('Otomatik'))
    
        self.yogunluk_manuel_btn = Button(
            text='Manuel',
            font_size=dp(9),
            bold=True,
            background_normal='',
            background_down='',
            background_color=COLORS['primary_blue_dark'],
            color=(1, 1, 1, 1)
        )
        self.yogunluk_manuel_btn.bind(on_press=lambda x: self.on_yogunluk_mode_change('Manuel'))
    
        self.yogunluk_atmosferik_btn = Button(
            text='Atmosferik',
            font_size=dp(9),
            bold=False,
            background_normal='',
            background_down='',
            background_color=COLORS['disabled_gray'],
            color=COLORS['text_gray']
        )
        self.yogunluk_atmosferik_btn.bind(on_press=lambda x: self.on_yogunluk_mode_change('Atmosferik'))
    
        yogunluk_mode_group.add_widget(self.yogunluk_otomatik_btn)
        yogunluk_mode_group.add_widget(self.yogunluk_manuel_btn)
        yogunluk_mode_group.add_widget(self.yogunluk_atmosferik_btn)
        fluid_card.add_widget(yogunluk_mode_group)
    
        # Yoğunluk değerleri
        density_row = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(32))
        density_label = Label(text='Yoğunluk:', size_hint_x=0.25, font_size=dp(10),
                             color=COLORS['text_gray'], halign='left', bold=True)
        density_label.bind(size=density_label.setter('text_size'))
    
        self.density_input = CompactTextInput(
            hint_text="0.771",
            text=str(VARSAYILAN_DEGERLER["yogunluk_manuel"]),
            size_hint_x=0.6
        )
    
        density_unit = Label(text='kg/m³', size_hint_x=0.15, font_size=dp(10),
                           color=COLORS['primary_blue'], halign='center', bold=True)
        density_unit.bind(size=density_unit.setter('text_size'))
    
        density_row.add_widget(density_label)
        density_row.add_widget(self.density_input)
        density_row.add_widget(density_unit)
        fluid_card.add_widget(density_row)
    
        # Atmosferik yoğunluk
        atmo_density_row = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(32))
        atmo_density_label = Label(text='Atmosferik:', size_hint_x=0.25, font_size=dp(10),
                                  color=COLORS['text_gray'], halign='left', bold=True)
        atmo_density_label.bind(size=atmo_density_label.setter('text_size'))
    
        self.density_atmosferik = CompactTextInput(
            hint_text="0.771",
            text=str(VARSAYILAN_DEGERLER["yogunluk_atmosferik"]),
            size_hint_x=0.6,
            disabled=True
        )
        self.density_atmosferik.background_color = COLORS['disabled_gray']
    
        atmo_density_unit = Label(text='kg/m³', size_hint_x=0.15, font_size=dp(10),
                                 color=COLORS['primary_blue'], halign='center', bold=True)
        atmo_density_unit.bind(size=atmo_density_unit.setter('text_size'))
    
        atmo_density_row.add_widget(atmo_density_label)
        atmo_density_row.add_widget(self.density_atmosferik)
        atmo_density_row.add_widget(atmo_density_unit)
        fluid_card.add_widget(atmo_density_row)
    
        # Viskozite modu
        viscosity_title = Label(
            text='Viskozite Modu:',
            size_hint_y=None,
            height=dp(19),
            color=COLORS['text_white'],
            halign='left',
            font_size=dp(9)
        )
        viscosity_title.bind(size=viscosity_title.setter('text_size'))
        fluid_card.add_widget(viscosity_title)
    
        viskozite_mode_group = BoxLayout(orientation='horizontal', spacing=dp(10),
                                        size_hint_y=None, height=dp(32))
    
        self.viskozite_otomatik_btn = Button(
            text='Otomatik',
            font_size=dp(9),
            bold=False,
            background_normal='',
            background_down='',
            background_color=COLORS['disabled_gray'],
            color=COLORS['text_gray']
        )
        self.viskozite_otomatik_btn.bind(on_press=lambda x: self.on_viskozite_mode_change('Otomatik'))
    
        self.viskozite_manuel_btn = Button(
            text='Manuel',
            font_size=dp(9),
            bold=True,
            background_normal='',
            background_down='',
            background_color=COLORS['primary_blue_dark'],
            color=(1, 1, 1, 1)
        )
        self.viskozite_manuel_btn.bind(on_press=lambda x: self.on_viskozite_mode_change('Manuel'))
    
        self.viskozite_atmosferik_btn = Button(
            text='Atmosferik',
            font_size=dp(9),
            bold=False,
            background_normal='',
            background_down='',
            background_color=COLORS['disabled_gray'],
            color=COLORS['text_gray']
        )
        self.viskozite_atmosferik_btn.bind(on_press=lambda x: self.on_viskozite_mode_change('Atmosferik'))
    
        viskozite_mode_group.add_widget(self.viskozite_otomatik_btn)
        viskozite_mode_group.add_widget(self.viskozite_manuel_btn)
        viskozite_mode_group.add_widget(self.viskozite_atmosferik_btn)
        fluid_card.add_widget(viskozite_mode_group)
    
        # Viskozite değerleri
        viscosity_row = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(32))
        viscosity_label = Label(text='Viskozite:', size_hint_x=0.25, font_size=dp(10),
                               color=COLORS['text_gray'], halign='left', bold=True)
        viscosity_label.bind(size=viscosity_label.setter('text_size'))
    
        self.viscosity_input = CompactTextInput(
            hint_text="1.16e-05",
            text=str(VARSAYILAN_DEGERLER["viskozite_manuel"]),
            size_hint_x=0.6
        )
    
        viscosity_unit = Label(text='Pa·s', size_hint_x=0.15, font_size=dp(10),
                             color=COLORS['primary_blue'], halign='center', bold=True)
        viscosity_unit.bind(size=viscosity_unit.setter('text_size'))
    
        viscosity_row.add_widget(viscosity_label)
        viscosity_row.add_widget(self.viscosity_input)
        viscosity_row.add_widget(viscosity_unit)
        fluid_card.add_widget(viscosity_row)
    
        # Atmosferik viskozite
        atmo_viscosity_row = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(32))
        atmo_viscosity_label = Label(text='Atmosferik:', size_hint_x=0.25, font_size=dp(10),
                                    color=COLORS['text_gray'], halign='left', bold=True)
        atmo_viscosity_label.bind(size=atmo_viscosity_label.setter('text_size'))
    
        self.viscosity_atmosferik = CompactTextInput(
            hint_text="1.16e-05",
            text=str(VARSAYILAN_DEGERLER["viskozite_atmosferik"]),
            size_hint_x=0.6,
            disabled=True
        )
        self.viscosity_atmosferik.background_color = COLORS['disabled_gray']
    
        atmo_viscosity_unit = Label(text='Pa·s', size_hint_x=0.15, font_size=dp(10),
                                   color=COLORS['primary_blue'], halign='center', bold=True)
        atmo_viscosity_unit.bind(size=atmo_viscosity_unit.setter('text_size'))
    
        atmo_viscosity_row.add_widget(atmo_viscosity_label)
        atmo_viscosity_row.add_widget(self.viscosity_atmosferik)
        atmo_viscosity_row.add_widget(atmo_viscosity_unit)
        fluid_card.add_widget(atmo_viscosity_row)
    
        content.add_widget(fluid_card)
    
        # İleri Ayarlar
        advanced_card = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(6),
                                 size_hint_y=None, height=dp(106))
    
        with advanced_card.canvas.before:
            Color(*COLORS['bg_card'])
            advanced_bg = RoundedRectangle(pos=advanced_card.pos, size=advanced_card.size, radius=[dp(8)])
            Color(*COLORS['border_dark'])
            advanced_border = Line(
                rounded_rectangle=(advanced_card.x, advanced_card.y, advanced_card.width, advanced_card.height, dp(8)),
                width=1
            )
    
        def update_advanced_graphics(instance, value):
            advanced_bg.pos = advanced_card.pos
            advanced_bg.size = advanced_card.size
            advanced_border.rounded_rectangle = (advanced_card.x, advanced_card.y, advanced_card.width, advanced_card.height, dp(8))
    
        advanced_card.bind(pos=update_advanced_graphics, size=update_advanced_graphics)
    
        advanced_title = Label(
            text='⚙️ İLERİ AYARLAR',
            font_size=dp(11),
            bold=True,
            color=COLORS['text_white'],
            size_hint_y=None,
            height=dp(22),
            halign='left',
            valign='middle'
        )
        advanced_title.bind(size=advanced_title.setter('text_size'))
    
        with advanced_title.canvas.after:
            Color(*COLORS['success_green'])
            advanced_underline = Line(points=[], width=2)
    
        def update_advanced_underline(instance, value):
            advanced_underline.points = [
                advanced_title.x, advanced_title.y,
                advanced_title.x + advanced_title.width, advanced_title.y
            ]
    
        advanced_title.bind(size=update_advanced_underline, pos=update_advanced_underline)
    
        advanced_card.add_widget(advanced_title)
    
        advanced_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(52))
    
        # Max İterasyon
        max_iter_box = BoxLayout(orientation='vertical', spacing=dp(5))
        max_iter_label = Label(
            text='Max İterasyon:',
            font_size=dp(9),
            color=COLORS['text_gray'],
            size_hint_y=None,
            height=dp(16),
            halign='center',
            bold=True
        )
        max_iter_label.bind(size=max_iter_label.setter('text_size'))
        self.max_iter_input = CompactTextInput(
            hint_text="100",
            text=str(VARSAYILAN_DEGERLER["max_iter"]),
            halign='center'
        )
        max_iter_box.add_widget(max_iter_label)
        max_iter_box.add_widget(self.max_iter_input)
    
        # Hassasiyet
        epsilon_box = BoxLayout(orientation='vertical', spacing=dp(5))
        epsilon_label = Label(
            text='Hassasiyet (ε):',
            font_size=dp(9),
            color=COLORS['text_gray'],
            size_hint_y=None,
            height=dp(16),
            halign='center',
            bold=True
        )
        epsilon_label.bind(size=epsilon_label.setter('text_size'))
        self.epsilon_input = CompactTextInput(
            hint_text="0.000001",
            text=str(VARSAYILAN_DEGERLER["epsilon"]),
            halign='center'
        )
        epsilon_box.add_widget(epsilon_label)
        epsilon_box.add_widget(self.epsilon_input)
    
        advanced_grid.add_widget(max_iter_box)
        advanced_grid.add_widget(epsilon_box)
        advanced_card.add_widget(advanced_grid)
    
        content.add_widget(advanced_card)
    
        # Hesapla Butonu
        self.calc_btn = CompactButton(
            "HESAPLA",
            color_type="primary",
            icon="🚀",
            size_hint_y=None,
            height=dp(36)
        )
        self.calc_btn.bind(on_press=self.hesapla)
        content.add_widget(self.calc_btn)
    
        # ========== BUTON SATIRLARI - YAZI BOYUTU AYARLARININ ÜSTÜNE ==========
        btn_row1 = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(36))
        self.save_btn = CompactButton("KAYDET", color_type="secondary", icon="💾")
        self.save_btn.disabled = True
        self.save_btn.opacity = 0.5
    
        self.load_btn = CompactButton("YÜKLE", color_type="warning", icon="📂")
        self.clear_btn = CompactButton("TEMİZLE", color_type="danger", icon="🧹")
    
        btn_row1.add_widget(self.save_btn)
        btn_row1.add_widget(self.load_btn)
        btn_row1.add_widget(self.clear_btn)
        content.add_widget(btn_row1)
    
        btn_row2 = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(36))
        self.default_btn = CompactButton("VARS.", color_type="purple", icon="🔄")
        self.help_btn = CompactButton("YARDIM", color_type="secondary", icon="❓")
        self.add_gas_btn = CompactButton("AKIŞKAN", color_type="primary", icon="➕")
    
        btn_row2.add_widget(self.default_btn)
        btn_row2.add_widget(self.help_btn)
        btn_row2.add_widget(self.add_gas_btn)
        content.add_widget(btn_row2)
    
        # Anlık Hesap Butonu - TEK SATIRDA
        anlik_btn_row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(36))
        self.anlik_hesap_btn = CompactButton(
            "ANLIK HESAP",
            color_type="warning",
            icon="⚡",
            size_hint_x=1
        )
        self.anlik_hesap_btn.disabled = True
        self.anlik_hesap_btn.opacity = 0.5
        self.anlik_hesap_btn.bind(on_press=self.show_anlik_hesap_popup)
        anlik_btn_row.add_widget(self.anlik_hesap_btn)
        content.add_widget(anlik_btn_row)
    
        # YAZI BOYUTU VE YÜKSEKLİK AYARLARI KONTROL PANELİ - BUTONLARDAN SONRA
        control_card = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8),
                               size_hint_y=None, height=dp(100))
        
        with control_card.canvas.before:
            Color(*COLORS['bg_card'])
            control_bg = RoundedRectangle(pos=control_card.pos, size=control_card.size, radius=[dp(8)])
            Color(*COLORS['border_dark'])
            control_border = Line(
                rounded_rectangle=(control_card.x, control_card.y, control_card.width, control_card.height, dp(8)),
                width=1
            )
        
        def update_control_graphics(instance, value):
            control_bg.pos = control_card.pos
            control_bg.size = control_card.size
            control_border.rounded_rectangle = (control_card.x, control_card.y, control_card.width, control_card.height, dp(8))
        
        control_card.bind(pos=update_control_graphics, size=update_control_graphics)
        
        control_title = Label(
            text='🎛️ YAZI BOYUTU ve YÜKSEKLİK AYARLARI',
            font_size=dp(11),
            bold=True,
            color=COLORS['text_white'],
            size_hint_y=None,
            height=dp(24),
            halign='left',
            valign='middle'
        )
        control_title.bind(size=control_title.setter('text_size'))
        
        with control_title.canvas.after:
            Color(*COLORS['purple'])
            control_underline = Line(points=[], width=2)
        
        def update_control_underline(instance, value):
            control_underline.points = [
                control_title.x, control_title.y,
                control_title.x + control_title.width, control_title.y
            ]
        
        control_title.bind(size=update_control_underline, pos=update_control_underline)
        control_card.add_widget(control_title)
        
        # Yazı Boyutu Slider
        font_size_row = BoxLayout(orientation='horizontal', spacing=dp(10),
                                 size_hint_y=None, height=dp(30))
        
        font_size_label = Label(
            text='Yazı Boyutu:',
            size_hint_x=0.35,
            font_size=dp(10),
            color=COLORS['text_gray'],
            halign='left',
            bold=True
        )
        font_size_label.bind(size=font_size_label.setter('text_size'))
        
        self.font_size_slider = Slider(
            min=8,
            max=20,
            value=13,  # Varsayılan 13 dp
            size_hint_x=0.5
        )
        self.font_size_slider.bind(value=self.on_font_size_change)
        
        self.font_size_value = Label(
            text=f'{13:.0f} dp',  # Başlangıç değeri 13
            size_hint_x=0.15,
            font_size=dp(10),
            color=COLORS['primary_blue'],
            halign='center',
            bold=True
        )
        self.font_size_value.bind(size=self.font_size_value.setter('text_size'))
        
        font_size_row.add_widget(font_size_label)
        font_size_row.add_widget(self.font_size_slider)
        font_size_row.add_widget(self.font_size_value)
        control_card.add_widget(font_size_row)
        
        # Kutu Yüksekliği Slider
        box_height_row = BoxLayout(orientation='horizontal', spacing=dp(10),
                                  size_hint_y=None, height=dp(30))
        
        box_height_label = Label(
            text='Kutu Yüksekliği:',
            size_hint_x=0.35,
            font_size=dp(10),
            color=COLORS['text_gray'],
            halign='left',
            bold=True
        )
        box_height_label.bind(size=box_height_label.setter('text_size'))
        
        self.box_height_slider = Slider(
            min=400,
            max=1500,
            value=1250,  # Varsayılan 1250 dp
            size_hint_x=0.5
        )
        self.box_height_slider.bind(value=self.on_box_height_change)
        
        self.box_height_value = Label(
            text=f'{1250:.0f} dp',  # Başlangıç değeri 1250
            size_hint_x=0.15,
            font_size=dp(10),
            color=COLORS['primary_blue'],
            halign='center',
            bold=True
        )
        self.box_height_value.bind(size=self.box_height_value.setter('text_size'))
        
        box_height_row.add_widget(box_height_label)
        box_height_row.add_widget(self.box_height_slider)
        box_height_row.add_widget(self.box_height_value)
        control_card.add_widget(box_height_row)
        
        content.add_widget(control_card)
    
        # HESAPLAMA SONUÇLARI - YAZI BOYUTU AYARLARINDAN SONRA, DAHA GENİŞ
        results_card = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(6),
                                size_hint_y=None, height=dp(1250))
    
        with results_card.canvas.before:
            Color(*COLORS['bg_card'])
            results_bg = RoundedRectangle(pos=results_card.pos, size=results_card.size, radius=[dp(8)])
            Color(*COLORS['border_dark'])
            results_border = Line(
                rounded_rectangle=(results_card.x, results_card.y, results_card.width, results_card.height, dp(8)),
                width=1
            )
    
        def update_results_graphics(instance, value):
            results_bg.pos = results_card.pos
            results_bg.size = results_card.size
            results_border.rounded_rectangle = (results_card.x, results_card.y, results_card.width, results_card.height, dp(8))
    
        results_card.bind(pos=update_results_graphics, size=update_results_graphics)
    
        results_title = Label(
            text='📋 HESAPLAMA SONUÇLARI',
            font_size=dp(11),
            bold=True,
            color=COLORS['text_white'],
            size_hint_y=None,
            height=dp(22),
            halign='left',
            valign='middle'
        )
        results_title.bind(size=results_title.setter('text_size'))
    
        with results_title.canvas.after:
            Color(*COLORS['success_green'])
            results_underline = Line(points=[], width=2)
    
        def update_results_underline(instance, value):
            results_underline.points = [
                results_title.x, results_title.y,
                results_title.x + results_title.width, results_title.y
            ]
    
        results_title.bind(size=update_results_underline, pos=update_results_underline)
    
        results_card.add_widget(results_title)
    
        # Sonuç alanı - SCROLLVIEW DÜZELTMESİ
        results_scroll = ScrollView(
            size_hint=(1, 1),
            bar_width=dp(8),  # Scroll bar kalınlığı
            bar_color=COLORS['scroll_dark'],
            bar_inactive_color=(0.5, 0.5, 0.5, 0.3),
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content']
        )
    
        # Normal TextInput kullan - CompactTextInput yerine
        self.result_text = TextInput(
            hint_text="""Hesaplama sonuçları burada görünecek...

Değerleri girin
'HESAPLAYIN' butonuna tıklayın
Sonuçlar burada görünecek
Designed by Lutfi

═══════════════════════════════
ORİFİS HESAPLAYICI v9.8
═══════════════════════════════""",
            size_hint_y=None,
            height=dp(1200),  # 1250 - 50 (başlık)
            font_size=dp(13),  # Varsayılan 13 dp
            multiline=True,
            readonly=True,
            background_color=COLORS['input_bg'],
            foreground_color=COLORS['text_white'],
            cursor_color=COLORS['primary_blue'],
            padding=[dp(12), dp(12)],
            scroll_y=1  # En üstten başlasın
        )
        
        # Başlangıç değerlerini ayarla
        self.result_text.font_size = dp(13)
        
        results_scroll.add_widget(self.result_text)
        results_card.add_widget(results_scroll)
        content.add_widget(results_card)
    
        # Durum Bar
        status_bar = BoxLayout(
            size_hint_y=None,
            height=dp(29),
            padding=[dp(12), dp(8)]
        )
    
        with status_bar.canvas.before:
            Color(*COLORS['bg_card'])
            status_bg = RoundedRectangle(pos=status_bar.pos, size=status_bar.size, radius=[dp(5)])
            Color(*COLORS['primary_blue'])
            status_left_border = Rectangle(pos=(status_bar.x, status_bar.y), size=(dp(2), status_bar.height))
    
        def update_status_graphics(instance, value):
            status_bg.pos = status_bar.pos
            status_bg.size = status_bar.size
            status_left_border.pos = (status_bar.x, status_bar.y)
            status_left_border.size = (dp(2), status_bar.height)
    
        status_bar.bind(pos=update_status_graphics, size=update_status_graphics)
    
        self.status_label = Label(
            text='⏳ Değerleri girin ve HESAPLAYIN!',
            font_size=dp(8),
            color=COLORS['primary_blue'],
            size_hint_x=1,
            halign='center',
            valign='middle'
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        status_bar.add_widget(self.status_label)
        content.add_widget(status_bar)
    
        # Footer
        footer = BoxLayout(
            size_hint_y=None,
            height=dp(26),
            padding=[dp(12), dp(6)]
        )
    
        with footer.canvas.before:
            Color(*COLORS['bg_dark'])
            Rectangle(pos=footer.pos, size=footer.size)
            Color(*COLORS['border_dark'])
            Line(points=[footer.x, footer.y + footer.height,
                        footer.x + footer.width, footer.y + footer.height], width=1)
    
        footer_label = Label(
            text='Designed by Lutfi • Modern UI • v9.8',
            font_size=dp(8),
            italic=True,
            color=COLORS['text_light_gray'],
            size_hint_x=1,
            halign='center',
            valign='middle'
        )
        footer_label.bind(size=footer_label.setter('text_size'))
        footer.add_widget(footer_label)
        content.add_widget(footer)
    
        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def setup_events(self):
        self.D_input.bind(text=self.on_D_change)
        self.d_input.bind(text=self.on_d_change)
        self.D_birim.bind(text=self.on_D_unit_change)
        self.d_birim.bind(text=self.on_d_unit_change)

        self.delta_p_input.bind(text=self.on_delta_p_change)
        self.p1_input.bind(text=self.on_p1_change)
        self.p2_input.bind(text=self.on_p2_change)
        self.pressure_unit.bind(text=self.on_pressure_unit_change)

        self.gaz_spinner.bind(text=self.on_gas_change)

        self.save_btn.bind(on_press=self.kaydet_hesaplama)
        self.load_btn.bind(on_press=self.yukle_hesaplama)
        self.clear_btn.bind(on_press=self.temizle)
        self.default_btn.bind(on_press=self.load_defaults)
        self.help_btn.bind(on_press=self.show_help)
        self.add_gas_btn.bind(on_press=self.add_custom_gas)

    def on_font_size_change(self, instance, value):
        """Yazı boyutu slider değişimini işle"""
        self.result_font_size = value
        self.font_size_value.text = f'{value:.0f} dp'
        
        # Ana sonuç kutusundaki yazı boyutunu güncelle
        if hasattr(self, 'result_text'):
            self.result_text.font_size = self.result_font_size
        
        # Anlık hesap popup'ı açıksa onu da güncelle
        if self.current_anlik_popup and hasattr(self, 'anlik_sonuc_label'):
            self.anlik_sonuc_label.font_size = self.anlik_result_font_size
    
    def on_box_height_change(self, instance, value):
        """Kutu yüksekliği slider değişimini işle"""
        self.result_box_height = value
        self.box_height_value.text = f'{value:.0f} dp'
        
        # Sonuç kartının yüksekliğini güncelle
        if hasattr(self, 'result_text'):
            self.result_text.height = self.result_box_height - dp(50)
        
        # Sonuç kartının yüksekliğini güncelle
        if hasattr(self, 'results_card'):
            self.results_card.height = self.result_box_height

    def update_gaz_dropdown(self):
        all_gases = {**GAZLAR, **self.orifis_kayit.custom_gazlar}
        self.gaz_spinner.values = list(all_gases.keys())
        if VARSAYILAN_DEGERLER["gaz_tipi"] in all_gases:
            self.gaz_spinner.text = VARSAYILAN_DEGERLER["gaz_tipi"]

    def get_gas_info(self, gaz_secim):
        all_gases = {**GAZLAR, **self.orifis_kayit.custom_gazlar}
        return all_gases.get(gaz_secim, GAZLAR["Hava"])

    def calculate_beta(self):
        try:
            D_val_str = self.D_input.text.strip() if self.D_input.text else ""
            d_val_str = self.d_input.text.strip() if self.d_input.text else ""

            if not D_val_str or not d_val_str:
                self.beta_label.text = 'β = Hesaplanacak'
                self.beta_label.color = COLORS['success_light']
                return

            D_val = float(D_val_str)
            d_val = float(d_val_str)

            D_val_m = convert_length(D_val, self.D_birim.text, "m")
            d_val_m = convert_length(d_val, self.d_birim.text, "m")

            self.current_values["D_m"] = D_val_m
            self.current_values["d_m"] = d_val_m

            if D_val_m > 0:
                beta = d_val_m / D_val_m
                is_valid = 0.2 <= beta <= 0.75
                check_icon = "✅" if is_valid else "⚠️"
                self.beta_label.text = f'β = {beta:.2f} {check_icon}'
                if not is_valid:
                    self.beta_label.color = COLORS['error_red']
                else:
                    self.beta_label.color = COLORS['success_light']
            else:
                self.beta_label.text = 'β = Hesaplanacak'
                self.beta_label.color = COLORS['success_light']
        except Exception as e:
            print(f"Beta hesaplama hatası: {e}")
            self.beta_label.text = 'β = Hesaplanacak'
            self.beta_label.color = COLORS['success_light']

    def update_pressure_display(self):
        try:
            unit = self.pressure_unit.text

            p1_pa = self.current_values["p1_pa"]
            p1_display = convert_pressure(p1_pa, "Pa", unit)
            self.p1_input.text = f"{p1_display:.2f}"

            p2_pa = self.current_values["p2_pa"]
            p2_display = convert_pressure(p2_pa, "Pa", unit)
            self.p2_input.text = f"{p2_display:.2f}"

            delta_p_pa = p1_pa - p2_pa
            delta_p_val = delta_p_pa / 9.80665
            self.delta_p_input.text = f"{delta_p_val:.2f}"

        except Exception as e:
            print(f"Basınç güncelleme hatası: {e}")

    def on_D_change(self, instance, value):
        self.calculate_beta()

    def on_d_change(self, instance, value):
        self.calculate_beta()

    def on_D_unit_change(self, instance, value):
        try:
            if self.D_input.text and self.D_input.text.strip():
                value_str = self.D_input.text
                old_value = float(value_str) if value_str else 0

                previous_text = getattr(instance, 'previous_text', "m")
                value_m = convert_length(old_value, previous_text, "m")
                self.current_values["D_m"] = value_m

                converted = convert_length(value_m, "m", value)
                self.D_input.text = f"{converted:.4f}"
                self.calculate_beta()

                instance.previous_text = value
        except Exception as e:
            print(f"D birim değişim hatası: {e}")

    def on_d_unit_change(self, instance, value):
        try:
            if self.d_input.text and self.d_input.text.strip():
                value_str = self.d_input.text
                old_value = float(value_str) if value_str else 0

                previous_text = getattr(instance, 'previous_text', "m")
                value_m = convert_length(old_value, previous_text, "m")
                self.current_values["d_m"] = value_m

                converted = convert_length(value_m, "m", value)
                self.d_input.text = f"{converted:.4f}"
                self.calculate_beta()

                instance.previous_text = value
        except Exception as e:
            print(f"d birim değişim hatası: {e}")

    def on_pressure_mode_change(self, mode):
        self.basinc_mode_var = mode
        try:
            if "ΔP" in mode:
                self.delta_p_input.disabled = False
                self.delta_p_input.background_color = COLORS['input_bg']
                self.p2_input.disabled = True
                self.p2_input.background_color = COLORS['disabled_gray']
                self.p2_status.text = "(Çıkış basıncı otomatik hesaplanacak)"
                self.delta_p_btn.background_color = COLORS['primary_blue_dark']
                self.delta_p_btn.color = (1, 1, 1, 1)
                self.delta_p_btn.bold = True
                self.gc_btn.background_color = COLORS['disabled_gray']
                self.gc_btn.color = COLORS['text_gray']
                self.gc_btn.bold = False
            else:
                self.delta_p_input.disabled = True
                self.delta_p_input.background_color = COLORS['disabled_gray']
                self.p2_input.disabled = False
                self.p2_input.background_color = COLORS['input_bg']
                self.p2_status.text = "(Fark basıncı otomatik hesaplanacak)"
                self.gc_btn.background_color = COLORS['primary_blue_dark']
                self.gc_btn.color = (1, 1, 1, 1)
                self.gc_btn.bold = True
                self.delta_p_btn.background_color = COLORS['disabled_gray']
                self.delta_p_btn.color = COLORS['text_gray']
                self.delta_p_btn.bold = False
                self.update_pressure_display()
        except AttributeError as e:
            print(f"Basınç modu değişim hatası: {e}")

    def on_delta_p_change(self, instance, value):
        if "ΔP" in self.basinc_mode_var and value:
            try:
                delta_p_val = float(value)
                delta_p_pa = delta_p_val * 9.80665
                p1_pa = self.current_values["p1_pa"]
                p2_pa = p1_pa - delta_p_pa
                self.current_values["p2_pa"] = p2_pa
                self.update_pressure_display()
            except:
                pass

    def on_p1_change(self, instance, value):
        if value:
            try:
                unit = self.pressure_unit.text
                value_num = float(value)
                value_pa = convert_pressure(value_num, unit, "Pa")
                self.current_values["p1_pa"] = value_pa

                if "ΔP" in self.basinc_mode_var:
                    self.on_delta_p_change(None, self.delta_p_input.text)
                else:
                    if self.p2_input.text and self.p2_input.text.strip():
                        self.on_p2_change(None, self.p2_input.text)
                    else:
                        self.update_pressure_display()
            except:
                pass

    def on_p2_change(self, instance, value):
        if "G/Ç" in self.basinc_mode_var and value:
            try:
                unit = self.pressure_unit.text
                value_num = float(value)
                value_pa = convert_pressure(value_num, unit, "Pa")
                self.current_values["p2_pa"] = value_pa

                p1_pa = self.current_values["p1_pa"]
                delta_p_pa = p1_pa - value_pa
                delta_p_val = delta_p_pa / 9.80665
                self.delta_p_input.text = f"{delta_p_val:.2f}"
            except:
                pass

    def on_pressure_unit_change(self, instance, value):
        self.update_pressure_display()

    def on_gas_change(self, instance, value):
        if value:
            info = self.get_gas_info(value)
            if value == "MANUEL GİRİŞ":
                self.density_input.text = str(VARSAYILAN_DEGERLER["yogunluk_manuel"])
                self.viscosity_input.text = str(VARSAYILAN_DEGERLER["viskozite_manuel"])
                self.density_atmosferik.text = str(VARSAYILAN_DEGERLER["yogunluk_atmosferik"])
                self.viscosity_atmosferik.text = str(VARSAYILAN_DEGERLER["viskozite_atmosferik"])
            else:
                viskozite_degeri = info.get('viskozite_293', 1e-05)
                self.viscosity_input.text = str(viskozite_degeri)
                self.viscosity_atmosferik.text = str(info.get("atmosferik_viskozite", 1.16e-05))
    
                if 'yogunluk_293' in info:
                    self.density_input.text = str(info['yogunluk_293'])
                else:
                    self.density_input.text = str(info.get("atmosferik_yogunluk", 1.293))
    
                self.density_atmosferik.text = str(info.get("atmosferik_yogunluk", 1.293))
    
            # Sıvı ise sadece atmosferik modları devre dışı bırak
            if info.get("tip") == "sıvı":
                # Atmosferik checkbox'ı devre dışı bırak
                self.atmosferik_check.disabled = True
                self.atmosferik_check.opacity = 0.5
                self.atmosferik_check.active = False
                
                # SADECE atmosferik butonlarını pasif yap
                self.yogunluk_atmosferik_btn.disabled = True
                self.yogunluk_atmosferik_btn.opacity = 0.5
                self.yogunluk_atmosferik_btn.background_color = COLORS['disabled_gray']
                self.yogunluk_atmosferik_btn.color = COLORS['text_gray']
                self.yogunluk_atmosferik_btn.bold = False
                
                self.viskozite_atmosferik_btn.disabled = True
                self.viskozite_atmosferik_btn.opacity = 0.5
                self.viskozite_atmosferik_btn.background_color = COLORS['disabled_gray']
                self.viskozite_atmosferik_btn.color = COLORS['text_gray']
                self.viskozite_atmosferik_btn.bold = False
                
                # Manuel ve Otomatik butonlarını AKTİF yap
                self.yogunluk_otomatik_btn.disabled = False
                self.yogunluk_otomatik_btn.opacity = 1.0
                
                self.yogunluk_manuel_btn.disabled = False
                self.yogunluk_manuel_btn.opacity = 1.0
                
                self.viskozite_otomatik_btn.disabled = False
                self.viskozite_otomatik_btn.opacity = 1.0
                
                self.viskozite_manuel_btn.disabled = False
                self.viskozite_manuel_btn.opacity = 1.0
                
                # Varsayılan olarak Manuel modu seç
                if self.yogunluk_mode_var == "Atmosferik":
                    self.yogunluk_mode_var = "Manuel"
                    self.on_yogunluk_mode_change('Manuel')
                
                if self.viskozite_mode_var == "Atmosferik":
                    self.viskozite_mode_var = "Manuel"
                    self.on_viskozite_mode_change('Manuel')
                    
                # Yoğunluk ve viskozite inputlarını aktif et
                if self.yogunluk_mode_var == "Manuel":
                    self.density_input.disabled = False
                    self.density_input.background_color = COLORS['input_bg']
                else:
                    self.density_input.disabled = True
                    self.density_input.background_color = COLORS['disabled_gray']
                    
                if self.viskozite_mode_var == "Manuel":
                    self.viscosity_input.disabled = False
                    self.viscosity_input.background_color = COLORS['input_bg']
                else:
                    self.viscosity_input.disabled = True
                    self.viscosity_input.background_color = COLORS['disabled_gray']
                    
            else:
                # Gaz ise tüm butonları aktif et
                self.atmosferik_check.disabled = False
                self.atmosferik_check.opacity = 1.0
                
                # Tüm yoğunluk butonlarını aktif et
                self.yogunluk_otomatik_btn.disabled = False
                self.yogunluk_otomatik_btn.opacity = 1.0
                self.yogunluk_manuel_btn.disabled = False
                self.yogunluk_manuel_btn.opacity = 1.0
                self.yogunluk_atmosferik_btn.disabled = False
                self.yogunluk_atmosferik_btn.opacity = 1.0
                
                # Tüm viskozite butonlarını aktif et
                self.viskozite_otomatik_btn.disabled = False
                self.viskozite_otomatik_btn.opacity = 1.0
                self.viskozite_manuel_btn.disabled = False
                self.viskozite_manuel_btn.opacity = 1.0
                self.viskozite_atmosferik_btn.disabled = False
                self.viskozite_atmosferik_btn.opacity = 1.0
                
                # Eğer atmosferik mod aktifse, o modda kal
                if self.atmosferik_check.active:
                    self.on_yogunluk_mode_change('Atmosferik')
                    self.on_viskozite_mode_change('Atmosferik')

    def check_and_disable_atmosferic(self):
        """Sıvı seçiliyse atmosferik modu devre dışı bırak"""
        gaz_secim = self.gaz_spinner.text
        if gaz_secim:
            info = self.get_gas_info(gaz_secim)
            if info.get("tip") == "sıvı":
                self.atmosferik_check.disabled = True
                self.atmosferik_check.opacity = 0.5
                self.atmosferik_check.active = False
            else:
                self.atmosferik_check.disabled = False
                self.atmosferik_check.opacity = 1.0

    def on_atmosferik_check(self, instance, value):
        """Atmosferik checkbox değişimini işle"""
        self.atmosferik_checked = value
        
        if value:
            self.temp_input.text = "273.15"
            self.temp_unit.text = "K"
            # Yoğunluk ve viskozite modlarını atmosferik yap
            self.yogunluk_mode_var = 'Atmosferik'
            self.viskozite_mode_var = 'Atmosferik'

            self.on_yogunluk_mode_change('Atmosferik')
            self.on_viskozite_mode_change('Atmosferik')
            self.show_snackbar("✅ Atmosferik mod aktif (0°C, 1 atm)", "success")
        else:
            # Manuel moda dön
            self.yogunluk_mode_var = 'Manuel'
            self.viskozite_mode_var = 'Manuel'

            self.on_yogunluk_mode_change('Manuel')
            self.on_viskozite_mode_change('Manuel')
            self.show_snackbar("🔄 Atmosferik mod devre dışı", "warning")

    def on_yogunluk_mode_change(self, mode):
        self.yogunluk_mode_var = mode
        if mode == "Atmosferik":
            self.density_input.disabled = True
            self.density_input.background_color = COLORS['disabled_gray']
            self.density_atmosferik.disabled = False
            self.density_atmosferik.background_color = COLORS['input_bg']

            self.yogunluk_otomatik_btn.background_color = COLORS['disabled_gray']
            self.yogunluk_otomatik_btn.color = COLORS['text_gray']
            self.yogunluk_otomatik_btn.bold = False

            self.yogunluk_manuel_btn.background_color = COLORS['disabled_gray']
            self.yogunluk_manuel_btn.color = COLORS['text_gray']
            self.yogunluk_manuel_btn.bold = False

            self.yogunluk_atmosferik_btn.background_color = COLORS['primary_blue_dark']
            self.yogunluk_atmosferik_btn.color = (1, 1, 1, 1)
            self.yogunluk_atmosferik_btn.bold = True

        elif mode == "Manuel":
            self.density_input.disabled = False
            self.density_input.background_color = COLORS['input_bg']
            self.density_atmosferik.disabled = True
            self.density_atmosferik.background_color = COLORS['disabled_gray']

            self.yogunluk_otomatik_btn.background_color = COLORS['disabled_gray']
            self.yogunluk_otomatik_btn.color = COLORS['text_gray']
            self.yogunluk_otomatik_btn.bold = False

            self.yogunluk_manuel_btn.background_color = COLORS['primary_blue_dark']
            self.yogunluk_manuel_btn.color = (1, 1, 1, 1)
            self.yogunluk_manuel_btn.bold = True

            self.yogunluk_atmosferik_btn.background_color = COLORS['disabled_gray']
            self.yogunluk_atmosferik_btn.color = COLORS['text_gray']
            self.yogunluk_atmosferik_btn.bold = False

        else:  # Otomatik
            self.density_input.disabled = True
            self.density_input.background_color = COLORS['disabled_gray']
            self.density_atmosferik.disabled = True
            self.density_atmosferik.background_color = COLORS['disabled_gray']

            self.yogunluk_otomatik_btn.background_color = COLORS['primary_blue_dark']
            self.yogunluk_otomatik_btn.color = (1, 1, 1, 1)
            self.yogunluk_otomatik_btn.bold = True

            self.yogunluk_manuel_btn.background_color = COLORS['disabled_gray']
            self.yogunluk_manuel_btn.color = COLORS['text_gray']
            self.yogunluk_manuel_btn.bold = False

            self.yogunluk_atmosferik_btn.background_color = COLORS['disabled_gray']
            self.yogunluk_atmosferik_btn.color = COLORS['text_gray']
            self.yogunluk_atmosferik_btn.bold = False

    def on_viskozite_mode_change(self, mode):
        self.viskozite_mode_var = mode
        if mode == "Atmosferik":
            self.viscosity_input.disabled = True
            self.viscosity_input.background_color = COLORS['disabled_gray']
            self.viscosity_atmosferik.disabled = False
            self.viscosity_atmosferik.background_color = COLORS['input_bg']

            self.viskozite_otomatik_btn.background_color = COLORS['disabled_gray']
            self.viskozite_otomatik_btn.color = COLORS['text_gray']
            self.viskozite_otomatik_btn.bold = False

            self.viskozite_manuel_btn.background_color = COLORS['disabled_gray']
            self.viskozite_manuel_btn.color = COLORS['text_gray']
            self.viskozite_manuel_btn.bold = False

            self.viskozite_atmosferik_btn.background_color = COLORS['primary_blue_dark']
            self.viskozite_atmosferik_btn.color = (1, 1, 1, 1)
            self.viskozite_atmosferik_btn.bold = True

        elif mode == "Manuel":
            self.viscosity_input.disabled = False
            self.viscosity_input.background_color = COLORS['input_bg']
            self.viscosity_atmosferik.disabled = True
            self.viscosity_atmosferik.background_color = COLORS['disabled_gray']

            self.viskozite_otomatik_btn.background_color = COLORS['disabled_gray']
            self.viskozite_otomatik_btn.color = COLORS['text_gray']
            self.viskozite_otomatik_btn.bold = False

            self.viskozite_manuel_btn.background_color = COLORS['primary_blue_dark']
            self.viskozite_manuel_btn.color = (1, 1, 1, 1)
            self.viskozite_manuel_btn.bold = True

            self.viskozite_atmosferik_btn.background_color = COLORS['disabled_gray']
            self.viskozite_atmosferik_btn.color = COLORS['text_gray']
            self.viskozite_atmosferik_btn.bold = False

        else:  # Otomatik
            self.viscosity_input.disabled = True
            self.viscosity_input.background_color = COLORS['disabled_gray']
            self.viscosity_atmosferik.disabled = True
            self.viscosity_atmosferik.background_color = COLORS['disabled_gray']

            self.viskozite_otomatik_btn.background_color = COLORS['primary_blue_dark']
            self.viskozite_otomatik_btn.color = (1, 1, 1, 1)
            self.viskozite_otomatik_btn.bold = True

            self.viskozite_manuel_btn.background_color = COLORS['disabled_gray']
            self.viskozite_manuel_btn.color = COLORS['text_gray']
            self.viskozite_manuel_btn.bold = False

            self.viskozite_atmosferik_btn.background_color = COLORS['disabled_gray']
            self.viskozite_atmosferik_btn.color = COLORS['text_gray']
            self.viskozite_atmosferik_btn.bold = False

    def yogunluk_hesapla(self, gaz_secim, sicaklik_K, basinc_pa):
        info = self.get_gas_info(gaz_secim)
        yogunluk_mode = self.yogunluk_mode_var.lower()

        if yogunluk_mode == "manuel":
            try:
                rho = float(self.density_input.text) if self.density_input.text else 1.2
                return rho
            except:
                return 1.2

        elif yogunluk_mode == "atmosferik":
            rho = float(self.density_atmosferik.text) if self.density_atmosferik.text else 1.293
            return rho

        else:  # otomatik
            if info.get("tip") == "sıvı":
                rho = info.get('yogunluk_293', 1000)
                return rho

            R = 8314.462618
            M = info.get("mol_agirligi", 28.97)
            if M > 0:
                rho = (basinc_pa * M) / (R * sicaklik_K)
                return rho
            else:
                return 1.2

    def viskozite_hesapla(self, gaz_secim, sicaklik_K):
        info = self.get_gas_info(gaz_secim)
        viskozite_mode = self.viskozite_mode_var.lower()

        if viskozite_mode == "manuel":
            try:
                return float(self.viscosity_input.text) if self.viscosity_input.text else 1.8e-05
            except:
                return 1.8e-05

        elif viskozite_mode == "atmosferik":
            return float(self.viscosity_atmosferik.text) if self.viscosity_atmosferik.text else 1.8e-05

        else:  # otomatik
            base_mu = info.get("viskozite_293", 1.8e-05)

            if info.get("tip") == "gaz":
                return base_mu * (sicaklik_K / 293.15)**0.7
            else:
                return base_mu

    def hesapla(self, instance):
        try:
            self.status_label.text = "⏳ Hesaplama başlatıldı..."
            self.status_label.color = COLORS['primary_blue']
            self.calc_btn.disabled = True
            self.calc_btn.text = "⏳  HESAPLANIYOR..."

            anim = Animation(opacity=0.7, duration=0.2) + Animation(opacity=1, duration=0.2)
            anim.repeat = True
            anim.start(self.calc_btn)

            # Geometrik değerler
            D_val_m = self.current_values["D_m"]
            d_val_m = self.current_values["d_m"]
            L1_val = float(self.L1_input.text) if self.L1_input.text else 0.03
            L2_val = float(self.L2_input.text) if self.L2_input.text else 0.03
            C0_baslangic_val = float(self.C0_input.text) if self.C0_input.text else 0.000000001
            gaz_secim = self.gaz_spinner.text

            if not gaz_secim:
                raise ValueError("Akışkan tipi seçiniz")

            max_iter_val = int(self.max_iter_input.text) if self.max_iter_input.text else 100
            epsilon_val = float(self.epsilon_input.text) if self.epsilon_input.text else 0.000001

            # Sıcaklık
            sicaklik_input = float(self.temp_input.text) if self.temp_input.text else 20
            sicaklik_K = convert_temperature(sicaklik_input, self.temp_unit.text, "K")

            if D_val_m <= 0 or d_val_m <= 0:
                raise ValueError("Boru ve orifis çapı 0'dan büyük olmalı")

            beta = d_val_m / D_val_m

            if beta > 0.75 or beta < 0.2:
                self.show_snackbar(f"⚠️ β={beta:.3f} ideal aralıkta değil (0.2-0.75)", "warning")

            # Basınç değerleri
            p1_gauge = self.current_values["p1_pa"]
            p2_gauge = self.current_values["p2_pa"]
            delta_p_pa = p1_gauge - p2_gauge
            delta_p_val = delta_p_pa / 9.80665

            # Absolute basınçlar
            ATMOSFERIK_BASINC = 101325
            p1_abs = p1_gauge + ATMOSFERIK_BASINC
            p2_abs = p2_gauge + ATMOSFERIK_BASINC

            # Yoğunluk ve viskozite
            rho = self.yogunluk_hesapla(gaz_secim, sicaklik_K, p1_abs)
            mu = self.viskozite_hesapla(gaz_secim, sicaklik_K)

            # İteratif hesaplama
            C0_son, Q, Re, v, converged, iter_count, C_calc = iteratif_C0_hesapla_excel(
                D_val_m, d_val_m, delta_p_pa, rho, mu, L1_val, L2_val,
                C0_baslangic_val, max_iter_val, epsilon_val
            )

            # Debi hesaplamaları
            q_m3s = Q
            q_m3h = q_m3s * 3600
            mass_flow = q_m3h * rho

            info = self.get_gas_info(gaz_secim)
            if info.get("tip") == "sıvı":
                # Sıvılar için normalize edilmiş debi hesaplanmaz
                q_normal_m3h = q_m3h
                rho_atmosferik = rho
                debi_etiketi = "🔵 SIVI DEBİ (Gerçek)"
                debi_degeri = f"{q_m3h:,.1f} m³/h"
            else:
                rho_atmosferik = info.get("atmosferik_yogunluk", 1.293)
                q_normal_m3h = q_m3h * (rho / rho_atmosferik) if rho_atmosferik > 0 else 0
                debi_etiketi = "🟢 GAZ DEBİ (Gerçek)"
                debi_degeri = f"{q_m3h:,.1f} m³/h"

            A0 = excel_A0_hesapla(D_val_m)
            A1 = excel_A1_hesapla(d_val_m)

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            katsayi = q_normal_m3h / math.sqrt(delta_p_val) if delta_p_val > 0 else 0

            # Dizayn basıncı ve sıcaklığı
            if self.atmosferik_checked:
                dizayn_p_abs = 101325
                dizayn_T = 273.15
            else:
                dizayn_p_abs = p1_abs
                dizayn_T = sicaklik_K

            # Hesaplama verilerini kaydet
            hesaplama_data = {
                "tarih": now,
                "gaz": gaz_secim,
                "sicaklik_K": sicaklik_K,
                "sicaklik_input": sicaklik_input,
                "beta": beta,
                "D": D_val_m,
                "d": d_val_m,
                "p1_gauge": p1_gauge,
                "p2_gauge": p2_gauge,
                "p1_abs": p1_abs,
                "p2_abs": p2_abs,
                "delta_p": delta_p_val,
                "delta_p_pa": delta_p_pa,
                "rho": rho,
                "mu": mu,
                "C0_baslangic": C0_baslangic_val,
                "C0_son": C0_son,
                "C_calc": C_calc,
                "Q_m3s": q_m3s,
                "Q_m3h": q_m3h,
                "mass_flow": mass_flow,
                "v": v,
                "Re": Re,
                "iter_count": iter_count,
                "converged": converged,
                "q_normal": q_normal_m3h,
                "A0": A0,
                "A1": A1,
                "katsayi": katsayi,
                "rho_atmosferik": rho_atmosferik,
                "basinc_birim": self.pressure_unit.text,
                "D_birim": self.D_birim.text,
                "d_birim": self.d_birim.text,
                "basinc_mode": self.basinc_mode_var,
                "yogunluk_mode": self.yogunluk_mode_var,
                "viskozite_mode": self.viskozite_mode_var,
                "atmosferik_mode": self.atmosferik_checked,
                "dizayn_p_abs": dizayn_p_abs,
                "dizayn_T": dizayn_T,
                "L1": L1_val,
                "L2": L2_val,
                "max_iter": max_iter_val,
                "epsilon": epsilon_val,
                "is_sivi": info.get("tip") == "sıvı"
            }

            self.hesaplama_gecmisi.append(hesaplama_data)
            self.anlik_hesap_data = hesaplama_data
            self.last_calculation_result = hesaplama_data

            # Butonları aktif et
            self.save_btn.disabled = False
            self.save_btn.opacity = 1.0
            self.anlik_hesap_btn.disabled = False
            self.anlik_hesap_btn.opacity = 1.0

            # Sonuçları göster - YENİ YAZI BOYUTU İLE
            result_text = f"""╔═══════════════════════════════════╗
║   ORİFİS HESAP SONUÇLARI          ║
╚═══════════════════════════════════╝
📅 Tarih: {now}
🌡️ Akışkan: {gaz_secim} {'(Sıvı)' if info.get('tip') == 'sıvı' else '(Gaz)'}
🔥 Sıcaklık: {sicaklik_input:.1f} {self.temp_unit.text} ({sicaklik_K:.1f} K)
📏 β Oranı: {beta:.2f} {'✅' if 0.2 <= beta <= 0.75 else '⚠️'}
⚡ İterasyon: {iter_count} {'✅' if converged else '⚠️'}
🌍 Atmosferik Mod: {'❌ KAPALI (Sıvı)' if info.get('tip') == 'sıvı' else '✅ AÇIK' if self.atmosferik_checked else '❌ KAPALI'}
📊 Yoğunluk Modu: {self.yogunluk_mode_var}
📊 Viskozite Modu: {self.viskozite_mode_var}
📊 BASINÇ DEĞERLERİ:
Giriş: {p1_gauge/1000:.1f} kPa (gauge)
Giriş: {p1_abs/1000:.1f} kPa (mutlak)
Çıkış: {p2_gauge/1000:.1f} kPa (gauge)
ΔP: {delta_p_val:.1f} mmH₂O ({delta_p_pa:.0f} Pa)
📏 GEOMETRİK ÖLÇÜLER:
Boru Çapı (D): {D_val_m:.4f} m
Orifis Çapı (d): {d_val_m:.4f} m
A0 (Boru Kesiti): {A0:.4f} m²
A1 (Orifis Kesiti): {A1:.4f} m²
🚀 DEBİ SONUÇLARI:"""

            if info.get("tip") == "sıvı":
                result_text += f"""
╔═══════════════════════════════════════════════════════════╗
║  🔵 SIVI DEBİ (Gerçek): {q_m3h:,.1f} m³/h                 ║
║  🔵 KÜTLESEL DEBİ: {mass_flow:,.1f} kg/h                  ║
║  🔵 YOĞUNLUK: {rho:.3f} kg/m³                            ║
║                                                           ║
║  ⚠️ Sıvılar için normalize edilmiş debi (Nm³/h)           ║
║    hesaplanmaz. Yalnızca gerçek debi (m³/h) gösterilir.   ║
╚═══════════════════════════════════════════════════════════╝"""
            else:
                result_text += f"""
╔═══════════════════════════════════════════════════════════╗
║  🟢 GAZ DEBİ (Gerçek): {q_m3h:,.1f} m³/h                  ║
║  🟢 KÜTLESEL DEBİ: {mass_flow:,.1f} kg/h                  ║
║  🟢 NORMAL DEBİ: {q_normal_m3h:,.1f} Nm³/h (0°C, 1 atm)   ║
║                                                           ║
║  🟢 GERÇEK YOĞUNLUK: {rho:.3f} kg/m³                     ║
║  🟢 ATMOSFERİK YOĞUNLUK: {rho_atmosferik:.3f} kg/m³      ║
║    (0°C, 1 atm)                                          ║
╚═══════════════════════════════════════════════════════════╝"""

            result_text += f"""
📈 AKIŞ PARAMETRELERİ:
Hız: {v:.2f} m/s
Reynolds: {Re:,.0f}
Viskozite: {mu:.2e} Pa·s
🎯 C KATSAYILARI:
Başlangıç C0: {C0_baslangic_val:.3f}
Hesaplanan C_calc: {C_calc:.3f}
Son C0 Değeri: {C0_son:.3f}
Fark: {C0_son - C_calc:.3f}
🔢 KATSAYI (Anlık Hesap İçin):
k = Nm³/h / √ΔP = {katsayi:.2f}
📊 DİZAYN ŞARTLARI:
{'🌍 ATMOSFERİK' if self.atmosferik_checked else '📏 ÖLÇÜLEN'}
Basınç: {dizayn_p_abs/1000:.1f} kPa (mutlak)
Sıcaklık: {dizayn_T:.1f} K ({dizayn_T-273.15:.1f}°C)
{'✅ YAKINSAMA BAŞARILI!' if converged else '⚠️ MAX ITERASYONA ULAŞILDI!'}
═══════════════════════════════════
HESAPLAMA TAMAM v9.8 ✅
Designed by Lutfi
═══════════════════════════════════
"""
            
            # Yeni yazı boyutu ile güncelle
            self.result_text.font_size = self.result_font_size
            self.result_text.text = result_text

            self.status_label.text = f"✅ Hesaplama tamam! {'Sıvı debi: ' if info.get('tip') == 'sıvı' else 'Normal debi: '}{q_normal_m3h:,.1f} {'m³/h' if info.get('tip') == 'sıvı' else 'Nm³/h'}"
            self.status_label.color = COLORS['success_light']

            self.show_snackbar("✅ Hesaplama başarıyla tamamlandı!", "success")

        except ValueError as ve:
            self.result_text.text = f"❌ HATA: {str(ve)}\n\nLütfen değerleri kontrol edin."
            self.status_label.text = "❌ Hata: Geçersiz değer!"
            self.status_label.color = COLORS['error_red']
            self.show_snackbar(f"❌ Hata: {str(ve)[:50]}", "error")

        except Exception as ex:
            self.result_text.text = f"❌ SİSTEM HATASI: {str(ex)}\n\nLütfen tekrar deneyin."
            self.status_label.text = "❌ Hata: Hesaplama başarısız!"
            self.status_label.color = COLORS['error_red']
            self.show_snackbar(f"❌ Sistem hatası: {str(ex)[:50]}", "error")

        finally:
            anim.cancel(self.calc_btn)
            self.calc_btn.disabled = False
            self.calc_btn.text = "🚀  HESAPLA"
            self.calc_btn.opacity = 1.0

    def show_anlik_hesap_popup(self, instance):
        """Anlık hesap popup'ını göster - OPTIMIZED FOR SMALL SCREENS"""
        if not self.anlik_hesap_data:
            self.show_snackbar("❌ Önce dizayn hesabı yapın!", "error")
            return
        
        content = BoxLayout(orientation='vertical', spacing=0, padding=0)
        
        # Header (aynı)
        header = BoxLayout(orientation='vertical', padding=[dp(10), dp(6)], 
                          size_hint_y=None, height=dp(48))
        
        with header.canvas.before:
            Color(*COLORS['bg_card'])
            header_bg = RoundedRectangle(pos=header.pos, size=header.size, radius=[dp(12), dp(12), 0, 0])
            Color(*COLORS['warning_orange'])
            header_accent = Rectangle(pos=(header.x, header.y + header.height - dp(2)), 
                                      size=(header.width, dp(2)))
            Color(0.824, 0.663, 0.133, 0.1)
            header_glow = Rectangle(pos=(header.x, header.y + header.height - dp(15)), 
                                   size=(header.width, dp(15)))
        
        def update_header_graphics(instance, value):
            header_bg.pos = header.pos
            header_bg.size = header.size
            header_accent.pos = (header.x, header.y + header.height - dp(2))
            header_accent.size = (header.width, dp(2))
            header_glow.pos = (header.x, header.y + header.height - dp(15))
            header_glow.size = (header.width, dp(15))
        
        header.bind(pos=update_header_graphics, size=update_header_graphics)
        
        title = Label(
            text='ANLIK HESAP',
            font_size=dp(14),
            bold=True,
            color=COLORS['warning_orange'],
            size_hint_y=None,
            height=dp(22),
            halign='center'
        )
        title.bind(size=title.setter('text_size'))
        
        subtitle = Label(
            text=f'Dizayn Debi: {self.anlik_hesap_data["q_normal"]:.1f} {"m³/h" if self.anlik_hesap_data.get("is_sivi") else "Nm³/h"}',
            font_size=dp(9),
            color=COLORS['text_gray'],
            size_hint_y=None,
            height=dp(16),
            halign='center',
            italic=True
        )
        subtitle.bind(size=subtitle.setter('text_size'))
        
        header.add_widget(title)
        header.add_widget(subtitle)
        content.add_widget(header)
        
        # Main Content Area - SIDE BY SIDE
        main_container = BoxLayout(orientation='horizontal', spacing=0)
        
        # ========== SOL TARAF: DEĞERLERİ GİRİN (%25) - SOL ÜST HİZALAMA ==========
        left_panel = BoxLayout(orientation='vertical', spacing=dp(4),
                              padding=[dp(6), dp(6), dp(6), dp(6)], size_hint_x=0.25)
        
        with left_panel.canvas.before:
            Color(*COLORS['bg_card'])
            left_bg = Rectangle(pos=left_panel.pos, size=left_panel.size)
            Color(*COLORS['border_dark'])
            left_border = Line(points=[], width=1)
        
        def update_left_graphics(instance, value):
            left_bg.pos = left_panel.pos
            left_bg.size = left_panel.size
            left_border.points = [
                left_panel.x + left_panel.width, left_panel.y,
                left_panel.x + left_panel.width, left_panel.y + left_panel.height
            ]
        
        left_panel.bind(pos=update_left_graphics, size=update_left_graphics)
        
        # Inputs Title - EN ÜST
        inputs_title_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(22))
        with inputs_title_box.canvas.before:
            Color(*COLORS['primary_blue_dark'])
            inputs_title_bg = RoundedRectangle(pos=inputs_title_box.pos, size=inputs_title_box.size, 
                                              radius=[dp(4)])
        
        def update_inputs_title_bg(instance, value):
            inputs_title_bg.pos = inputs_title_box.pos
            inputs_title_bg.size = inputs_title_box.size
        
        inputs_title_box.bind(pos=update_inputs_title_bg, size=update_inputs_title_bg)
        
        inputs_title = Label(
            text='Değerler',
            font_size=dp(8),
            bold=True,
            color=(1, 1, 1, 1),
            halign='center'
        )
        inputs_title.bind(size=inputs_title.setter('text_size'))
        inputs_title_box.add_widget(inputs_title)
        left_panel.add_widget(inputs_title_box)
        
        # ΔP Input - SOL ÜST
        dp_container = BoxLayout(orientation='vertical', spacing=dp(1),
                                size_hint=(1, None), height=dp(65))
        with dp_container.canvas.before:
            Color(0.345, 0.651, 1.0, 0.1)
            dp_card_bg = RoundedRectangle(pos=dp_container.pos, size=dp_container.size, radius=[dp(4)])
            Color(*COLORS['primary_blue'])
            dp_card_border = Line(
                rounded_rectangle=(dp_container.x, dp_container.y, dp_container.width, dp_container.height, dp(4)),
                width=1
            )
        
        def update_dp_bg(instance, value):
            dp_card_bg.pos = dp_container.pos
            dp_card_bg.size = dp_container.size
            dp_card_border.rounded_rectangle = (dp_container.x, dp_container.y, dp_container.width, dp_container.height, dp(4))
        
        dp_container.bind(pos=update_dp_bg, size=update_dp_bg)
        
        dp_label = Label(
            text='Anlık ΔP',
            font_size=dp(6),
            color=COLORS['primary_blue'],
            size_hint_y=None,
            height=dp(12),
            halign='center',
            bold=True
        )
        dp_label.bind(size=dp_label.setter('text_size'))
        
        self.anlik_delta_p_input = CompactTextInput(
            hint_text=str(self.anlik_hesap_data["delta_p"]),
            text=f"{self.anlik_hesap_data['delta_p']:.2f}",
            size_hint_y=None,
            height=dp(30),
            halign='center',
            font_size=dp(8),
            padding=[dp(4), dp(3)]
        )
        
        dp_unit = Label(
            text='mmH₂O',
            font_size=dp(5),
            color=COLORS['text_gray'],
            size_hint_y=None,
            height=dp(10),
            halign='center',
            bold=True
        )
        dp_unit.bind(size=dp_unit.setter('text_size'))
        
        dp_container.add_widget(dp_label)
        dp_container.add_widget(self.anlik_delta_p_input)
        dp_container.add_widget(dp_unit)
        left_panel.add_widget(dp_container)
        
        # Pressure Input
        p_container = BoxLayout(orientation='vertical', spacing=dp(1),
                               size_hint=(1, None), height=dp(65))
        with p_container.canvas.before:
            Color(0.139, 0.525, 0.212, 0.1)
            p_card_bg = RoundedRectangle(pos=p_container.pos, size=p_container.size, radius=[dp(4)])
            Color(*COLORS['success_green'])
            p_card_border = Line(
                rounded_rectangle=(p_container.x, p_container.y, p_container.width, p_container.height, dp(4)),
                width=1
            )
        
        def update_p_bg(instance, value):
            p_card_bg.pos = p_container.pos
            p_card_bg.size = p_container.size
            p_card_border.rounded_rectangle = (p_container.x, p_container.y, p_container.width, p_container.height, dp(4))
        
        p_container.bind(pos=update_p_bg, size=update_p_bg)
        
        p_label = Label(
            text='Basınç',
            font_size=dp(6),
            color=COLORS['success_green'],
            size_hint_y=None,
            height=dp(12),
            halign='center',
            bold=True
        )
        p_label.bind(size=p_label.setter('text_size'))
        
        self.anlik_p_input = CompactTextInput(
            hint_text=f"{self.anlik_hesap_data['p1_gauge']/1000:.1f}",
            text=f"{self.anlik_hesap_data['p1_gauge']/1000:.1f}",
            size_hint_y=None,
            height=dp(30),
            halign='center',
            font_size=dp(8),
            padding=[dp(4), dp(3)]
        )
        
        self.anlik_p_birim_spinner = CompactSpinner(
            text='kPa',
            values=('kPa', 'bar', 'atm'),
            size_hint_y=None,
            height=dp(18),
            font_size=dp(7),
            padding=[dp(3), dp(2)]
        )
        
        p_container.add_widget(p_label)
        p_container.add_widget(self.anlik_p_input)
        p_container.add_widget(self.anlik_p_birim_spinner)
        left_panel.add_widget(p_container)
        
        # Temperature Input
        t_container = BoxLayout(orientation='vertical', spacing=dp(1),
                               size_hint=(1, None), height=dp(65))
        with t_container.canvas.before:
            Color(0.537, 0.341, 0.898, 0.1)
            t_card_bg = RoundedRectangle(pos=t_container.pos, size=t_container.size, radius=[dp(4)])
            Color(*COLORS['purple'])
            t_card_border = Line(
                rounded_rectangle=(t_container.x, t_container.y, t_container.width, t_container.height, dp(4)),
                width=1
            )
        
        def update_t_bg(instance, value):
            t_card_bg.pos = t_container.pos
            t_card_bg.size = t_container.size
            t_card_border.rounded_rectangle = (t_container.x, t_container.y, t_container.width, t_container.height, dp(4))
        
        t_container.bind(pos=update_t_bg, size=update_t_bg)
        
        t_label = Label(
            text='Sıcaklık',
            font_size=dp(6),
            color=COLORS['purple'],
            size_hint_y=None,
            height=dp(12),
            halign='center',
            bold=True
        )
        t_label.bind(size=t_label.setter('text_size'))
        
        self.anlik_t_input = CompactTextInput(
            hint_text=f"{self.anlik_hesap_data['sicaklik_input']:.1f}",
            text=f"{self.anlik_hesap_data['sicaklik_input']:.1f}",
            size_hint_y=None,
            height=dp(30),
            halign='center',
            font_size=dp(8),
            padding=[dp(4), dp(3)]
        )
        
        self.anlik_t_birim_spinner = CompactSpinner(
            text=self.temp_unit.text,
            values=('K', '°C'),
            size_hint_y=None,
            height=dp(18),
            font_size=dp(7),
            padding=[dp(3), dp(2)]
        )
        
        t_container.add_widget(t_label)
        t_container.add_widget(self.anlik_t_input)
        t_container.add_widget(self.anlik_t_birim_spinner)
        left_panel.add_widget(t_container)
        
        # Calculate Button - EN ALTTA
        hesapla_btn = CompactButton(
            "HESAPLA",
            color_type="warning",
            icon="⚡",
            size_hint_y=None,
            height=dp(32)
        )
        hesapla_btn.font_size = dp(9)
        hesapla_btn.bind(on_press=self.anlik_hesapla_popup)
        left_panel.add_widget(hesapla_btn)
        
        # Spacer - Kalan alanı doldur (inputları yukarıda tutar)
        spacer = BoxLayout(size_hint_y=1)
        left_panel.add_widget(spacer)
        
        main_container.add_widget(left_panel)
        
        # ========== SAĞ TARAF: SONUÇLAR (%75) ==========
        right_panel = BoxLayout(orientation='vertical', spacing=0,
                               padding=[dp(6), dp(6)], size_hint_x=0.75)
        
        # Results Title
        results_title_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(24))
        with results_title_box.canvas.before:
            Color(*COLORS['success_green_dark'])
            results_title_bg = RoundedRectangle(pos=results_title_box.pos, size=results_title_box.size, 
                                               radius=[dp(4)])
        
        def update_results_title_bg(instance, value):
            results_title_bg.pos = results_title_box.pos
            results_title_bg.size = results_title_box.size
        
        results_title_box.bind(pos=update_results_title_bg, size=update_results_title_bg)
        
        results_title = Label(
            text='ANLIK HESAP SONUÇLARI',
            font_size=dp(9),
            bold=True,
            color=COLORS['success_light'],
            halign='center'
        )
        results_title.bind(size=results_title.setter('text_size'))
        results_title_box.add_widget(results_title)
        right_panel.add_widget(results_title_box)
        
        # Yazı Boyutu Kontrolleri - SAĞ PANELDE
        anlik_control_row = BoxLayout(orientation='horizontal', spacing=dp(8),
                                     padding=[dp(2), dp(2)],
                                     size_hint_y=None, height=dp(30))
        
        anlik_font_label = Label(
            text='Yazı Boyutu:',
            size_hint_x=0.3,
            font_size=dp(8),
            color=COLORS['text_gray'],
            halign='left',
            bold=True
        )
        anlik_font_label.bind(size=anlik_font_label.setter('text_size'))
        
        self.anlik_font_slider = Slider(
            min=6,
            max=16,
            value=self.anlik_result_font_size,
            size_hint_x=0.5
        )
        self.anlik_font_slider.bind(value=self.on_anlik_font_size_change)
        
        self.anlik_font_value = Label(
            text=f'{self.anlik_result_font_size:.0f} dp',
            size_hint_x=0.2,
            font_size=dp(8),
            color=COLORS['warning_orange'],
            halign='center',
            bold=True
        )
        self.anlik_font_value.bind(size=self.anlik_font_value.setter('text_size'))
        
        anlik_control_row.add_widget(anlik_font_label)
        anlik_control_row.add_widget(self.anlik_font_slider)
        anlik_control_row.add_widget(self.anlik_font_value)
        right_panel.add_widget(anlik_control_row)
        
        # SCROLLVIEW for results - DÜZELTİLMİŞ
        results_scroll = ScrollView(
            size_hint=(1, 1),
            bar_width=dp(8),
            bar_color=COLORS['warning_orange'],
            bar_inactive_color=(0.824, 0.663, 0.133, 0.3),
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            effect_cls='ScrollEffect',
            always_overscroll=False
        )
        
        # Styled result text input - SCROLLABLE
        self.anlik_sonuc_label = TextInput(
            hint_text="""ANLIK HESAP SONUÇLARI
    
    KULLANIM:
    1. Sol panelden değerleri girin
    2. HESAPLA butonuna tıklayın
    3. Sonuçlar burada görünecek
    
    IPUCU:
    - Anlik ΔP: Anlik fark basinci
    - Anlik Basinç: Anlik giris basinci
    - Anlik Sicaklik: Anlik sicaklik
    
    Sonuçlar detayli olarak bu alanda
    gosterilecektir.
    
    Hesaplama için sol paneli kullanın
    Designed by Lutfi""",
            size_hint_y=None,
            height=dp(600),  # Sabit yükseklik
            font_size=self.anlik_result_font_size,
            multiline=True,
            readonly=True,
            background_color=(0.051, 0.067, 0.090, 1),
            foreground_color=COLORS['text_white'],
            cursor_color=COLORS['warning_orange'],
            padding=[dp(12), dp(12), dp(12), dp(12)]
        )
        
        results_scroll.add_widget(self.anlik_sonuc_label)
        right_panel.add_widget(results_scroll)
        
        main_container.add_widget(right_panel)
        content.add_widget(main_container)
        
        # Footer Butons
        footer = BoxLayout(orientation='horizontal', spacing=dp(4),
                          padding=[dp(4), dp(4)],
                          size_hint_y=None, height=dp(35))
        
        with footer.canvas.before:
            Color(*COLORS['bg_card'])
            footer_bg = RoundedRectangle(pos=footer.pos, size=footer.size, radius=[0, 0, dp(8), dp(8)])
            Color(*COLORS['border_dark'])
            footer_line = Line(points=[footer.x, footer.y + footer.height, 
                                      footer.x + footer.width, footer.y + footer.height], 
                              width=1)
        
        def update_footer_graphics(instance, value):
            footer_bg.pos = footer.pos
            footer_bg.size = footer.size
            footer_line.points = [footer.x, footer.y + footer.height,
                                 footer.x + footer.width, footer.y + footer.height]
        
        footer.bind(pos=update_footer_graphics, size=update_footer_graphics)
        
        pdf_btn = CompactButton(
            "TXT OLUŞTUR",
            color_type="danger",
            icon="",
            size_hint_x=0.33
        )
        pdf_btn.font_size = dp(8)
        pdf_btn.height = dp(28)
        pdf_btn.bind(on_press=lambda x: self.create_anlik_pdf_safe(popup))
        
        kaydet_btn = CompactButton(
            "KAYDET",
            color_type="primary",
            icon="",
            size_hint_x=0.33
        )
        kaydet_btn.font_size = dp(8)
        kaydet_btn.height = dp(28)
        kaydet_btn.bind(on_press=lambda x: self.kaydet_anlik_hesap(popup))
        
        kapat_btn = CompactButton(
            "KAPAT",
            color_type="secondary",
            icon="",
            size_hint_x=0.34
        )
        kapat_btn.font_size = dp(8)
        kapat_btn.height = dp(28)
        kapat_btn.bind(on_press=lambda x: popup.dismiss())
        
        footer.add_widget(pdf_btn)
        footer.add_widget(kaydet_btn)
        footer.add_widget(kapat_btn)
        content.add_widget(footer)
        
        # Create popup
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.95, 0.95),
            background_color=COLORS['bg_dark'],
            auto_dismiss=False,
            separator_color=COLORS['warning_orange']
        )
        
        self.current_anlik_popup = popup
        popup.open()

    def on_anlik_font_size_change(self, instance, value):
        """Anlık hesap yazı boyutu slider değişimini işle"""
        self.anlik_result_font_size = value
        self.anlik_font_value.text = f'{value:.0f} dp'
        
        # Anlık sonuç etiketindeki yazı boyutunu güncelle
        if hasattr(self, 'anlik_sonuc_label'):
            self.anlik_sonuc_label.font_size = self.anlik_result_font_size

    def anlik_hesapla_popup(self, instance):
        """Popup içindeki anlık hesabı yap"""
        if not self.anlik_hesap_data:
            return
        
        try:
            anlik_delta_p_val = float(self.anlik_delta_p_input.text) if self.anlik_delta_p_input.text else 0
            anlik_p_input = float(self.anlik_p_input.text) if self.anlik_p_input.text else 0
            anlik_t_input = float(self.anlik_t_input.text) if self.anlik_t_input.text else 0

            if anlik_delta_p_val <= 0 or anlik_p_input <= 0 or anlik_t_input <= 0:
                raise ValueError("Anlık değerler pozitif olmalı")

            anlik_p_unit = self.anlik_p_birim_spinner.text
            anlik_t_unit = self.anlik_t_birim_spinner.text
            
            # Birim dönüşümleri
            if anlik_p_unit == "kPa":
                anlik_p_pa = anlik_p_input * 1000
            elif anlik_p_unit == "bar":
                anlik_p_pa = anlik_p_input * 100000
            elif anlik_p_unit == "atm":
                anlik_p_pa = anlik_p_input * 101325
            else:
                anlik_p_pa = anlik_p_input * 1000  # varsayılan kPa
            
            anlik_t_K = convert_temperature(anlik_t_input, anlik_t_unit, "K")

            dizayn_q_normal = self.anlik_hesap_data["q_normal"]
            dizayn_delta_p = self.anlik_hesap_data["delta_p"]
            dizayn_p_abs = self.anlik_hesap_data.get("dizayn_p_abs", self.anlik_hesap_data["p1_abs"])
            dizayn_T = self.anlik_hesap_data.get("dizayn_T", self.anlik_hesap_data["sicaklik_K"])
            katsayi = self.anlik_hesap_data["katsayi"]

            # Akışkan tipini kontrol et
            gaz_secim = self.gaz_spinner.text
            info = self.get_gas_info(gaz_secim)
            is_sivi = info.get("tip") == "sıvı"

            ATMOSFERIK_BASINC = 101325
            anlik_p_abs = anlik_p_pa + ATMOSFERIK_BASINC

            # Sıvılar için normalize etme yok
            if is_sivi:
                # Sıvılar için: ham debi = katsayi * sqrt(ΔP)
                anlik_debi = katsayi * math.sqrt(anlik_delta_p_val) if katsayi > 0 else 0

                sonuc_text = f"""📊 ANLIK HESAP SONUÇLARI (SIVI)

Anlık ΔP: {anlik_delta_p_val:.1f} mmH₂O
Anlık Basınç: {anlik_p_input:.1f} {anlik_p_unit} (gauge)
Anlık Sıcaklık: {anlik_t_input:.1f} {anlik_t_unit} ({anlik_t_K:.1f} K)

Anlık Debi: {anlik_debi:.1f} m³/h
Katsayı (k): {katsayi:.2f}

Dizayn Debi: {dizayn_q_normal:.1f} m³/h
Dizayn ΔP: {dizayn_delta_p:.1f} mmH₂O

⚠️ Designed by Lutfi"""

            else:
                # Gazlar için normalize etme
                ham_debi_anlik = katsayi * math.sqrt(anlik_delta_p_val) if katsayi > 0 else 0

                p_oran = anlik_p_abs / dizayn_p_abs
                T_oran = dizayn_T / anlik_t_K
                duzeltme_faktor = math.sqrt(p_oran * T_oran)
                anlik_nm3h = ham_debi_anlik * duzeltme_faktor

                sonuc_text = f"""📊 ANLIK HESAP SONUÇLARI (GAZ)

Anlık ΔP: {anlik_delta_p_val:.1f} mmH₂O
Anlık Basınç: {anlik_p_input:.1f} {anlik_p_unit} (gauge)
Anlık Basınç: {anlik_p_abs/1000:.1f} kPa (mutlak)
Anlık Sıcaklık: {anlik_t_input:.1f} {anlik_t_unit} ({anlik_t_K:.1f} K)

Ham Debi: {ham_debi_anlik:.1f} m³/h (k × √ΔP)
Düzeltme Faktörü: √(({anlik_p_abs/1000:.1f}/{dizayn_p_abs/1000:.1f}) × ({dizayn_T:.1f}/{anlik_t_K:.1f})) = {duzeltme_faktor:.2f}

Anlık Normal Debi: {anlik_nm3h:.1f} Nm³/h
Katsayı (k): {katsayi:.2f}

Dizayn Normal Debi: {dizayn_q_normal:.1f} Nm³/h
Dizayn ΔP: {dizayn_delta_p:.1f} mmH₂O
Dizayn Mutlak Basınç: {dizayn_p_abs/1000:.1f} kPa
Dizayn Sıcaklık: {dizayn_T:.1f} K

Designed by Lutfi"""

            # Yeni yazı boyutu ile güncelle
            self.anlik_sonuc_label.font_size = self.anlik_result_font_size
            self.anlik_sonuc_label.text = sonuc_text
            self.show_snackbar("✅ Anlık hesap tamamlandı!", "success")

        except ValueError as ve:
            self.anlik_sonuc_label.text = f"❌ HATA: {str(ve)}\n\nLütfen geçerli sayısal değerler girin."
            self.show_snackbar(f"❌ Hata: {str(ve)}", "error")

        except Exception as ex:
            self.anlik_sonuc_label.text = f"❌ SİSTEM HATASI: {str(ex)}\n\nLütfen tekrar deneyin."
            self.show_snackbar("❌ Sistem hatası", "error")

    def create_anlik_pdf_safe(self, popup):
        """Anlık hesap sonuçlarını güvenli şekilde TXT olarak oluştur"""
        try:
            if not self.anlik_sonuc_label.text or "ANLIK HESAP SONUÇLARI" not in self.anlik_sonuc_label.text:
                self.show_snackbar("❌ Önce anlık hesap yapın!", "error")
                return
            
            # Önce popup'ı kapat
            if popup:
                popup.dismiss()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dosya_adi = f"anlik_hesap_{timestamp}.txt"
            
            # Platform bazlı dosya yolu
            try:
                if current_platform == "Android":
                    try:
                        from android.storage import app_storage_path
                        base_dir = Path(app_storage_path())
                    except:
                        from jnius import autoclass
                        PythonActivity = autoclass('org.kivy.android.PythonActivity')
                        context = PythonActivity.mActivity
                        files_dir = context.getFilesDir().getAbsolutePath()
                        base_dir = Path(files_dir)
                    
                    save_dir = base_dir / "orifis_kayitlar"
                    save_dir.mkdir(parents=True, exist_ok=True)
                    kayit_yolu = save_dir / dosya_adi
                else:
                    # Windows/Linux için
                    kayit_yolu = Path("orifis_kayitlar") / dosya_adi
                    kayit_yolu.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"Dizin oluşturma hatası: {e}")
                kayit_yolu = Path("orifis_kayitlar") / dosya_adi
                kayit_yolu.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                # Dosyayı oluştur
                with open(kayit_yolu, 'w', encoding='utf-8') as f:
                    f.write("=" * 50 + "\n")
                    f.write("ANLIK HESAP SONUÇLARI\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(self.anlik_sonuc_label.text)
                    f.write("\n\n" + "=" * 50 + "\n")
                    f.write(f"Kayıt Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Dosya Konumu: {str(kayit_yolu)}\n")
                    f.write("=" * 50)
                
                print(f"Dosya oluşturuldu: {kayit_yolu}")
                
                # Başarı mesajı
                self.show_snackbar(f"✅ TXT oluşturuldu: {dosya_adi}", "success")
                
                # Platform bazlı dosya seçenekleri
                if current_platform == "Android":
                    Clock.schedule_once(lambda dt: self.show_android_file_info(str(kayit_yolu), dosya_adi), 0.5)
                else:
                    Clock.schedule_once(lambda dt: self.show_desktop_file_options(kayit_yolu, dosya_adi), 0.5)
                    
            except PermissionError:
                print("İzin hatası!")
                self.show_snackbar("❌ Yazma izni reddedildi!", "error")
            except Exception as e:
                print(f"Dosya yazma hatası: {e}")
                import traceback
                traceback.print_exc()
                self.show_snackbar(f"❌ Dosya hatası: {str(e)[:30]}", "error")
                
        except Exception as e:
            print(f"İşlem hatası: {e}")
            import traceback
            traceback.print_exc()
            self.show_snackbar(f"❌ Hata: {str(e)[:30]}", "error")
    
    def show_desktop_file_options(self, kayit_yolu, dosya_adi):
        """Windows/Linux/Mac için dosya seçenekleri"""
        try:
            content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
            
            content.add_widget(Label(
                text=f"✅ Dosya Oluşturuldu\n{dosya_adi}",
                color=COLORS['text_white'],
                size_hint_y=None,
                height=dp(60),
                font_size=dp(14),
                halign='center'
            ))
            
            path_label = Label(
                text=f"Konum:\n{str(kayit_yolu)}",
                color=COLORS['primary_blue'],
                size_hint_y=None,
                height=dp(80),
                font_size=dp(10),
                halign='center'
            )
            path_label.bind(size=path_label.setter('text_size'))
            content.add_widget(path_label)
            
            button_box = BoxLayout(orientation='horizontal', spacing=dp(10),
                                  size_hint_y=None, height=dp(40))
            
            def open_location(instance):
                import os, subprocess
                try:
                    if current_platform == "Windows":
                        os.startfile(str(kayit_yolu.parent))
                    elif current_platform == "Darwin":  # macOS
                        subprocess.call(["open", str(kayit_yolu.parent)])
                    else:  # Linux
                        subprocess.call(["xdg-open", str(kayit_yolu.parent)])
                    file_popup.dismiss()
                except Exception as e:
                    print(f"Konum açma hatası: {e}")
                    self.show_snackbar("❌ Konum açılamadı", "error")
            
            def close_popup(instance):
                file_popup.dismiss()
            
            goster_btn = CompactButton("KLASÖRÜ AÇ", color_type="primary", on_press=open_location)
            kapat_btn = CompactButton("KAPAT", color_type="secondary", on_press=close_popup)
            
            button_box.add_widget(goster_btn)
            button_box.add_widget(kapat_btn)
            content.add_widget(button_box)
            
            file_popup = Popup(
                title='📄 Dosya Oluşturuldu',
                content=content,
                size_hint=(0.85, 0.6),
                background_color=COLORS['bg_card']
            )
            file_popup.open()
            
        except Exception as e:
            print(f"Popup hatası: {e}")
            self.show_snackbar(f"✅ Dosya kaydedildi: {dosya_adi}", "success")
    
    def show_android_file_info(self, kayit_yolu, dosya_adi):
        """Android için basit bilgi popup'ı"""
        try:
            content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
            
            content.add_widget(Label(
                text=f"✅ Dosya Kaydedildi\n{dosya_adi}",
                color=COLORS['text_white'],
                size_hint_y=None,
                height=dp(60),
                font_size=dp(14),
                halign='center'
            ))
            
            info_label = Label(
                text="Dosya uygulama dahili\ndepolamasına kaydedildi.",
                color=COLORS['primary_blue'],
                size_hint_y=None,
                height=dp(50),
                font_size=dp(11),
                halign='center'
            )
            info_label.bind(size=info_label.setter('text_size'))
            content.add_widget(info_label)
            
            path_label = Label(
                text=f"Konum:\n{kayit_yolu}",
                color=COLORS['text_gray'],
                size_hint_y=None,
                height=dp(60),
                font_size=dp(9),
                halign='center'
            )
            path_label.bind(size=path_label.setter('text_size'))
            content.add_widget(path_label)
            
            def close_popup(instance):
                info_popup.dismiss()
            
            kapat_btn = CompactButton("TAMAM", color_type="primary", on_press=close_popup)
            content.add_widget(kapat_btn)
            
            info_popup = Popup(
                title='📄 Dosya Kaydedildi',
                content=content,
                size_hint=(0.85, 0.55),
                background_color=COLORS['bg_card']
            )
            info_popup.open()
            
        except Exception as e:
            print(f"Popup hatası: {e}")
            self.show_snackbar("✅ Dosya kaydedildi", "success")
    
    def kaydet_anlik_hesap(self, popup):
        """Anlık hesap sonuçlarını kaydet"""
        try:
            if not self.anlik_sonuc_label.text or "ANLIK HESAP SONUÇLARI" not in self.anlik_sonuc_label.text:
                self.show_snackbar("❌ Önce anlık hesap yapın!", "error")
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dosya_adi = f"anlik_hesap_{timestamp}.txt"
            kayit_yolu = self.orifis_kayit.get_save_dir() / dosya_adi
            
            with open(kayit_yolu, 'w', encoding='utf-8') as f:
                f.write("=" * 50 + "\n")
                f.write("ANLIK HESAP SONUÇLARI\n")
                f.write("=" * 50 + "\n\n")
                f.write(self.anlik_sonuc_label.text)
                f.write("\n\n" + "=" * 50 + "\n")
                f.write(f"Kayıt Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50)
            
            self.show_snackbar(f"✅ Kaydedildi: {dosya_adi}", "success")
            
        except Exception as e:
            print(f"Kayıt hatası: {e}")
            self.show_snackbar(f"❌ Kayıt hatası: {str(e)[:50]}", "error")
                      
    
    
    def show_txt_share_options(self, dosya_adi, kayit_yolu):
        """TXT paylaşım seçeneklerini göster"""
        try:
            content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
            
            content.add_widget(Label(
                text=f"Dosya Oluşturuldu:\n{dosya_adi}",
                color=COLORS['text_white'],
                size_hint_y=None,
                height=dp(60),
                font_size=dp(14),
                halign='center'
            ))
            
            # Bilgi mesajı
            info_label = Label(
                text="Dosya başarıyla kaydedildi.\nKonumunu görmek için 'GÖSTER' butonuna basın.",
                color=COLORS['text_gray'],
                size_hint_y=None,
                height=dp(40),
                font_size=dp(11),
                halign='center'
            )
            info_label.bind(size=info_label.setter('text_size'))
            content.add_widget(info_label)
            
            # Konum bilgisi
            path_label = Label(
                text=f"Konum:\n{str(kayit_yolu)}",
                color=COLORS['primary_blue'],
                size_hint_y=None,
                height=dp(60),
                font_size=dp(9),
                halign='center'
            )
            path_label.bind(size=path_label.setter('text_size'))
            content.add_widget(path_label)
            
            button_box = BoxLayout(orientation='horizontal', spacing=dp(10),
                                  size_hint_y=None, height=dp(40))
            
            def show_location(instance):
                import os, subprocess, platform
                try:
                    if platform.system() == "Windows":
                        os.startfile(str(kayit_yolu.parent))
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.call(["open", str(kayit_yolu.parent)])
                    else:  # Linux
                        subprocess.call(["xdg-open", str(kayit_yolu.parent)])
                    popup.dismiss()
                except:
                    self.show_snackbar("❌ Konum açılamadı", "error")
            
            def close_action(instance):
                popup.dismiss()
            
            goster_btn = CompactButton("GÖSTER", color_type="primary", on_press=show_location)
            tamam_btn = CompactButton("TAMAM", color_type="secondary", on_press=close_action)
            
            button_box.add_widget(goster_btn)
            button_box.add_widget(tamam_btn)
            content.add_widget(button_box)
            
            popup = Popup(
                title='📄 Dosya Oluşturuldu',
                content=content,
                size_hint=(0.85, 0.6),
                background_color=COLORS['bg_card']
            )
            popup.open()
            
        except Exception as e:
            self.show_snackbar(f"❌ Paylaşım hatası: {str(e)[:50]}", "error")
    
    def show_pdf_share_options_safe(self, dosya_adi, kayit_yolu):
        """Güvenli PDF paylaşım seçeneklerini göster"""
        try:
            content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
            
            content.add_widget(Label(
                text=f"Dosya Oluşturuldu:\n{dosya_adi}",
                color=COLORS['text_white'],
                size_hint_y=None,
                height=dp(60),
                font_size=dp(14),
                halign='center'
            ))
            
            # Bilgi mesajı
            info_label = Label(
                text="Dosya başarıyla kaydedildi.\n'Dosya Yöneticisi'nden erişebilirsiniz.",
                color=COLORS['text_gray'],
                size_hint_y=None,
                height=dp(40),
                font_size=dp(11),
                halign='center'
            )
            info_label.bind(size=info_label.setter('text_size'))
            content.add_widget(info_label)
            
            # Konum bilgisi
            path_label = Label(
                text=f"Konum: {str(kayit_yolu)[:50]}...",
                color=COLORS['primary_blue'],
                size_hint_y=None,
                height=dp(30),
                font_size=dp(9),
                halign='center'
            )
            path_label.bind(size=path_label.setter('text_size'))
            content.add_widget(path_label)
            
            def close_action(instance):
                popup.dismiss()
            
            close_btn = CompactButton("TAMAM", color_type="primary", on_press=close_action)
            content.add_widget(close_btn)
            
            popup = Popup(
                title='📄 Dosya Oluşturuldu',
                content=content,
                size_hint=(0.8, 0.5),
                background_color=COLORS['bg_card']
            )
            popup.open()
            
        except Exception as e:
            self.show_snackbar(f"❌ Paylaşım hatası: {str(e)[:50]}", "error")

    def kaydet_hesaplama(self, instance):
        if not self.hesaplama_gecmisi:
            self.show_snackbar("❌ Kaydedilecek hesaplama yok!", "error")
            return

        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))

        content.add_widget(Label(
            text="Kaydedilecek dosya adı:",
            color=COLORS['text_white'],
            size_hint_y=None,
            height=dp(30),
            font_size=dp(14)
        ))

        filename_input = CompactTextInput(
            hint_text="Dosya Adı (.json)",
            text=f"hesaplama_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(filename_input)

        def save_action(instance):
            dosya_adi = filename_input.text
            if not dosya_adi:
                self.show_snackbar("❌ Dosya adı boş olamaz!", "error")
                return

            son_hesaplama = self.hesaplama_gecmisi[-1]
            kayit_yolu = self.orifis_kayit.kaydet(son_hesaplama, dosya_adi)

            if kayit_yolu:
                self.show_snackbar(f"✅ Kaydedildi: {kayit_yolu.name}", "success")
                popup.dismiss()
            else:
                self.show_snackbar("❌ Kayıt başarısız!", "error")

        def cancel_action(instance):
            popup.dismiss()

        button_box = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None, height=dp(50))
        button_box.add_widget(CompactButton("İPTAL", color_type="danger", on_press=cancel_action))
        button_box.add_widget(CompactButton("KAYDET", color_type="primary", on_press=save_action))

        content.add_widget(button_box)

        popup = Popup(
            title='💾 Hesaplamayı Kaydet',
            content=content,
            size_hint=(0.8, 0.4),
            background_color=COLORS['bg_card']
        )
        popup.open()

    def yukle_hesaplama(self, instance):
        kayitlar = self.orifis_kayit.listele_kayitlar()

        if not kayitlar:
            self.show_snackbar("❌ Kayıtlı hesaplama bulunamadı!", "error")
            return

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))

        scroll_view = ScrollView(size_hint=(1, 0.8))
        list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        list_layout.bind(minimum_height=list_layout.setter('height'))

        for kayit in kayitlar[:10]:
            btn = CompactButton(
                kayit,
                color_type="secondary",
                on_press=lambda x, k=kayit: self.load_file(k, popup)
            )
            btn.height = dp(40)
            list_layout.add_widget(btn)

        scroll_view.add_widget(list_layout)
        content.add_widget(scroll_view)

        close_btn = CompactButton(
            "KAPAT",
            color_type="danger",
            on_press=lambda x: popup.dismiss()
        )
        content.add_widget(close_btn)

        popup = Popup(
            title='📂 Kayıtlı Hesaplamalar',
            content=content,
            size_hint=(0.7, 0.6),
            background_color=COLORS['bg_card']
        )
        popup.open()

    def load_file(self, dosya_adi, popup):
        data = self.orifis_kayit.yukle(dosya_adi)
        if data:
            try:
                # Geometrik değerler
                D_val_m = float(data.get("D", VARSAYILAN_DEGERLER["D"]))
                d_val_m = float(data.get("d", VARSAYILAN_DEGERLER["d"]))

                D_birim_loaded = data.get("D_birim", "m")
                d_birim_loaded = data.get("d_birim", "m")
                self.D_birim.text = D_birim_loaded
                self.d_birim.text = d_birim_loaded

                D_display = convert_length(D_val_m, "m", D_birim_loaded)
                d_display = convert_length(d_val_m, "m", d_birim_loaded)
                self.D_input.text = f"{D_display:.4f}"
                self.d_input.text = f"{d_display:.4f}"
                self.current_values["D_m"] = D_val_m
                self.current_values["d_m"] = d_val_m

                self.L1_input.text = str(data.get("L1", VARSAYILAN_DEGERLER["L1"]))
                self.L2_input.text = str(data.get("L2", VARSAYILAN_DEGERLER["L2"]))
                self.C0_input.text = str(data.get("C0_baslangic", VARSAYILAN_DEGERLER["C0_baslangic"]))

                # Basınç değerleri
                self.current_values["p1_pa"] = float(data.get("p1", VARSAYILAN_DEGERLER["p1"]))
                self.current_values["p2_pa"] = float(data.get("p2", VARSAYILAN_DEGERLER["p2"]))
                self.update_pressure_display()
                self.temp_input.text = f"{float(data.get('sicaklik', VARSAYILAN_DEGERLER['sicaklik'])):.2f}"
                self.gaz_spinner.text = data.get("gaz", VARSAYILAN_DEGERLER["gaz_tipi"])
                self.max_iter_input.text = str(data.get("max_iter", VARSAYILAN_DEGERLER["max_iter"]))
                self.epsilon_input.text = str(data.get("epsilon", VARSAYILAN_DEGERLER["epsilon"]))
                self.density_input.text = str(data.get("yogunluk_manuel", VARSAYILAN_DEGERLER["yogunluk_manuel"]))
                self.viscosity_input.text = str(data.get("viskozite_manuel", VARSAYILAN_DEGERLER["viskozite_manuel"]))

                # Modlar
                basinc_mode = data.get("basinc_mode", "ΔP Modu")
                self.on_pressure_mode_change(basinc_mode)

                yogunluk_mode = data.get("yogunluk_mode", "Manuel")
                self.on_yogunluk_mode_change(yogunluk_mode.title())

                viskozite_mode = data.get("viskozite_mode", "Manuel")
                self.on_viskozite_mode_change(viskozite_mode.title())

                # Atmosferik mod
                atmosferik_mode = data.get("atmosferik_mode", False)
                self.atmosferik_check.active = atmosferik_mode

                popup.dismiss()

                self.show_snackbar(f"✅ Yüklendi: {dosya_adi}", "success")
                self.calculate_beta()
                self.on_gas_change(None, data.get("gaz", VARSAYILAN_DEGERLER["gaz_tipi"]))
                self.check_and_disable_atmosferic()

            except Exception as e:
                print(f"Yükleme işlem hatası: {e}")
                self.show_snackbar(f"❌ Yükleme hatası: {str(e)}", "error")

    def load_defaults(self, instance):
        try:
            # Geometrik değerler
            D_val_m = VARSAYILAN_DEGERLER["D"]
            d_val_m = VARSAYILAN_DEGERLER["d"]
            D_display = convert_length(D_val_m, "m", self.D_birim.text)
            d_display = convert_length(d_val_m, "m", self.d_birim.text)
            self.D_input.text = f"{D_display:.4f}"
            self.d_input.text = f"{d_display:.4f}"
            self.current_values["D_m"] = D_val_m
            self.current_values["d_m"] = d_val_m

            self.L1_input.text = str(VARSAYILAN_DEGERLER["L1"])
            self.L2_input.text = str(VARSAYILAN_DEGERLER["L2"])
            self.C0_input.text = str(VARSAYILAN_DEGERLER["C0_baslangic"])

            # Basınç değerleri
            self.current_values["p1_pa"] = VARSAYILAN_DEGERLER["p1"]
            self.current_values["p2_pa"] = VARSAYILAN_DEGERLER["p2"]
            self.update_pressure_display()
            self.temp_input.text = f"{VARSAYILAN_DEGERLER['sicaklik']:.2f}"
            self.gaz_spinner.text = VARSAYILAN_DEGERLER["gaz_tipi"]
            self.max_iter_input.text = str(VARSAYILAN_DEGERLER["max_iter"])
            self.epsilon_input.text = str(VARSAYILAN_DEGERLER["epsilon"])
            self.density_input.text = str(VARSAYILAN_DEGERLER["yogunluk_manuel"])
            self.viscosity_input.text = str(VARSAYILAN_DEGERLER["viskozite_manuel"])
            self.density_atmosferik.text = str(VARSAYILAN_DEGERLER["yogunluk_atmosferik"])
            self.viscosity_atmosferik.text = str(VARSAYILAN_DEGERLER["viskozite_atmosferik"])

            # Modları sıfırla
            self.on_pressure_mode_change('ΔP Modu')
            self.on_yogunluk_mode_change("Manuel")
            self.on_viskozite_mode_change("Manuel")
            self.atmosferik_check.active = False

            self.calculate_beta()
            self.on_gas_change(None, VARSAYILAN_DEGERLER["gaz_tipi"])
            self.check_and_disable_atmosferic()

            self.result_text.text = "✅ Excel varsayılan değerleri yüklendi!\n\n═══════════════════════════════\n   ORİFİS HESAPLAYICI v9.8\n═══════════════════════════════"

            self.show_snackbar("✅ Excel değerleri yüklendi (manuel mod)", "success")
        except Exception as e:
            print(f"Varsayılan yükleme hatası: {e}")

    def temizle(self, instance):
        self.D_input.text = ""
        self.d_input.text = ""
        self.L1_input.text = ""
        self.L2_input.text = ""
        self.C0_input.text = ""
        self.delta_p_input.text = ""
        self.p1_input.text = ""
        self.p2_input.text = ""
        self.temp_input.text = ""
        self.max_iter_input.text = ""
        self.epsilon_input.text = ""
        self.density_input.text = ""
        self.viscosity_input.text = ""

        self.current_values["D_m"] = 0
        self.current_values["d_m"] = 0
        self.current_values["p1_pa"] = 0
        self.current_values["p2_pa"] = 0

        self.atmosferik_check.active = False

        self.beta_label.text = 'β = Hesaplanacak'
        self.beta_label.color = COLORS['success_light']

        self.result_text.text = """🧹 Tüm alanlar temizlendi!

1. Değerleri girin
2. 'HESAPLAYIN' butonuna tıklayın
3. Sonuçlar burada görünecek

Designed by Lutfi

═══════════════════════════════
   ORİFİS HESAPLAYICI v9.8
═══════════════════════════════"""

        self.status_label.text = "⏳ Değerleri girin ve HESAPLAYIN!"
        self.status_label.color = COLORS['primary_blue']
        self.save_btn.disabled = True
        self.anlik_hesap_btn.disabled = True

        self.show_snackbar("🧹 Tüm alanlar temizlendi!", "warning")
        
        # Sıvı/gaz kontrolünü yeniden yap
        self.check_and_disable_atmosferic()

    def show_help(self, instance):
        help_text = """⚡ ORİFİS DEBİ HESAPLAYICI v9.8

📌 KULLANIM:
1. Boru ve orifis ölçülerini girin
2. Basınç değerlerini seçin (ΔP veya Giriş/Çıkış)
3. Akışkan tipini seçin
4. Yoğunluk ve viskozite modunu seçin
5. 'HESAPLAYIN' butonuna tıklayın

🌍 ATMOSFERİK MOD:
• Sıvı seçildiğinde OTOMATİK olarak devre dışı bırakılır
• Gazlar için aktif/pasif yapılabilir
• Aktif olduğunda: sıcaklık=0°C, basınç=1 atm
• Yoğunluk ve viskozite otomatik olarak atmosferik değerlere ayarlanır

🔄 BİRİM DÖNÜŞÜMLERİ:
• Basınç birimi değiştiğinde tüm değerler otomatik güncellenir
• Uzunluk birimi değiştiğinde değerler otomatik çevrilir
• Birimler: Pa, kPa, bar, atm, mmH2O, kg/cm²

📊 SONUÇLAR:
• Gerçek debi (m³/h) - ölçülen şartlarda
• Normal debi (Nm³/h) - 0°C, 1 atm şartlarında (SADECE GAZLAR)
• Kütlesel debi (kg/h)
• Yoğunluk değerleri

🔄 YOĞUNLUK MODLARI:
• SIVILAR: Sadece Manuel mod aktif
• GAZLAR: Otomatik, Manuel, Atmosferik
• OTOMATİK: İdeal gaz denklemi ile hesaplanır
• MANUEL: Elle girilen değer kullanılır
• ATMOSFERİK: 0°C, 1 atm'deki yoğunluk kullanılır

🔄 VİSKOZİTE MODLARI:
• SIVILAR: Sadece Manuel mod aktif
• GAZLAR: Otomatik, Manuel, Atmosferik
• OTOMATİK: Sıcaklıkla değişen viskozite
• MANUEL: Elle girilen değer
• ATMOSFERİK: Standart viskozite değeri

🔢 ANLIK HESAP:
• Dizayn hesabı yapıldıktan sonra aktif olur
• Popup penceresinde değerler girilir
• Kaydet butonu ile sonuçlar kaydedilebilir

🎛️ YENİ ÖZELLİKLER:
• Yazı boyutu ayarlama (8-20 dp)
• Sonuç kutusu yüksekliği ayarlama (400-1000 dp)
• Anlık hesap için ayrı yazı boyutu ayarı
• PDF oluşturma ve paylaşım özelliği

⚠️ NOTLAR:
• β oranı (d/D) 0.2-0.75 arasında olmalı
• Mobil uyumlu (Vivo X200 FE optimize)

👨‍💻 GELİŞTİRİCİ: Lütfi
"""

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))

        scroll_view = ScrollView()
        help_label = Label(text=help_text,
                          font_size=dp(11),
                          color=COLORS['text_white'],
                          size_hint_y=None,
                          halign='left')
        help_label.bind(texture_size=help_label.setter('size'))

        scroll_view.add_widget(help_label)

        content.add_widget(scroll_view)

        close_btn = CompactButton("TAMAM", color_type="primary",
                                 on_press=lambda x: popup.dismiss())
        content.add_widget(close_btn)

        popup = Popup(title='❓ Yardım',
                     content=content,
                     size_hint=(0.9, 0.8),
                     background_color=COLORS['bg_card'],
                     auto_dismiss=False)
        popup.open()

    def add_custom_gas(self, instance):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))

        name_input = CompactTextInput(hint_text="Akışkan Adı")
        formula_input = CompactTextInput(hint_text="Formül")
        mol_input = CompactTextInput(hint_text="Mol. Ağırlık (g/mol)")
        visc_input = CompactTextInput(hint_text="Viskozite 20°C (Pa·s)", text="1.16e-05")
        dens_input = CompactTextInput(hint_text="Yoğunluk 20°C (kg/m³)", text="1.2")
        atmos_dens_input = CompactTextInput(hint_text="Atmosferik Yoğunluk (kg/m³)", text="0.761")
        desc_input = CompactTextInput(hint_text="Açıklama")

        gas_type = CompactSpinner(text='gaz', values=('gaz', 'sıvı'))

        def save_gas(instance):
            name = name_input.text.strip()
            formula = formula_input.text.strip()
            mol_str = mol_input.text.strip()
            visc_str = visc_input.text.strip()
            dens_str = dens_input.text.strip()
            atmos_dens_str = atmos_dens_input.text.strip()
            gas_tip = gas_type.text
            desc = desc_input.text.strip()

            if not name:
                self.show_snackbar("❌ Akışkan adı boş olamaz!", "error")
                return

            try:
                mol_weight = float(mol_str) if mol_str else 0
                viscosity = float(visc_str) if visc_str else 1e-05
                density = float(dens_str) if dens_str else 1.2
                atmosferik_density = float(atmos_dens_str) if atmos_dens_str else 1.2
            except ValueError:
                self.show_snackbar("❌ Sayısal değerler geçerli olmalı!", "error")
                return

            new_gas = {
                "formula": formula,
                "mol_agirligi": mol_weight,
                "viskozite_293": viscosity,
                "yogunluk_293": density,
                "atmosferik_yogunluk": atmosferik_density,
                "atmosferik_viskozite": viscosity,
                "aciklama": desc,
                "tip": gas_tip
            }

            if self.orifis_kayit.add_custom_gas(name, new_gas):
                self.update_gaz_dropdown()
                popup.dismiss()
                self.show_snackbar(f"✅ '{name}' eklendi!", "success")
            else:
                self.show_snackbar("❌ Kaydetme başarısız!", "error")

        def cancel_action(instance):
            popup.dismiss()

        content.add_widget(name_input)
        content.add_widget(formula_input)
        content.add_widget(mol_input)
        content.add_widget(visc_input)
        content.add_widget(dens_input)
        content.add_widget(atmos_dens_input)
        content.add_widget(gas_type)
        content.add_widget(desc_input)

        button_box = BoxLayout(orientation='horizontal', spacing=dp(10))
        button_box.add_widget(CompactButton("İPTAL", color_type="danger", on_press=cancel_action))
        button_box.add_widget(CompactButton("KAYDET", color_type="primary", on_press=save_gas))

        content.add_widget(button_box)

        scroll_view = ScrollView()
        scroll_view.add_widget(content)

        popup = Popup(title='➕ Yeni Akışkan Ekle',
                     content=scroll_view,
                     size_hint=(0.9, 0.9),
                     background_color=COLORS['bg_card'],
                     auto_dismiss=False)
        popup.open()

    def show_snackbar(self, message, type="info"):
        colors = {
            "success": COLORS['success_green'],
            "error": COLORS['error_red'],
            "warning": COLORS['warning_orange'],
            "info": COLORS['primary_blue']
        }

        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=message, color=COLORS['text_white']))

        popup = Popup(title='',
                     content=content,
                     size_hint=(0.8, 0.15),
                     background_color=colors[type])
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 3)

class OrifisApp(App):
    def build(self):
        # Android'de tam ekran yap (isteğe bağlı)
        if current_platform == "Android":
            from kivy.utils import platform as kivy_platform  # farklı isim kullan
            if kivy_platform == 'android':
                from jnius import autoclass
                try:
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    activity = PythonActivity.mActivity
                    WindowManager = autoclass('android.view.WindowManager')
                    LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
                    
                    # Tam ekran yap
                    activity.getWindow().addFlags(LayoutParams.FLAG_FULLSCREEN)
                except Exception as e:
                    print(f"Tam ekran hatası: {e}")
        
        # Arka plan rengini ayarla (splash ile aynı renk)
        Window.clearcolor = COLORS['bg_dark']
        
        # Ekran yönünü kilitle (portrait)
        Window.allow_screensaver = False
        
        sm = ScreenManager()
        main_screen = MainScreen()
        sm.add_widget(main_screen)
        return sm
    
    def on_start(self):
        """Uygulama başladığında çalışır"""
        if current_platform == "Android":
            # Android izinlerini kontrol et
            self.check_android_permissions()
        
        # Status bar'ı güncelle
        if hasattr(self.root, 'children'):
            for screen in self.root.children:
                if hasattr(screen, 'status_label'):
                    screen.status_label.text = "✅ Uygulama başlatıldı!"
                    screen.status_label.color = COLORS['success_light']
    
    def check_android_permissions(self):
        """Android izinlerini kontrol et"""
        if current_platform != "Android":
            return
            
        try:
            from android.permissions import check_permission, Permission
            
            # Gerekli izinleri kontrol et
            required_perms = [
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ]
            
            for perm in required_perms:
                if not check_permission(perm):
                    print(f"İzin eksik: {perm}")
                    # İsteme mekanizması burada olabilir
                    
        except Exception as e:
            print(f"İzin kontrol hatası: {e}")
    
    def on_pause(self):
        """Uygulama pause olduğunda"""
        return True
    
    def on_resume(self):
        """Uygulama resume olduğunda"""
        if current_platform == "Android":
            # Storage izinlerini tekrar kontrol et
            self.check_android_permissions()

if __name__ == '__main__':
    # Uygulamayı başlat
    try:
        app = OrifisApp()
        app.run()
    except Exception as e:
        print(f"Uygulama başlatma hatası: {e}")
        # Hata durumunda log kaydet
        import traceback
        traceback.print_exc()

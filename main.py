import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.checkbox import CheckBox
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
import json
import math
from datetime import datetime
from pathlib import Path
import platform

# Platforma göre kayıt dizinini belirle
if platform.system() == "Android":
    BASE_DIR = Path("/storage/emulated/0/OrifisApp")
else:
    BASE_DIR = Path(".")

SAVE_DIR = BASE_DIR / "orifis_kayitlar"
CUSTOM_GASES_FILE = BASE_DIR / "custom_gases.json"

# Dizinleri oluştur
SAVE_DIR.mkdir(parents=True, exist_ok=True)

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
        "atmosferik_yogunluk": 0.761,
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
    "sicaklik": 273.15,
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

class OrifisHesap:
    def __init__(self):
        self.save_dir = SAVE_DIR
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.gazlar_dosyasi = CUSTOM_GASES_FILE
        self.custom_gazlar = self.load_custom_gases()

    def load_custom_gases(self):
        if self.gazlar_dosyasi.exists():
            try:
                with open(self.gazlar_dosyasi, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Gaz yükleme hatası: {e}")
                return {}
        return {}

    def save_custom_gases(self):
        try:
            with open(self.gazlar_dosyasi, 'w', encoding='utf-8') as f:
                json.dump(self.custom_gazlar, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Gaz kaydetme hatası: {e}")
            return False

    def add_custom_gas(self, name, properties):
        self.custom_gazlar[name] = properties
        return self.save_custom_gases()

    def remove_custom_gas(self, name):
        if name in self.custom_gazlar:
            del self.custom_gazlar[name]
            return self.save_custom_gases()
        return False

    def kaydet(self, data, dosya_adi=None):
        try:
            if not dosya_adi:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dosya_adi = f"orifis_{timestamp}.json"

            if not dosya_adi.endswith('.json'):
                dosya_adi += '.json'

            kayit_yolu = self.save_dir / dosya_adi

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
                "sicaklik": data.get("sicaklik_input", 273.15),
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
            kayit_yolu = self.save_dir / dosya_adi
            if kayit_yolu.exists():
                with open(kayit_yolu, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Yükleme hatası: {e}")
        return None

    def listele_kayitlar(self):
        try:
            kayitlar = []
            for dosya in self.save_dir.glob("*.json"):
                kayitlar.append(dosya.name)
            return sorted(kayitlar, reverse=True)
        except Exception as e:
            print(f"Listeleme hatası: {e}")
            return []

# === BİRİM DÖNÜŞÜM FONKSİYONLARI ===
def convert_length(value, from_unit, to_unit="m"):
    """Uzunluk birimi dönüşümü"""
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
    """Basınç birimi dönüşümü"""
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
    """Sıcaklık birimi dönüşümü"""
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

class MinimalTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = get_color_from_hex('#2D3748')
        self.foreground_color = get_color_from_hex('#FFFFFF')
        self.cursor_color = get_color_from_hex('#4299E1')
        self.multiline = False
        self.padding = [dp(8), dp(8)]
        self.font_size = sp(12)
        self.size_hint_y = None
        self.height = dp(36)
        
    def on_focus(self, instance, value):
        if value:
            self.background_color = get_color_from_hex('#4A5568')
        else:
            self.background_color = get_color_from_hex('#2D3748')

class MinimalButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = get_color_from_hex('#3182CE')
        self.color = get_color_from_hex('#FFFFFF')
        self.font_size = sp(11)
        self.size_hint_y = None
        self.height = dp(36)
        self.background_normal = ''
        self.background_down = ''
        
    def on_press(self):
        self.background_color = get_color_from_hex('#2C5282')
        
    def on_release(self):
        self.background_color = get_color_from_hex('#3182CE')

class ColorfulButton(Button):
    def __init__(self, color_hex='#3182CE', **kwargs):
        super().__init__(**kwargs)
        self.color_hex = color_hex
        self.background_color = get_color_from_hex(color_hex)
        self.color = get_color_from_hex('#FFFFFF')
        self.font_size = sp(12)
        self.size_hint_y = None
        self.height = dp(40)
        self.background_normal = ''
        self.background_down = ''
        
    def on_press(self):
        self.background_color = get_color_from_hex('#2C5282')
        
    def on_release(self):
        self.background_color = get_color_from_hex(self.color_hex)

class SecondaryButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = get_color_from_hex('#4A5568')
        self.color = get_color_from_hex('#FFFFFF')
        self.font_size = sp(11)
        self.size_hint_y = None
        self.height = dp(36)
        self.background_normal = ''
        self.background_down = ''

class MinimalLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = get_color_from_hex('#FFFFFF')
        self.font_size = sp(12)
        self.size_hint_y = None
        self.height = dp(30)
        self.halign = 'left'
        self.valign = 'middle'

class SectionTitle(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = get_color_from_hex('#63B3ED')
        self.font_size = sp(13)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(30)
        self.halign = 'left'

class BetaLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = get_color_from_hex('#68D391')
        self.font_size = sp(14)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(36)
        self.halign = 'left'
        self.valign = 'middle'

class StatusLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = sp(11)
        self.size_hint_y = None
        self.height = dp(30)
        self.halign = 'center'
        self.valign = 'middle'
        self.color = get_color_from_hex('#90CDF4')
        
    def set_status(self, message, status_type="info"):
        colors = {
            "info": "#90CDF4",
            "success": "#68D391",
            "warning": "#ECC94B",
            "error": "#FC8181"
        }
        self.color = get_color_from_hex(colors[status_type])
        self.text = message

class ColorfulSectionBox(BoxLayout):
    def __init__(self, color_hex='#1A202C', **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(8)
        self.padding = dp(10)
        self.size_hint_y = None
        with self.canvas.before:
            Color(rgba=get_color_from_hex(color_hex))
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
        
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class RadioButtonGroup(BoxLayout):
    def __init__(self, options=[], default="", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(30)
        self.buttons = {}
        self.selected_value = default
        
        for option in options:
            btn_layout = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_x=None)
            btn_layout.width = dp(100)
            
            radio = ToggleButton(group=f'group_{id(self)}', 
                               size_hint_x=0.3,
                               state='down' if (option == default) else 'normal')
            radio.bind(state=lambda instance, value, opt=option: self.on_radio_active(instance, value, opt))
            
            label = Label(text=option, 
                         size_hint_x=0.7,
                         color=get_color_from_hex('#FFFFFF'),
                         font_size=sp(11))
            
            btn_layout.add_widget(radio)
            btn_layout.add_widget(label)
            self.add_widget(btn_layout)
            self.buttons[option] = radio
    
    def on_radio_active(self, instance, value, option):
        if value == 'down':
            self.selected_value = option
            # Diğer butonları kapat
            for opt, btn in self.buttons.items():
                if opt != option:
                    btn.state = 'normal'

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        self.orifis_kayit = OrifisHesap()
        self.current_values = {
            "D_m": VARSAYILAN_DEGERLER["D"],
            "d_m": VARSAYILAN_DEGERLER["d"],
            "p1_pa": VARSAYILAN_DEGERLER["p1"],
            "p2_pa": VARSAYILAN_DEGERLER["p2"]
        }
        self.basinc_mode_var = "delta"
        self.yogunluk_mode_var = "manuel"
        self.viskozite_mode_var = "manuel"
        self.atmosferik_mode_var = False
        self.hesaplama_gecmisi = []
        self.anlik_hesap_data = None
        
        self.setup_ui()
        

    def setup_ui(self):
        # Ana layout
        main_layout = BoxLayout(orientation='vertical', spacing=dp(5))
        
        # ScrollView
        scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        content_layout = BoxLayout(orientation='vertical', spacing=dp(8), 
                                  size_hint_y=None, padding=dp(8))
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Başlık
        title_box = ColorfulSectionBox(color_hex='#2D3748', height=dp(70))
        title_box.add_widget(Label(text='ORİFİS DEBİ HESAPLAYICI', 
                                  font_size=sp(16), bold=True,
                                  color=get_color_from_hex('#63B3ED'),
                                  halign='center'))
        title_box.add_widget(Label(text='v9.7 • Designed by Lutfi • ATM ATIK',
                                  font_size=sp(9), italic=True,
                                  color=get_color_from_hex('#A0AEC0'),
                                  halign='center'))
        content_layout.add_widget(title_box)
        
        # 📏 GEOMETRİK ÖLÇÜLER
        geometric_box = ColorfulSectionBox(color_hex='#2D3748', height=dp(180))
        geometric_box.add_widget(SectionTitle(text='📏 GEOMETRİK ÖLÇÜLER'))
        
        # D satırı
        D_row = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        D_row.add_widget(MinimalLabel(text='D:', size_hint_x=0.2))
        self.D_input = MinimalTextInput(text=f"{VARSAYILAN_DEGERLER['D']:.6f}", size_hint_x=0.5)
        self.D_birim = Spinner(text='m', values=('m', 'mm', 'cm', 'inch'), 
                              size_hint_x=0.3, background_color=get_color_from_hex('#2D3748'),
                              color=get_color_from_hex('#FFFFFF'))
        D_row.add_widget(self.D_input)
        D_row.add_widget(self.D_birim)
        geometric_box.add_widget(D_row)
        
        # d satırı
        d_row = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        d_row.add_widget(MinimalLabel(text='d:', size_hint_x=0.2))
        self.d_input = MinimalTextInput(text=f"{VARSAYILAN_DEGERLER['d']:.6f}", size_hint_x=0.5)
        self.d_birim = Spinner(text='m', values=('m', 'mm', 'cm', 'inch'), 
                              size_hint_x=0.3, background_color=get_color_from_hex('#2D3748'),
                              color=get_color_from_hex('#FFFFFF'))
        d_row.add_widget(self.d_input)
        d_row.add_widget(self.d_birim)
        geometric_box.add_widget(d_row)
        
        # L1, L2, C0 satırı
        l_row = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        l_row.add_widget(MinimalLabel(text='L1:', size_hint_x=0.2))
        self.L1_input = MinimalTextInput(text=str(VARSAYILAN_DEGERLER['L1']), size_hint_x=0.25)
        l_row.add_widget(MinimalLabel(text='L2:', size_hint_x=0.2))
        self.L2_input = MinimalTextInput(text=str(VARSAYILAN_DEGERLER['L2']), size_hint_x=0.25)
        l_row.add_widget(MinimalLabel(text='C0:', size_hint_x=0.2))
        self.C0_input = MinimalTextInput(text=str(VARSAYILAN_DEGERLER['C0_baslangic']), size_hint_x=0.25)
        l_row.add_widget(self.L1_input)
        l_row.add_widget(self.L2_input)
        l_row.add_widget(self.C0_input)
        geometric_box.add_widget(l_row)
        
        # Beta değeri
        self.beta_label = BetaLabel(text='β = Hesaplanacak')
        geometric_box.add_widget(self.beta_label)
        
        content_layout.add_widget(geometric_box)
        
        # 📊 BASINÇ DEĞERLERİ
        pressure_box = ColorfulSectionBox(color_hex='#2A4365', height=dp(180))
        pressure_box.add_widget(SectionTitle(text='📊 BASINÇ DEĞERLERİ'))
        
        # Basınç modu
        pressure_mode_box = BoxLayout(orientation='horizontal', spacing=dp(5), 
                                     size_hint_y=None, height=dp(36))
        self.delta_mode_btn = ToggleButton(text='ΔP Modu', group='pressure_mode', 
                                          state='down', size_hint_x=0.5)
        self.absolute_mode_btn = ToggleButton(text='G/Ç Modu', group='pressure_mode',
                                             size_hint_x=0.5)
        pressure_mode_box.add_widget(self.delta_mode_btn)
        pressure_mode_box.add_widget(self.absolute_mode_btn)
        pressure_box.add_widget(pressure_mode_box)
        
        # ΔP satırı
        delta_p_row = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        delta_p_row.add_widget(MinimalLabel(text='ΔP:', size_hint_x=0.2))
        self.delta_p_input = MinimalTextInput(text=f"{VARSAYILAN_DEGERLER['delta_p']:.2f}", size_hint_x=0.6)
        delta_p_label = MinimalLabel(text='mmH₂O', size_hint_x=0.2, color=get_color_from_hex('#63B3ED'))
        delta_p_row.add_widget(self.delta_p_input)
        delta_p_row.add_widget(delta_p_label)
        pressure_box.add_widget(delta_p_row)
        
        # p1 satırı
        p1_row = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        p1_row.add_widget(MinimalLabel(text='p1:', size_hint_x=0.2))
        self.p1_input = MinimalTextInput(text=f"{VARSAYILAN_DEGERLER['p1']:.2f}", size_hint_x=0.5)
        self.pressure_unit = Spinner(text='Pa', values=('Pa', 'kPa', 'bar', 'atm', 'mmH2O', 'kg/cm2'),
                                    size_hint_x=0.3, background_color=get_color_from_hex('#2D3748'),
                                    color=get_color_from_hex('#FFFFFF'))
        p1_row.add_widget(self.p1_input)
        p1_row.add_widget(self.pressure_unit)
        pressure_box.add_widget(p1_row)
        
        # p2 satırı
        p2_row = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        p2_row.add_widget(MinimalLabel(text='p2:', size_hint_x=0.2))
        self.p2_input = MinimalTextInput(text=f"{VARSAYILAN_DEGERLER['p2']:.2f}", 
                                       size_hint_x=0.5,
                                       background_color=get_color_from_hex('#2D3748'),
                                       disabled=True)
        p2_label = MinimalLabel(text='Pa', 
                              size_hint_x=0.3,
                              color=get_color_from_hex('#63B3ED'))
        p2_row.add_widget(self.p2_input)
        p2_row.add_widget(p2_label)
        pressure_box.add_widget(p2_row)
        
        content_layout.add_widget(pressure_box)
        
        # 🌡️ AKIŞKAN ÖZELLİKLERİ (Güncellenmiş)
        fluid_box = ColorfulSectionBox(color_hex='#234E52', height=dp(420))
        fluid_box.add_widget(SectionTitle(text='🌡️ AKIŞKAN ÖZELLİKLERİ'))
        
        # Gaz seçimi
        all_gases = {**GAZLAR, **self.orifis_kayit.custom_gazlar}
        gaz_row = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        gaz_row.add_widget(MinimalLabel(text='Akışkan:', size_hint_x=0.25))
        self.gaz_spinner = Spinner(text=VARSAYILAN_DEGERLER['gaz_tipi'],
                                  values=list(all_gases.keys()),
                                  size_hint_x=0.75, 
                                  background_color=get_color_from_hex('#2D3748'),
                                  color=get_color_from_hex('#FFFFFF'))
        gaz_row.add_widget(self.gaz_spinner)
        fluid_box.add_widget(gaz_row)
        
        # Sıcaklık
        temp_row = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        temp_row.add_widget(MinimalLabel(text='Sıcaklık:', size_hint_x=0.25))
        self.temp_input = MinimalTextInput(text=f"{VARSAYILAN_DEGERLER['sicaklik']:.2f}", size_hint_x=0.4)
        self.temp_unit = Spinner(text='K', values=('K', '°C', '°F'),
                                size_hint_x=0.35, 
                                background_color=get_color_from_hex('#2D3748'),
                                color=get_color_from_hex('#FFFFFF'))
        temp_row.add_widget(self.temp_input)
        temp_row.add_widget(self.temp_unit)
        fluid_box.add_widget(temp_row)
        
        # Atmosferik checkbox - GÖRSELDEKİ GİBİ
        atmosferic_row = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        self.atmosferik_check = CheckBox(size_hint_x=0.15, active=False)
        atmos_label = MinimalLabel(text='Atmosferik (T=0°C, P=1 atm)', 
                                 font_size=sp(11), 
                                 size_hint_x=0.85,
                                 color=get_color_from_hex('#90CDF4'))
        atmosferic_row.add_widget(self.atmosferik_check)
        atmosferic_row.add_widget(atmos_label)
        fluid_box.add_widget(atmosferic_row)
        
        # Yoğunluk bölümü
        density_section = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(120))
        density_section.add_widget(MinimalLabel(text='Yoğunluk Modu:', font_size=sp(12), color=get_color_from_hex('#c9d1d9')))
        
        # Yoğunluk radio group - GÖRSELDEKİ GİBİ
        self.yogunluk_radio_group = RadioButtonGroup(
            options=['Otomatik', 'Manuel', 'Atmosferik'],
            default='Manuel'
        )
        density_section.add_widget(self.yogunluk_radio_group)
        
        # Yoğunluk değerleri
        density_value_box = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        density_value_box.add_widget(MinimalLabel(text='Yoğunluk:', size_hint_x=0.25))
        self.density_input = MinimalTextInput(text=str(VARSAYILAN_DEGERLER['yogunluk_manuel']), 
                                           size_hint_x=0.45,
                                           background_color=get_color_from_hex('#2A4365'))
        density_label = MinimalLabel(text='kg/m³', 
                                   size_hint_x=0.3,
                                   color=get_color_from_hex('#63B3ED'))
        density_value_box.add_widget(self.density_input)
        density_value_box.add_widget(density_label)
        density_section.add_widget(density_value_box)
        
        atmos_density_row = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        atmos_density_row.add_widget(MinimalLabel(text='Atmosferik:', size_hint_x=0.25))
        self.atmos_density_input = MinimalTextInput(text=str(VARSAYILAN_DEGERLER['yogunluk_atmosferik']),
                                                 size_hint_x=0.45, 
                                                 disabled=True,
                                                 background_color=get_color_from_hex('#4A5568'))
        atmos_density_label = MinimalLabel(text='kg/m³', 
                                         size_hint_x=0.3,
                                         color=get_color_from_hex('#A0AEC0'))
        atmos_density_row.add_widget(self.atmos_density_input)
        atmos_density_row.add_widget(atmos_density_label)
        density_section.add_widget(atmos_density_row)
        
        fluid_box.add_widget(density_section)
        
        # Viskozite bölümü
        viscosity_section = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(120))
        viscosity_section.add_widget(MinimalLabel(text='Viskozite Modu:', font_size=sp(12), color=get_color_from_hex('#c9d1d9')))
        
        # Viskozite radio group - GÖRSELDEKİ GİBİ
        self.viskozite_radio_group = RadioButtonGroup(
            options=['Otomatik', 'Manuel', 'Atmosferik'],
            default='Manuel'
        )
        viscosity_section.add_widget(self.viskozite_radio_group)
        
        # Viskozite değerleri
        viscosity_row = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        viscosity_row.add_widget(MinimalLabel(text='Viskozite:', size_hint_x=0.25))
        self.viscosity_input = MinimalTextInput(text=str(VARSAYILAN_DEGERLER['viskozite_manuel']), 
                                             size_hint_x=0.45,
                                             background_color=get_color_from_hex('#2A4365'))
        viscosity_label = MinimalLabel(text='Pa·s', 
                                     size_hint_x=0.3,
                                     color=get_color_from_hex('#63B3ED'))
        viscosity_row.add_widget(self.viscosity_input)
        viscosity_row.add_widget(viscosity_label)
        viscosity_section.add_widget(viscosity_row)
        
        atmos_viscosity_row = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        atmos_viscosity_row.add_widget(MinimalLabel(text='Atmosferik:', size_hint_x=0.25))
        self.atmos_viscosity_input = MinimalTextInput(text=str(VARSAYILAN_DEGERLER['viskozite_atmosferik']),
                                                   size_hint_x=0.45, 
                                                   disabled=True,
                                                   background_color=get_color_from_hex('#4A5568'))
        atmos_viscosity_label = MinimalLabel(text='Pa·s', 
                                           size_hint_x=0.3,
                                           color=get_color_from_hex('#A0AEC0'))
        atmos_viscosity_row.add_widget(self.atmos_viscosity_input)
        atmos_viscosity_row.add_widget(atmos_viscosity_label)
        viscosity_section.add_widget(atmos_viscosity_row)
        
        fluid_box.add_widget(viscosity_section)
        
        content_layout.add_widget(fluid_box)
        
        # ⚙️ İLERİ AYARLAR
        advanced_box = ColorfulSectionBox(color_hex='#553C9A', height=dp(120))
        advanced_box.add_widget(SectionTitle(text='⚙️ İLERİ AYARLAR'))
        
        # Max Iter ve Epsilon satırı
        advanced_row = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(36))
        
        # Max Iterasyon kısmı
        max_iter_box = BoxLayout(orientation='vertical', spacing=dp(2), size_hint_x=0.4)
        max_iter_label = MinimalLabel(text='Max İterasyon:', font_size=sp(10), color=get_color_from_hex('#D6BCFA'))
        self.max_iter_input = MinimalTextInput(
            text=str(VARSAYILAN_DEGERLER['max_iter']), 
            font_size=sp(14),
            halign='center',
            background_color=get_color_from_hex('#44337A')
        )
        max_iter_box.add_widget(max_iter_label)
        max_iter_box.add_widget(self.max_iter_input)
        
        # Hassasiyet kısmı
        epsilon_box = BoxLayout(orientation='vertical', spacing=dp(2), size_hint_x=0.4)
        epsilon_label = MinimalLabel(text='Hassasiyet (ε):', font_size=sp(10), color=get_color_from_hex('#D6BCFA'))
        self.epsilon_input = MinimalTextInput(
            text=str(VARSAYILAN_DEGERLER['epsilon']), 
            font_size=sp(14),
            halign='center',
            background_color=get_color_from_hex('#44337A')
        )
        epsilon_box.add_widget(epsilon_label)
        epsilon_box.add_widget(self.epsilon_input)
        
        advanced_row.add_widget(max_iter_box)
        advanced_row.add_widget(epsilon_box)
        advanced_box.add_widget(advanced_row)
        
        # Açıklama metni
        explanation_label = MinimalLabel(
            text='Yakınsama kontrolü için iterasyon sayısı ve hassasiyet değeri',
            font_size=sp(9),
            color=get_color_from_hex('#B794F4'),
            halign='center'
        )
        advanced_box.add_widget(explanation_label)
        
        content_layout.add_widget(advanced_box)
        
        # 🚀 HESAPLA BUTONU
        self.calc_btn = ColorfulButton(
            text='🚀 HESAPLA', 
            size_hint_y=None, 
            height=dp(45), 
            color_hex='#38A169',
            font_size=sp(14)
        )
        content_layout.add_widget(self.calc_btn)
        
        # BUTON SATIRLARI
        button_row1 = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        self.save_btn = ColorfulButton(text='💾 KAYDET', disabled=True, color_hex='#3182CE')
        self.load_btn = ColorfulButton(text='📂 YÜKLE', color_hex='#D69E2E')
        self.clear_btn = ColorfulButton(text='🧹 TEMİZLE', color_hex='#E53E3E')
        button_row1.add_widget(self.save_btn)
        button_row1.add_widget(self.load_btn)
        button_row1.add_widget(self.clear_btn)
        content_layout.add_widget(button_row1)
        
        button_row2 = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        self.default_btn = ColorfulButton(text='🔄 VARS.', color_hex='#805AD5')
        self.help_btn = ColorfulButton(text='❓ YARDIM', color_hex='#4299E1')
        self.add_gas_btn = ColorfulButton(text='➕ AKIŞKAN', color_hex='#38A169')
        button_row2.add_widget(self.default_btn)
        button_row2.add_widget(self.help_btn)
        button_row2.add_widget(self.add_gas_btn)
        content_layout.add_widget(button_row2)
        
        # ⚡ ANLIK HESAP (yeni fonksiyon ile)
        anlik_box = self.setup_anlik_hesap()
        content_layout.add_widget(anlik_box)
        
        # 📋 HESAPLAMA SONUÇLARI
        result_box = ColorfulSectionBox(color_hex='#1A202C', height=dp(350))
        result_box.add_widget(SectionTitle(text='📋 HESAPLAMA SONUÇLARI'))
        
        # Sonuçlar için ScrollView
        result_scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.result_text = TextInput(
            text='Hesaplama sonuçları burada görünecek...\n\n1. Değerleri girin\n2. HESAPLAYIN butonuna tıklayın\n3. Sonuçlar burada görünecek\n\n═══════════════════════════════\n   ORİFİS HESAPLAYICI v9.7\n═══════════════════════════════',
            readonly=True,
            background_color=get_color_from_hex('#1A202C'),
            foreground_color=get_color_from_hex('#E2E8F0'),
            font_size=sp(11),
            multiline=True,
            size_hint_y=None,
            height=dp(300)
        )
        self.result_text.bind(minimum_height=self.result_text.setter('height'))
        result_scroll.add_widget(self.result_text)
        result_box.add_widget(result_scroll)
        content_layout.add_widget(result_box)
        
        # DURUM
        self.status_label = StatusLabel(text='⏳ Değerleri girin ve HESAPLAYIN!')
        content_layout.add_widget(self.status_label)
        
        # 👣 FOOTER
        footer_box = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(40))
        footer_label = MinimalLabel(
            text='Designed by Lütfi • Mobil Uyumlu • v9.7 • ATM ATIK',
            font_size=sp(9),
            color=get_color_from_hex('#6e7681'),
            italic=True,
            halign='center'
        )
        footer_box.add_widget(footer_label)
        content_layout.add_widget(footer_box)
        
        scroll_view.add_widget(content_layout)
        main_layout.add_widget(scroll_view)
        self.add_widget(main_layout)
        
        # Event binding
        self.setup_events()
        self.update_gaz_dropdown()
        self.calculate_beta()
        self.update_pressure_display()
        
    # ⚡ ANLIK HESAP
    def setup_anlik_hesap(self):
        """Anlık hesap bölümünü oluştur"""
        anlik_box = ColorfulSectionBox(color_hex='#4C1D95', height=dp(180))
        
        # Başlık
        title_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
        title_label = Label(text='⚡ ANLIK HESAP', 
                           font_size=sp(14), 
                           bold=True,
                           color=get_color_from_hex('#c9d1d9'),
                           halign='left')
        title_row.add_widget(title_label)
        anlik_box.add_widget(title_row)
        
        # Anlık değerler için GridLayout
        grid = GridLayout(cols=2, spacing=dp(10), padding=dp(5), size_hint_y=None, height=dp(120))
        
        # Sol kolon (ΔP, P, T)
        left_col = BoxLayout(orientation='vertical', spacing=dp(5))
        
        # Anlık ΔP
        dp_container = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        dp_label = MinimalLabel(text='Anlık ΔP:', size_hint_x=0.4)
        self.anlik_delta_p_input = MinimalTextInput(
            text='729.00',
            size_hint_x=0.4,
            font_size=sp(12),
            halign='center'
        )
        dp_unit = MinimalLabel(text='mmH₂O', size_hint_x=0.2, color=get_color_from_hex('#63B3ED'))
        dp_container.add_widget(dp_label)
        dp_container.add_widget(self.anlik_delta_p_input)
        dp_container.add_widget(dp_unit)
        left_col.add_widget(dp_container)
        
        # Anlık Basınç
        p_container = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        p_label = MinimalLabel(text='Anlık P:', size_hint_x=0.4)
        self.anlik_p_input = MinimalTextInput(
            text='285471.00',
            size_hint_x=0.4,
            font_size=sp(12),
            halign='center'
        )
        self.anlik_p_unit = Spinner(
            text='Pa',
            values=('Pa', 'bar', 'atm'),
            size_hint_x=0.2,
            background_color=get_color_from_hex('#2D3748'),
            color=get_color_from_hex('#FFFFFF'),
            font_size=sp(10)
        )
        p_container.add_widget(p_label)
        p_container.add_widget(self.anlik_p_input)
        p_container.add_widget(self.anlik_p_unit)
        left_col.add_widget(p_container)
        
        # Anlık Sıcaklık
        t_container = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        t_label = MinimalLabel(text='Anlık T:', size_hint_x=0.4)
        self.anlik_t_input = MinimalTextInput(
            text='273.15',
            size_hint_x=0.4,
            font_size=sp(12),
            halign='center'
        )
        self.anlik_t_unit = Spinner(
            text='K',
            values=('K', '°C'),
            size_hint_x=0.2,
            background_color=get_color_from_hex('#2D3748'),
            color=get_color_from_hex('#FFFFFF'),
            font_size=sp(10)
        )
        t_container.add_widget(t_label)
        t_container.add_widget(self.anlik_t_input)
        t_container.add_widget(self.anlik_t_unit)
        left_col.add_widget(t_container)
        
        # Sağ kolon (boş - görselde boş kısım)
        right_col = BoxLayout(orientation='vertical')
        
        grid.add_widget(left_col)
        grid.add_widget(right_col)
        anlik_box.add_widget(grid)
        
        # ANLIK HESAP butonu
        anlik_btn_container = BoxLayout(size_hint=(1, None), height=dp(40), padding=(dp(50), 0))
        self.anlik_hesap_btn = ColorfulButton(
            text='ANLIK HESAP',
            disabled=True,
            color_hex='#D69E2E',
            size_hint=(None, None),
            size=(dp(150), dp(36)),
            pos_hint={'center_x': 0.5}
        )
        anlik_btn_container.add_widget(self.anlik_hesap_btn)
        anlik_box.add_widget(anlik_btn_container)
        
        return anlik_box        
        
    def setup_events(self):
        self.D_input.bind(text=self.on_D_change)
        self.d_input.bind(text=self.on_d_change)
        self.D_birim.bind(text=self.on_D_unit_change)
        self.d_birim.bind(text=self.on_d_unit_change)
        
        self.delta_mode_btn.bind(state=self.on_pressure_mode_change)
        self.absolute_mode_btn.bind(state=self.on_pressure_mode_change)
        
        self.delta_p_input.bind(text=self.on_delta_p_change)
        self.p1_input.bind(text=self.on_p1_change)
        self.p2_input.bind(text=self.on_p2_change)
        self.pressure_unit.bind(text=self.on_pressure_unit_change)
        
        self.gaz_spinner.bind(text=self.on_gas_change)
        self.atmosferik_check.bind(active=self.on_atmosferik_change)
        
        self.calc_btn.bind(on_press=self.hesapla)
        self.save_btn.bind(on_press=self.kaydet_hesaplama)
        self.load_btn.bind(on_press=self.yukle_hesaplama)
        self.clear_btn.bind(on_press=self.temizle)
        self.default_btn.bind(on_press=self.load_defaults)
        self.help_btn.bind(on_press=self.show_help)
        self.add_gas_btn.bind(on_press=self.add_custom_gas)
        self.anlik_hesap_btn.bind(on_press=self.show_anlik_hesap_popup)
    
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
                self.beta_label.text = "β = Değer gerekli"
                self.beta_label.color = get_color_from_hex('#FC8181')
                return

            D_val = float(D_val_str)
            d_val = float(d_val_str)

            D_val_m = convert_length(D_val, self.D_birim.text, "m")
            d_val_m = convert_length(d_val, self.d_birim.text, "m")

            self.current_values["D_m"] = D_val_m
            self.current_values["d_m"] = d_val_m

            if D_val_m > 0:
                beta = d_val_m / D_val_m
                self.beta_label.text = f"β = {beta:.4f}"
                if beta < 0.2 or beta > 0.75:
                    self.beta_label.color = get_color_from_hex('#FC8181')
                    self.beta_label.text += " ⚠️"
                else:
                    self.beta_label.color = get_color_from_hex('#68D391')
                    self.beta_label.text += " ✅"
            else:
                self.beta_label.text = "β = Geçersiz"
                self.beta_label.color = get_color_from_hex('#FC8181')
        except Exception as e:
            print(f"Beta hesaplama hatası: {e}")
            self.beta_label.text = "β = Hata"
            self.beta_label.color = get_color_from_hex('#FC8181')
    
    def update_pressure_display(self):
        try:
            unit = self.pressure_unit.text

            # Giriş basıncı
            p1_pa = self.current_values["p1_pa"]
            p1_display = convert_pressure(p1_pa, "Pa", unit)
            self.p1_input.text = f"{p1_display:.4f}"

            # Çıkış basıncı
            p2_pa = self.current_values["p2_pa"]
            p2_display = convert_pressure(p2_pa, "Pa", unit)
            self.p2_input.text = f"{p2_display:.4f}"

            # ΔP hesapla (her zaman mmH2O)
            delta_p_pa = p1_pa - p2_pa
            delta_p_val = delta_p_pa / 9.80665
            self.delta_p_input.text = f"{delta_p_val:.4f}"

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
                
                value_m = convert_length(old_value, instance.previous_text if hasattr(instance, 'previous_text') else "m", "m")
                self.current_values["D_m"] = value_m
                
                converted = convert_length(value_m, "m", value)
                self.D_input.text = f"{converted:.6f}"
                self.calculate_beta()
                
                instance.previous_text = value
        except Exception as e:
            print(f"D birim değişim hatası: {e}")
    
    def on_d_unit_change(self, instance, value):
        try:
            if self.d_input.text and self.d_input.text.strip():
                value_str = self.d_input.text
                old_value = float(value_str) if value_str else 0
                
                value_m = convert_length(old_value, instance.previous_text if hasattr(instance, 'previous_text') else "m", "m")
                self.current_values["d_m"] = value_m
                
                converted = convert_length(value_m, "m", value)
                self.d_input.text = f"{converted:.6f}"
                self.calculate_beta()
                
                instance.previous_text = value
        except Exception as e:
            print(f"d birim değişim hatası: {e}")
    
    def on_pressure_mode_change(self, instance, value):
        if value == 'down':
            if instance == self.delta_mode_btn:
                self.basinc_mode_var = "delta"
                self.delta_p_input.disabled = False
                self.delta_p_input.background_color = get_color_from_hex('#2D3748')
                self.p2_input.disabled = True
                self.p2_input.background_color = get_color_from_hex('#4A5568')
                self.on_delta_p_change(None, self.delta_p_input.text)
            else:
                self.basinc_mode_var = "absolute"
                self.delta_p_input.disabled = True
                self.delta_p_input.background_color = get_color_from_hex('#4A5568')
                self.p2_input.disabled = False
                self.p2_input.background_color = get_color_from_hex('#2D3748')
                self.update_pressure_display()
    
    def on_delta_p_change(self, instance, value):
        if self.basinc_mode_var == "delta" and value:
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
                
                if self.basinc_mode_var == "delta":
                    self.on_delta_p_change(None, self.delta_p_input.text)
                else:
                    if self.p2_input.text and self.p2_input.text.strip():
                        self.on_p2_change(None, self.p2_input.text)
                    else:
                        self.update_pressure_display()
            except:
                pass
    
    def on_p2_change(self, instance, value):
        if self.basinc_mode_var == "absolute" and value:
            try:
                unit = self.pressure_unit.text
                value_num = float(value)
                value_pa = convert_pressure(value_num, unit, "Pa")
                self.current_values["p2_pa"] = value_pa
                
                p1_pa = self.current_values["p1_pa"]
                delta_p_pa = p1_pa - value_pa
                delta_p_val = delta_p_pa / 9.80665
                self.delta_p_input.text = f"{delta_p_val:.4f}"
            except:
                pass
    
    def on_pressure_unit_change(self, instance, value):
        self.update_pressure_display()
    
    def on_gas_change(self, instance, value):
        if value:
            info = self.get_gas_info(value)
            
            # Yoğunluk ve viskozite atmosferik değerlerini güncelle
            atmosferik_yogunluk = info.get("atmosferik_yogunluk", 0.771)
            atmosferik_viskozite = info.get("atmosferik_viskozite", 1.16e-05)
            
            self.atmos_density_input.text = str(atmosferik_yogunluk)
            self.atmos_viscosity_input.text = str(atmosferik_viskozite)
            
            if value == "MANUEL GİRİŞ":
                # Manuel moda ayarla
                self.yogunluk_mode_var = "manuel"
                self.viskozite_mode_var = "manuel"
                self.density_input.text = str(VARSAYILAN_DEGERLER["yogunluk_manuel"])
                self.viscosity_input.text = str(VARSAYILAN_DEGERLER["viskozite_manuel"])
            else:
                # Diğer gazlar için varsayılan değerleri yükle
                viskozite_degeri = info.get('viskozite_293', 1e-05)
                self.viscosity_input.text = str(viskozite_degeri)
                
                if 'yogunluk_293' in info:
                    self.density_input.text = str(info['yogunluk_293'])
                else:
                    self.density_input.text = str(atmosferik_yogunluk)
                
                # Eğer atmosferik mod aktifse, değerleri güncelle
                if self.atmosferik_mode_var:
                    self.atmos_density_input.text = str(atmosferik_yogunluk)
                    self.atmos_viscosity_input.text = str(atmosferik_viskozite)
    
    def on_atmosferik_change(self, instance, value):
        self.atmosferik_mode_var = value
        
        if value:
            # Atmosferik mod aktif: sıcaklık, yoğunluk ve viskoziteyi atmosferik değerlere ayarla
            self.temp_input.text = "273.15"
            self.temp_unit.text = "K"
            
            # Radio gruplarını atmosferik moda ayarla
            self.yogunluk_mode_var = "atmosferik"
            self.viskozite_mode_var = "atmosferik"
            
            # Yoğunluk ve viskozite alanlarını güncelle
            self.density_input.disabled = True
            self.density_input.background_color = get_color_from_hex('#4A5568')
            self.viscosity_input.disabled = True
            self.viscosity_input.background_color = get_color_from_hex('#4A5568')
            
            self.atmos_density_input.disabled = False
            self.atmos_density_input.background_color = get_color_from_hex('#2A4365')
            self.atmos_viscosity_input.disabled = False
            self.atmos_viscosity_input.background_color = get_color_from_hex('#2A4365')
            
            # Gaz bilgilerini güncelle
            gaz_secim = self.gaz_spinner.text
            if gaz_secim:
                info = self.get_gas_info(gaz_secim)
                self.atmos_density_input.text = str(info.get("atmosferik_yogunluk", 1.293))
                self.atmos_viscosity_input.text = str(info.get("atmosferik_viskozite", 1.81e-05))
            
            self.show_popup("✅ Atmosferik mod aktif (0°C, 1 atm)", "info")
        else:
            # Atmosferik mod devre dışı: manuel moda dön
            self.yogunluk_mode_var = "manuel"
            self.viskozite_mode_var = "manuel"
            
            self.density_input.disabled = False
            self.density_input.background_color = get_color_from_hex('#2A4365')
            self.viscosity_input.disabled = False
            self.viscosity_input.background_color = get_color_from_hex('#2A4365')
            
            self.atmos_density_input.disabled = True
            self.atmos_density_input.background_color = get_color_from_hex('#4A5568')
            self.atmos_viscosity_input.disabled = True
            self.atmos_viscosity_input.background_color = get_color_from_hex('#4A5568')
            
            self.show_popup("🔄 Atmosferik mod devre dışı", "warning")
    
    def yogunluk_hesapla(self, gaz_secim, sicaklik_K, basinc_pa):
        info = self.get_gas_info(gaz_secim)
        
        # Radio group değerini kontrol et
        yogunluk_mode = self.yogunluk_radio_group.selected_value.lower() if hasattr(self.yogunluk_radio_group, 'selected_value') else self.yogunluk_mode_var
        
        if yogunluk_mode == "manuel":
            try:
                rho = float(self.density_input.text) if self.density_input.text else 1.2
                return rho
            except:
                return 1.2
        
        elif yogunluk_mode == "atmosferik":
            return info.get("atmosferik_yogunluk", 1.293)
        
        else:  # otomatik
            if info.get("tip") == "sıvı":
                return info.get('yogunluk_293', 1000)
            
            R = 8314.462618
            M = info.get("mol_agirligi", 28.97)
            if M > 0:
                rho = (basinc_pa * M) / (R * sicaklik_K)
                return rho
            else:
                return 1.2
    
    def viskozite_hesapla(self, gaz_secim, sicaklik_K):
        info = self.get_gas_info(gaz_secim)
        
        # Radio group değerini kontrol et
        viskozite_mode = self.viskozite_radio_group.selected_value.lower() if hasattr(self.viskozite_radio_group, 'selected_value') else self.viskozite_mode_var
        
        if viskozite_mode == "manuel":
            try:
                return float(self.viscosity_input.text) if self.viscosity_input.text else 1.8e-05
            except:
                return 1.8e-05
        
        elif viskozite_mode == "atmosferik":
            return info.get("atmosferik_viskozite", 1.8e-05)
        
        else:  # otomatik
            base_mu = info.get("viskozite_293", 1.8e-05)
            
            if info.get("tip") == "gaz":
                return base_mu * (sicaklik_K / 293.15)**0.7
            else:
                return base_mu
    
    def hesapla(self, instance):
        try:
            self.status_label.set_status("⏳ Hesaplama başlatıldı...", "info")
            self.calc_btn.disabled = True
            self.calc_btn.text = "⏳ HESAPLANIYOR..."
            
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
            self.beta_label.text = f"β = {beta:.4f}"

            if beta > 0.75 or beta < 0.2:
                self.show_popup(f"⚠️ β={beta:.3f} ideal aralıkta değil (0.2-0.75)", "warning")

            # Basınç değerleri
            p1_gauge = self.current_values["p1_pa"]
            p2_gauge = self.current_values["p2_pa"]
            delta_p_pa = p1_gauge - p2_gauge
            delta_p_val = delta_p_pa / 9.80665

            # Absolute basınçlar
            ATMOSFERIK_BASINC = 101325
            p1_abs = p1_gauge + ATMOSFERIK_BASINC
            p2_abs = p2_gauge + ATMOSFERIK_BASINC

            # Yoğunluk ve viskozite (radio group değerlerine göre)
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
            if info.get("tip") == "gaz":
                rho_atmosferik = info.get("atmosferik_yogunluk", 1.293)
                q_normal_m3h = q_m3h * (rho / rho_atmosferik) if rho_atmosferik > 0 else 0
            else:
                q_normal_m3h = q_m3h
                rho_atmosferik = rho

            A0 = excel_A0_hesapla(D_val_m)
            A1 = excel_A1_hesapla(d_val_m)

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            katsayi = q_normal_m3h / math.sqrt(delta_p_val) if delta_p_val > 0 else 0

            # Dizayn basıncı ve sıcaklığını belirle (atmosferik mod kontrolü)
            if self.atmosferik_mode_var:
                dizayn_p_abs = 101325  # 1 atm
                dizayn_T = 273.15      # 0°C
            else:
                dizayn_p_abs = p1_abs
                dizayn_T = sicaklik_K

            # Yoğunluk ve viskozite modlarını belirle
            yogunluk_mode = self.yogunluk_radio_group.selected_value if hasattr(self.yogunluk_radio_group, 'selected_value') else self.yogunluk_mode_var
            viskozite_mode = self.viskozite_radio_group.selected_value if hasattr(self.viskozite_radio_group, 'selected_value') else self.viskozite_mode_var

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
                "yogunluk_mode": yogunluk_mode,
                "viskozite_mode": viskozite_mode,
                "atmosferik_mode": self.atmosferik_mode_var,
                "dizayn_p_abs": dizayn_p_abs,
                "dizayn_T": dizayn_T,
                "L1": L1_val,
                "L2": L2_val,
                "max_iter": max_iter_val,
                "epsilon": epsilon_val
            }

            self.hesaplama_gecmisi.append(hesaplama_data)
            self.anlik_hesap_data = hesaplama_data

            # Butonları aktif et
            self.save_btn.disabled = False
            self.anlik_hesap_btn.disabled = False

            # Anlık hesap alanlarını doldur
            self.anlik_delta_p_input.text = f"{delta_p_val:.2f}"
            self.anlik_p_input.text = f"{convert_pressure(p1_gauge, 'Pa', self.pressure_unit.text):.2f}"
            self.anlik_t_input.text = f"{sicaklik_input:.2f}"
            self.anlik_p_unit.text = self.pressure_unit.text
            self.anlik_t_unit.text = self.temp_unit.text

            # Sonuçları göster
            result_text = f"""╔═══════════════════════════════╗
║   ORİFİS HESAP SONUÇLARI    ║
╚═══════════════════════════════╝

📅 Tarih: {now}
🌡️ Akışkan: {gaz_secim}
🔥 Sıcaklık: {sicaklik_input:.1f} {self.temp_unit.text} ({sicaklik_K:.1f} K)
📏 β Oranı: {beta:.4f} {'✅' if 0.2 <= beta <= 0.75 else '⚠️'}
⚡ İterasyon: {iter_count} {'✅' if converged else '⚠️'}
🌍 Atmosferik Mod: {'✅ AÇIK' if self.atmosferik_mode_var else '❌ KAPALI'}
📊 Yoğunluk Modu: {yogunluk_mode}
📊 Viskozite Modu: {viskozite_mode}

📊 BASINÇ DEĞERLERİ:
  Giriş: {p1_gauge/1000:.1f} kPa (gauge)
  Giriş: {p1_abs/1000:.1f} kPa (mutlak)
  Çıkış: {p2_gauge/1000:.1f} kPa (gauge)
  ΔP: {delta_p_val:.1f} mmH₂O ({delta_p_pa:.0f} Pa)

📐 GEOMETRİK ÖLÇÜLER:
  Boru Çapı (D): {D_val_m:.4f} m
  Orifis Çapı (d): {d_val_m:.4f} m
  A0 (Boru Kesiti): {A0:.6f} m²
  A1 (Orifis Kesiti): {A1:.6f} m²

🚀 DEBİ SONUÇLARI:"""

            if info.get("tip") == "gaz":
                result_text += f"""
╔═══════════════════════════════════════════════════════════════╗
║  🟢 GERÇEK DEBİ: {q_m3h:,.1f} m³/h                              ║
║  🟢 KÜTLESEL DEBİ: {mass_flow:,.1f} kg/h                         ║
║  🟢 NORMAL DEBİ: {q_normal_m3h:,.1f} Nm³/h (0°C, 1 atm)          ║
║                                                               ║
║  🟢 GERÇEK YOĞUNLUK: {rho:.4f} kg/m³                            ║
║  🟢 ATMOSFERİK YOĞUNLUK: {rho_atmosferik:.4f} kg/m³ (0°C, 1 atm) ║
╚═══════════════════════════════════════════════════════════════╝"""
            else:
                result_text += f"""
╔═══════════════════════════════════════════════════════════════╗
║  🟢 GERÇEK DEBİ: {q_m3h:,.1f} m³/h                              ║
║  🟢 KÜTLESEL DEBİ: {mass_flow:,.1f} kg/h                         ║
║  🟢 YOĞUNLUK: {rho:.4f} kg/m³                                   ║
╚═══════════════════════════════════════════════════════════════╝"""

            result_text += f"""
📈 AKIŞ PARAMETRELERİ:
  Hız: {v:.4f} m/s
  Reynolds: {Re:,.0f}
  Viskozite: {mu:.2e} Pa·s

🎯 C KATSAYILARI:
  Başlangıç C0: {C0_baslangic_val:.6f}
  Hesaplanan C_calc: {C_calc:.6f}
  Son C0 Değeri: {C0_son:.6f}
  Fark: {C0_son - C_calc:.6f}

🔢 KATSAYI (Anlık Hesap İçin):
  k = Nm³/h / √ΔP = {katsayi:.2f}

📊 DİZAYN ŞARTLARI:
  {'🌍 ATMOSFERİK' if self.atmosferik_mode_var else '📏 ÖLÇÜLEN'}
  Basınç: {dizayn_p_abs/1000:.1f} kPa (mutlak)
  Sıcaklık: {dizayn_T:.1f} K ({dizayn_T-273.15:.1f}°C)

{'✅ YAKINSAMA BAŞARILI!' if converged else '⚠️ MAX ITERASYONA ULAŞILDI!'}

═══════════════════════════════
     HESAPLAMA TAMAM v9.7 ✅
═══════════════════════════════
"""

            self.result_text.text = result_text
            # TextInput'in boyutunu güncelle
            self.result_text.height = max(dp(350), len(result_text.split('\n')) * dp(20))
            
            self.status_label.set_status(f"✅ Hesaplama tamam! Debi: {q_normal_m3h:,.1f} Nm³/h", "success")

            self.show_popup("✅ Hesaplama başarıyla tamamlandı!", "success")

        except ValueError as ve:
            self.result_text.text = f"❌ HATA: {str(ve)}\n\nLütfen değerleri kontrol edin."
            self.status_label.set_status("❌ Hata: Geçersiz değer!", "error")
            self.show_popup(f"❌ Hata: {str(ve)[:50]}", "error")

        except Exception as ex:
            self.result_text.text = f"❌ SİSTEM HATASI: {str(ex)}\n\nLütfen tekrar deneyin."
            self.status_label.set_status("❌ Hata: Hesaplama başarısız!", "error")
            self.show_popup(f"❌ Sistem hatası: {str(ex)[:50]}", "error")

        finally:
            self.calc_btn.disabled = False
            self.calc_btn.text = "🚀 HESAPLA"
    
    def show_anlik_hesap_popup(self, instance):
        if not self.anlik_hesap_data:
            self.show_popup("❌ Önce dizayn hesabı yapın!", "error")
            return
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        # Başlık
        title_label = Label(text='⚡ ANLIK HESAP',
                           font_size=sp(16),
                           color=get_color_from_hex('#63B3ED'),
                           size_hint_y=None,
                           height=dp(40))
        content.add_widget(title_label)
        
        # Giriş alanları
        input_box = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # Anlık ΔP
        dp_row = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        dp_row.add_widget(MinimalLabel(text='Anlık ΔP:', size_hint_x=0.3))
        anlik_dp_input = MinimalTextInput(text=self.anlik_delta_p_input.text, size_hint_x=0.5)
        dp_row.add_widget(anlik_dp_input)
        dp_row.add_widget(MinimalLabel(text='mmH₂O', size_hint_x=0.2, color=get_color_from_hex('#63B3ED')))
        input_box.add_widget(dp_row)
        
        # Anlık Basınç
        p_row = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        p_row.add_widget(MinimalLabel(text='Anlık P:', size_hint_x=0.3))
        anlik_p_input = MinimalTextInput(text=self.anlik_p_input.text, size_hint_x=0.4)
        anlik_p_unit = Spinner(text=self.anlik_p_unit.text, values=('Pa', 'bar', 'atm'),
                              size_hint_x=0.3, background_color=get_color_from_hex('#2D3748'),
                              color=get_color_from_hex('#FFFFFF'))
        p_row.add_widget(anlik_p_input)
        p_row.add_widget(anlik_p_unit)
        input_box.add_widget(p_row)
        
        # Anlık Sıcaklık
        t_row = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(36))
        t_row.add_widget(MinimalLabel(text='Anlık T:', size_hint_x=0.3))
        anlik_t_input = MinimalTextInput(text=self.anlik_t_input.text, size_hint_x=0.4)
        anlik_t_unit = Spinner(text=self.anlik_t_unit.text, values=('K', '°C'),
                              size_hint_x=0.3, background_color=get_color_from_hex('#2D3748'),
                              color=get_color_from_hex('#FFFFFF'))
        t_row.add_widget(anlik_t_input)
        t_row.add_widget(anlik_t_unit)
        input_box.add_widget(t_row)
        
        content.add_widget(input_box)
        
        # Sonuç alanı
        sonuc_label = Label(text='',
                           font_size=sp(11),
                           color=get_color_from_hex('#E2E8F0'),
                           size_hint_y=None,
                           valign='top',
                           halign='left')
        sonuc_label.bind(texture_size=sonuc_label.setter('size'))
        
        sonuc_scroll = ScrollView(size_hint=(1, 0.6))
        sonuc_scroll.add_widget(sonuc_label)
        content.add_widget(sonuc_scroll)
        
        def hesapla_anlik(instance):
            try:
                anlik_delta_p_val = float(anlik_dp_input.text) if anlik_dp_input.text else 0
                anlik_p_input_val = float(anlik_p_input.text) if anlik_p_input.text else 0
                anlik_T_input_val = float(anlik_t_input.text) if anlik_t_input.text else 0

                if anlik_delta_p_val <= 0 or anlik_p_input_val <= 0 or anlik_T_input_val <= 0:
                    raise ValueError("Anlık değerler pozitif olmalı")

                anlik_p_pa = convert_pressure(anlik_p_input_val, anlik_p_unit.text, "Pa")
                anlik_T_K = convert_temperature(anlik_T_input_val, anlik_t_unit.text, "K")

                dizayn_q_normal = self.anlik_hesap_data["q_normal"]
                dizayn_delta_p = self.anlik_hesap_data["delta_p"]
                dizayn_p_abs = self.anlik_hesap_data.get("dizayn_p_abs", self.anlik_hesap_data["p1_abs"])
                dizayn_T = self.anlik_hesap_data.get("dizayn_T", self.anlik_hesap_data["sicaklik_K"])
                katsayi = self.anlik_hesap_data["katsayi"]

                ATMOSFERIK_BASINC = 101325
                anlik_p_abs = anlik_p_pa + ATMOSFERIK_BASINC

                ham_debi_anlik = katsayi * math.sqrt(anlik_delta_p_val) if katsayi > 0 else 0

                p_oran = anlik_p_abs / dizayn_p_abs
                T_oran = dizayn_T / anlik_T_K
                duzeltme_faktor = math.sqrt(p_oran * T_oran)
                anlik_nm3h = ham_debi_anlik * duzeltme_faktor

                sonuc_text = f"""📊 ANLIK HESAP SONUÇLARI:

• Anlık ΔP: {anlik_delta_p_val:.1f} mmH₂O
• Anlık Basınç: {anlik_p_input_val:.1f} {anlik_p_unit.text} (gauge)
• Anlık Basınç: {anlik_p_abs/1000:.1f} kPa (mutlak)
• Anlık Sıcaklık: {anlik_T_input_val:.1f} {anlik_t_unit.text} ({anlik_T_K:.1f} K)

• Ham Debi: {ham_debi_anlik:.1f} m³/h (k × √ΔP)
• Düzeltme Faktörü: √(({anlik_p_abs/1000:.1f}/{dizayn_p_abs/1000:.1f}) × ({dizayn_T:.1f}/{anlik_T_K:.1f})) = {duzeltme_faktor:.4f}
• Anlık Normal Debi: {anlik_nm3h:.1f} Nm³/h

• Katsayı (k): {katsayi:.2f}
• Dizayn Normal Debi: {dizayn_q_normal:.1f} Nm³/h
• Dizayn ΔP: {dizayn_delta_p:.1f} mmH₂O
• Dizayn Mutlak Basınç: {dizayn_p_abs/1000:.1f} kPa
• Dizayn Sıcaklık: {dizayn_T:.1f} K

═══════════════════════════════
     HESAPLAMA TAMAM ✅
═══════════════════════════════"""

                sonuc_label.text = sonuc_text
                sonuc_label.height = max(dp(200), len(sonuc_text.split('\n')) * dp(20))
                
            except ValueError as ve:
                sonuc_label.text = f"❌ HATA: {str(ve)}"
            except Exception as ex:
                sonuc_label.text = f"❌ SİSTEM HATASI: {str(ex)}"
        
        # Butonlar
        button_box = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
        iptal_btn = ColorfulButton(text='İPTAL', color_hex='#E53E3E')
        hesapla_btn = ColorfulButton(text='HESAPLA', color_hex='#38A169')
        
        iptal_btn.bind(on_press=lambda x: popup.dismiss())
        hesapla_btn.bind(on_press=hesapla_anlik)
        
        button_box.add_widget(iptal_btn)
        button_box.add_widget(hesapla_btn)
        content.add_widget(button_box)
        
        popup = Popup(title='',
                     content=content,
                     size_hint=(0.9, 0.8),
                     background_color=get_color_from_hex('#1A202C'))
        popup.open()
    
    def kaydet_hesaplama(self, instance):
        if not self.hesaplama_gecmisi:
            self.show_popup("❌ Kaydedilecek hesaplama yok!", "error")
            return
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        filename_input = MinimalTextInput(text=f"hesaplama_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        def save_action(instance):
            dosya_adi = filename_input.text
            if not dosya_adi:
                self.show_popup("❌ Dosya adı boş olamaz!", "error")
                return
            
            son_hesaplama = self.hesaplama_gecmisi[-1]
            kayit_yolu = self.orifis_kayit.kaydet(son_hesaplama, dosya_adi)
            
            if kayit_yolu:
                self.show_popup(f"✅ Kaydedildi: {kayit_yolu.name}", "success")
                popup.dismiss()
            else:
                self.show_popup("❌ Kayıt başarısız!", "error")
        
        def cancel_action(instance):
            popup.dismiss()
        
        content.add_widget(MinimalLabel(text="Kaydedilecek dosya adı:"))
        content.add_widget(filename_input)
        
        button_box = BoxLayout(orientation='horizontal', spacing=dp(10))
        button_box.add_widget(ColorfulButton(text="İPTAL", on_press=cancel_action, color_hex='#E53E3E'))
        button_box.add_widget(ColorfulButton(text="KAYDET", on_press=save_action, color_hex='#38A169'))
        
        content.add_widget(button_box)
        
        popup = Popup(title='💾 Hesaplamayı Kaydet',
                     content=content,
                     size_hint=(0.8, 0.4),
                     background_color=get_color_from_hex('#1A202C'))
        popup.open()
    
    def yukle_hesaplama(self, instance):
        kayitlar = self.orifis_kayit.listele_kayitlar()
        
        if not kayitlar:
            self.show_popup("❌ Kayıtlı hesaplama bulunamadı!", "error")
            return
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        scroll_view = ScrollView(size_hint=(1, 0.8))
        list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        for kayit in kayitlar[:10]:
            btn = ColorfulButton(text=kayit, 
                               size_hint_y=None, 
                               height=dp(36),
                               color_hex='#4A5568',
                               on_press=lambda x, k=kayit: self.load_file(k))
            list_layout.add_widget(btn)
        
        scroll_view.add_widget(list_layout)
        content.add_widget(scroll_view)
        
        close_btn = ColorfulButton(text="KAPAT", on_press=lambda x: popup.dismiss(), color_hex='#E53E3E')
        content.add_widget(close_btn)
        
        popup = Popup(title='📂 Kayıtlı Hesaplamalar',
                     content=content,
                     size_hint=(0.9, 0.8),
                     background_color=get_color_from_hex('#1A202C'))
        popup.open()
    
    def load_file(self, dosya_adi):
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
                self.D_input.text = f"{D_display:.6f}"
                self.d_input.text = f"{d_display:.6f}"
                self.current_values["D_m"] = D_val_m
                self.current_values["d_m"] = d_val_m
                
                self.L1_input.text = str(data.get("L1", VARSAYILAN_DEGERLER["L1"]))
                self.L2_input.text = str(data.get("L2", VARSAYILAN_DEGERLER["L2"]))
                self.C0_input.text = str(data.get("C0_baslangic", VARSAYILAN_DEGERLER["C0_baslangic"]))
                
                # Basınç değerleri
                p1_gauge = float(data.get("p1", VARSAYILAN_DEGERLER["p1"]))
                p2_gauge = float(data.get("p2", VARSAYILAN_DEGERLER["p2"]))
                self.current_values["p1_pa"] = p1_gauge
                self.current_values["p2_pa"] = p2_gauge
                
                basinc_birim_loaded = data.get("basinc_birim", "Pa")
                self.pressure_unit.text = basinc_birim_loaded
                self.update_pressure_display()
                
                # Sıcaklık
                sicaklik_input = float(data.get("sicaklik", VARSAYILAN_DEGERLER["sicaklik"]))
                sicaklik_birim_loaded = data.get("sicaklik_birim", "K")
                self.temp_unit.text = sicaklik_birim_loaded
                self.temp_input.text = f"{sicaklik_input:.2f}"
                
                # Gaz
                gaz_loaded = data.get("gaz", VARSAYILAN_DEGERLER["gaz_tipi"])
                self.gaz_spinner.text = gaz_loaded
                
                # Yoğunluk ve viskozite
                self.density_input.text = str(data.get("yogunluk_manuel", VARSAYILAN_DEGERLER["yogunluk_manuel"]))
                self.viscosity_input.text = str(data.get("viskozite_manuel", VARSAYILAN_DEGERLER["viskozite_manuel"]))
                self.atmos_density_input.text = str(data.get("yogunluk_atmosferik", VARSAYILAN_DEGERLER["yogunluk_atmosferik"]))
                self.atmos_viscosity_input.text = str(data.get("viskozite_atmosferik", VARSAYILAN_DEGERLER["viskozite_atmosferik"]))
                
                # Modlar
                basinc_mode = data.get("basinc_mode", "delta")
                if basinc_mode == "delta":
                    self.delta_mode_btn.state = 'down'
                    self.absolute_mode_btn.state = 'normal'
                    self.basinc_mode_var = "delta"
                    self.delta_p_input.disabled = False
                    self.delta_p_input.background_color = get_color_from_hex('#2D3748')
                    self.p2_input.disabled = True
                    self.p2_input.background_color = get_color_from_hex('#4A5568')
                else:
                    self.absolute_mode_btn.state = 'down'
                    self.delta_mode_btn.state = 'normal'
                    self.basinc_mode_var = "absolute"
                    self.delta_p_input.disabled = True
                    self.delta_p_input.background_color = get_color_from_hex('#4A5568')
                    self.p2_input.disabled = False
                    self.p2_input.background_color = get_color_from_hex('#2D3748')
                
                # Yoğunluk ve viskozite modları
                yogunluk_mode = data.get("yogunluk_mode", "manuel")
                self.yogunluk_mode_var = yogunluk_mode
                
                viskozite_mode = data.get("viskozite_mode", "manuel")
                self.viskozite_mode_var = viskozite_mode
                
                # Atmosferik mod
                atmosferik_mode = data.get("atmosferik_mode", False)
                self.atmosferik_check.active = atmosferik_mode
                self.atmosferik_mode_var = atmosferik_mode
                
                # Anlık hesap değerleri
                delta_p_val = float(data.get("delta_p", VARSAYILAN_DEGERLER["delta_p"]))
                self.anlik_delta_p_input.text = str(delta_p_val)
                self.anlik_p_input.text = f"{convert_pressure(p1_gauge, 'Pa', basinc_birim_loaded):.2f}"
                self.anlik_t_input.text = str(sicaklik_input)
                self.anlik_p_unit.text = basinc_birim_loaded
                self.anlik_t_unit.text = sicaklik_birim_loaded
                
                popup = self.get_popup_parent()
                if popup:
                    popup.dismiss()
                
                self.show_popup(f"✅ Yüklendi: {dosya_adi}", "success")
                
                self.calculate_beta()
                
            except Exception as e:
                print(f"Yükleme işlem hatası: {e}")
                self.show_popup(f"❌ Yükleme hatası: {str(e)}", "error")
    
    def load_defaults(self, instance):
        try:
            # Geometrik değerler
            D_val_m = VARSAYILAN_DEGERLER["D"]
            d_val_m = VARSAYILAN_DEGERLER["d"]
            D_display = convert_length(D_val_m, "m", self.D_birim.text)
            d_display = convert_length(d_val_m, "m", self.d_birim.text)
            self.D_input.text = f"{D_display:.6f}"
            self.d_input.text = f"{d_display:.6f}"
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
            self.atmos_density_input.text = str(VARSAYILAN_DEGERLER["yogunluk_atmosferik"])
            self.atmos_viscosity_input.text = str(VARSAYILAN_DEGERLER["viskozite_atmosferik"])

            # Atmosferik modu kapat
            self.atmosferik_check.active = False
            self.atmosferik_mode_var = False
            self.density_input.disabled = False
            self.density_input.background_color = get_color_from_hex('#2A4365')
            self.viscosity_input.disabled = False
            self.viscosity_input.background_color = get_color_from_hex('#2A4365')
            self.atmos_density_input.disabled = True
            self.atmos_density_input.background_color = get_color_from_hex('#4A5568')
            self.atmos_viscosity_input.disabled = True
            self.atmos_viscosity_input.background_color = get_color_from_hex('#4A5568')

            self.calculate_beta()
            self.delta_mode_btn.state = 'down'
            self.absolute_mode_btn.state = 'normal'

            self.result_text.text = "✅ Excel varsayılan değerleri yüklendi!\n\n═══════════════════════════════\n   ORİFİS HESAPLAYICI v9.7\n═══════════════════════════════"

            self.show_popup("✅ Excel değerleri yüklendi (manuel mod)", "info")
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
        self.anlik_delta_p_input.text = ""
        self.anlik_p_input.text = ""
        self.anlik_t_input.text = ""

        self.current_values["D_m"] = 0
        self.current_values["d_m"] = 0
        self.current_values["p1_pa"] = 0
        self.current_values["p2_pa"] = 0
        
        self.atmosferik_check.active = False
        self.atmosferik_mode_var = False
        
        self.result_text.text = """🧹 Tüm alanlar temizlendi!

1. Değerleri girin
2. 'HESAPLAYIN' butonuna tıklayın
3. Sonuçlar burada görünecek

═══════════════════════════════
   ORİFİS HESAPLAYICI v9.7
═══════════════════════════════"""
        
        self.status_label.set_status("⏳ Değerleri girin ve HESAPLAYIN!", "info")
        self.save_btn.disabled = True
        self.anlik_hesap_btn.disabled = True
        
        self.show_popup("🧹 Tüm alanlar temizlendi!", "warning")
    
    def show_help(self, instance):
        help_text = """⚡ ORİFİS DEBİ HESAPLAYICI v9.7

📌 KULLANIM:
1. Boru ve orifis ölçülerini girin
2. Basınç değerlerini seçin (ΔP veya Giriş/Çıkış)
3. Akışkan tipini seçin
4. Yoğunluk ve viskozite modunu seçin
5. 'HESAPLAYIN' butonuna tıklayın

🌍 ATMOSFERİK MOD:
• Tek checkbox ile aktifleştirilir
• Aktif olduğunda: sıcaklık=0°C, basınç=1 atm
• Yoğunluk ve viskozite otomatik olarak atmosferik değerlere ayarlanır
• Anlık hesapta dizayn şartları atmosferik olarak alınır

🔄 BİRİM DÖNÜŞÜMLERİ:
• Basınç birimi değiştiğinde tüm değerler otomatik güncellenir
• Uzunluk birimi değiştiğinde değerler otomatik çevrilir
• Birimler: Pa, kPa, bar, atm, mmH2O, kg/cm²

📊 SONUÇLAR:
• Gerçek debi (m³/h) - ölçülen şartlarda
• Normal debi (Nm³/h) - 0°C, 1 atm şartlarında
• Kütlesel debi (kg/h)
• Yoğunluk değerleri

🔄 YOĞUNLUK MODLARI:
• OTOMATİK: İdeal gaz denklemi ile hesaplanır
• MANUEL: Elle girilen değer kullanılır
• ATMOSFERİK: 0°C, 1 atm'deki yoğunluk kullanılır

🔄 VİSKOZİTE MODLARI:
• OTOMATİK: Sıcaklıkla değişen viskozite
• MANUEL: Elle girilen değer
• ATMOSFERİK: Standart viskozite değeri

🔢 ANLIK HESAP:
• Dizayn hesabı yapıldıktan sonra aktif olur
• Formül: Nm³/h_anlık = k × √(ΔP_anlık) × √((P_anlık/P_dizayn) × (T_dizayn/T_anlık))
• k = Nm³/h_dizayn / √(ΔP_dizayn)
• Atmosferik mod açıksa: P_dizayn=1 atm, T_dizayn=0°C

⚠️ NOTLAR:
• β oranı (d/D) 0.2-0.75 arasında olmalı
• Excel ile tam uyumlu
• Mobil uyumlu

👨‍💻 GELİŞTİRİCİ: Lütfi
"""
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        help_label = Label(text=help_text,
                          font_size=sp(11),
                          color=get_color_from_hex('#E2E8F0'),
                          size_hint_y=None)
        help_label.bind(texture_size=help_label.setter('size'))
        
        scroll_view = ScrollView()
        scroll_view.add_widget(help_label)
        
        content.add_widget(scroll_view)
        
        close_btn = ColorfulButton(text="TAMAM", on_press=lambda x: popup.dismiss(), color_hex='#3182CE')
        content.add_widget(close_btn)
        
        popup = Popup(title='Yardım',
                     content=content,
                     size_hint=(0.9, 0.8),
                     background_color=get_color_from_hex('#1A202C'))
        popup.open()
    
    def add_custom_gas(self, instance):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        name_input = MinimalTextInput(hint_text="Akışkan Adı")
        formula_input = MinimalTextInput(hint_text="Formül")
        mol_input = MinimalTextInput(hint_text="Mol. Ağırlık (g/mol)")
        visc_input = MinimalTextInput(hint_text="Viskozite 20°C (Pa·s)", text="1.16e-05")
        dens_input = MinimalTextInput(hint_text="Yoğunluk 20°C (kg/m³)", text="1.2")
        atmo_dens_input = MinimalTextInput(hint_text="Atmosferik Yoğunluk", text="0.761")
        desc_input = MinimalTextInput(hint_text="Açıklama")
        
        gas_type = Spinner(text='gaz', values=('gaz', 'sıvı'), 
                          background_color=get_color_from_hex('#2D3748'),
                          color=get_color_from_hex('#FFFFFF'))
        
        def save_gas(instance):
            name = name_input.text.strip()
            formula = formula_input.text.strip()
            mol_str = mol_input.text.strip()
            visc_str = visc_input.text.strip()
            dens_str = dens_input.text.strip()
            atmo_dens_str = atmo_dens_input.text.strip()
            gas_tip = gas_type.text
            desc = desc_input.text.strip()
            
            if not name:
                self.show_popup("❌ Akışkan adı boş olamaz!", "error")
                return
            
            try:
                mol_weight = float(mol_str) if mol_str else 0
                viscosity = float(visc_str) if visc_str else 1e-05
                density = float(dens_str) if dens_str else 1.2
                atmosferik_density = float(atmo_dens_str) if atmo_dens_str else 1.2
            except ValueError:
                self.show_popup("❌ Sayısal değerler geçerli olmalı!", "error")
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
                self.show_popup(f"✅ '{name}' eklendi!", "success")
            else:
                self.show_popup("❌ Kaydetme başarısız!", "error")
        
        def cancel_action(instance):
            popup.dismiss()
        
        content.add_widget(name_input)
        content.add_widget(formula_input)
        content.add_widget(mol_input)
        content.add_widget(visc_input)
        content.add_widget(dens_input)
        content.add_widget(atmo_dens_input)
        content.add_widget(gas_type)
        content.add_widget(desc_input)
        
        button_box = BoxLayout(orientation='horizontal', spacing=dp(10))
        button_box.add_widget(ColorfulButton(text="İPTAL", on_press=cancel_action, color_hex='#E53E3E'))
        button_box.add_widget(ColorfulButton(text="KAYDET", on_press=save_gas, color_hex='#38A169'))
        
        content.add_widget(button_box)
        
        scroll_view = ScrollView()
        scroll_view.add_widget(content)
        
        popup = Popup(title='➕ Yeni Akışkan Ekle',
                     content=scroll_view,
                     size_hint=(0.9, 0.9),
                     background_color=get_color_from_hex('#1A202C'))
        popup.open()
    
    def show_popup(self, message, type="info"):
        colors = {
            "success": get_color_from_hex('#38A169'),
            "error": get_color_from_hex('#E53E3E'),
            "warning": get_color_from_hex('#D69E2E'),
            "info": get_color_from_hex('#3182CE')
        }
        
        popup = Popup(title='',
                     content=Label(text=message, color=get_color_from_hex('#ffffff')),
                     size_hint=(0.8, 0.2),
                     background_color=colors[type])
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 3)
    
    def get_popup_parent(self):
        # Mevcut açık popup'ı bul
        for child in Window.children:
            if isinstance(child, Popup):
                return child
        return None

class OrifisApp(App):
    def build(self):
        Window.clearcolor = get_color_from_hex('#1A202C')
        
        sm = ScreenManager()
        main_screen = MainScreen()
        sm.add_widget(main_screen)
        
        return sm

if __name__ == '__main__':
    OrifisApp().run()
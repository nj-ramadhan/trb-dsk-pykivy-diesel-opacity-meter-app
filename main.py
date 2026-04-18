import cmd
import datetime
import os, sys, time
import ssl
import random
import math
import serial
from serial.tools import list_ports
ssl._create_default_https_context = ssl._create_unverified_context
import cv2
from kivy.graphics.texture import Texture
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    running_mode = 'Frozen/executable'
else:
    try:
        app_full_path = os.path.realpath(__file__)
        application_path = os.path.dirname(app_full_path)
        running_mode = "Non-interactive"
    except NameError:
        application_path = os.getcwd()
        running_mode = 'Interactive'
logger_name = f'app.log'
logger_dir = os.path.join(application_path, "logs")

from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'system')

from kivy.logger import Logger
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager
from kivymd.font_definitions import theme_font_styles
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivy.metrics import dp
from kivymd.toast import toast
from kivymd.app import MDApp
import numpy as np
import configparser, hashlib, mysql.connector
from pymodbus.client import ModbusTcpClient
from kivy.graphics.texture import Texture
import serial.tools.list_ports
import threading
from kivy.clock import mainthread
from kivy.uix.spinner import Spinner
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivy.properties import NumericProperty, ListProperty, StringProperty, BooleanProperty
from kivymd.uix.button import MDFillRoundFlatButton
import bcrypt 

dt_id_user = 0
dt_user = ""
dt_foto_user = ""

colors = {

    "Red"   : {"A200": "#FF2A2A","A500": "#FF8080","A700": "#FFD5D5",},
    "Gray"  : {"200": "#CCCCCC","500": "#ECECEC","700": "#F9F9F9",},
    "Blue"  : {"200": "#4471C4","500": "#5885D8","700": "#6C99EC",},
    "Green" : {"200": "#2CA02C","500": "#2DB97F", "700": "#D5FFD5",},
    "Yellow": {"200": "#ffD42A","500": "#ffE680","700": "#fff6D5",},
    "Light" : {"StatusBar": "E0E0E0","AppBar": "#202020","Background": "#EEEEEE","CardsDialogs": "#FFFFFF","FlatButtonDown": "#CCCCCC",},
    "Dark"  : {"StatusBar": "101010","AppBar": "#E0E0E0","Background": "#111111","CardsDialogs": "#222222","FlatButtonDown": "#DDDDDD",},
}

config_name = 'config.ini'
config_full_path = os.path.join(application_path, config_name)
config = configparser.ConfigParser()
config.read(config_full_path)

## App Setting
APP_TITLE = config['app']['APP_TITLE']
APP_SUBTITLE = config['app']['APP_SUBTITLE']
IMG_LOGO_PEMKAB = config['app']['IMG_LOGO_PEMKAB']
IMG_LOGO_DISHUB = config['app']['IMG_LOGO_DISHUB']
LB_PEMKAB = config['app']['LB_PEMKAB']
LB_DISHUB = config['app']['LB_DISHUB']
LB_UNIT = config['app']['LB_UNIT']
LB_UNIT_ADDRESS = config['app']['LB_UNIT_ADDRESS']

# SQL setting
DB_HOST = "187.77.112.162"
DB_USER = "Pndujikir2026!"  
DB_PASSWORD = "@PndKir2026!"

DB_NAME = "pkbpandeglang"
TB_DATA = "tb_cekident"
TB_USER = "users"
TB_MERK = "merk"
TB_BAHAN_BAKAR = "bahanbakar"
TB_WARNA = "warna"
TB_DATA_MASTER = "identkendaraan"

FTP_HOST = "187.117.112.162"
FTP_USER = "root"
FTP_PASS = "@SorongNew2026"

class ScreenHome(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenHome, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 1)
    
    def delayed_init(self, dt):
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE        
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS

    def on_enter(self):
        Clock.schedule_interval(self.regular_update_carousel, 3)

    def on_leave(self):
        Clock.unschedule(self.regular_update_carousel)

    def regular_update_carousel(self, dt):
        try:
            self.ids.carousel.index += 1

        except Exception as e:
            toast_msg = f'Gagal Memperbaharui Tampilan Carousel'
            toast_msg = f'Error Update Carousel: {e}'
            toast(toast_msg)                

    def exec_navigate_home(self):
        try:
            self.screen_manager.current = 'screen_home'

        except Exception as e:
            toast_msg = f'Error Navigate to Home Screen: {e}'
            toast(toast_msg)        

    def exec_navigate_login(self):
        global dt_user
        try:
            if (dt_user == ""):
                self.screen_manager.current = 'screen_login'
            else:
                toast(f"Anda sudah login sebagai {dt_user}")

        except Exception as e:
            toast_msg = f'Terjadi kesalahan saat berpindah ke halaman Login'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

    def exec_navigate_main(self):
        try:
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Terjadi kesalahan saat berpindah ke halaman Utama'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

class ScreenLogin(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenLogin, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 1)
    
    def delayed_init(self, dt):
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE  
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS

    def exec_cancel(self):
        try:
            self.ids.tx_username.text = ""
            self.ids.tx_password.text = ""    
        except Exception as e:
            toast_msg = f'error Login: {e}'

    # def exec_login(self):
    #     global mydb, db_users
    #     global dt_id_user, dt_user, dt_foto_user
    #     screen_main = self.screen_manager.get_screen('screen_main')

    #     try:
    #         screen_main.exec_reload_database()
    #         input_username = self.ids.tx_username.text
    #         input_password = self.ids.tx_password.text        
    #         dataBase_password = input_password
    #         hashed_password = hashlib.md5(dataBase_password.encode())
    #         mycursor = mydb.cursor()
    #         mycursor.execute(f"SELECT id_user, nama, username, password, image FROM {TB_USER} WHERE username = '{input_username}' and password = '{hashed_password.hexdigest()}'")
    #         myresult = mycursor.fetchone()
    #         db_users = np.array(myresult).T
            
    #         if myresult is None:
    #             toast_msg = f'Gagal Masuk, Nama Pengguna atau Password Salah'
    #             toast(toast_msg) 
    #             Logger.warning(f"{self.name}: {toast_msg}") 
    #         else:
    #             toast_msg = f'Berhasil Masuk, Selamat Datang {myresult[1]}'
    #             toast(toast_msg)
    #             Logger.info(f"{self.name}: {toast_msg}")  
    #             dt_id_user = myresult[0]
    #             dt_user = myresult[1]
    #             dt_foto_user = myresult[4]
    #             self.ids.tx_username.text = ""
    #             self.ids.tx_password.text = "" 
    #             self.screen_manager.current = 'screen_main'

    #     except Exception as e:
    #         toast_msg = f'Gagal masuk, silahkan isi nama user dan password yang sesuai'
    #         toast(toast_msg)  
    #         Logger.error(f"{self.name}: {toast_msg}, {e}")  

# ... di dalam class ScreenLogin ...

    def exec_login(self):
        # Gunakan global agar ID dan Nama bisa dipakai di layar lain (Saving data)
        global mydb, dt_id_user, dt_user, dt_foto_user
        
        screen_main = self.screen_manager.get_screen('screen_main')
        TB_WEB_USER = "web_users" 

        try:
            screen_main.exec_reload_database()
            input_email = self.ids.tx_username.text
            input_password = self.ids.tx_password.text        
            
            mycursor = mydb.cursor()
            
            # 1. Ambil ID, Name, dan Password (untuk diverifikasi bcrypt)
            # Pastikan kolom 'tipe_user' namanya sudah sesuai dengan di DB
            query = f"SELECT id, name, email, password FROM {TB_WEB_USER} WHERE email = %s AND tipe_user = '2'"
            
            mycursor.execute(query, (input_email,))
            myresult = mycursor.fetchone()
            
            if myresult:
                db_id = myresult[0]
                db_name = myresult[1]
                db_hashed_password = myresult[3] 

                # 2. Verifikasi Password
                import bcrypt # Sebaiknya pindahkan ke baris paling atas file script Anda
                if bcrypt.checkpw(input_password.encode('utf-8'), db_hashed_password.encode('utf-8')):
                    
                    # SIMPAN KE VARIABEL GLOBAL
                    dt_id_user = db_id    # Ini yang nanti masuk ke 'emission_user'
                    dt_user = db_name      # Ini yang tampil di Dashboard "Login Sebagai: ..."
                    dt_foto_user = ""      # Kosong karena kolom 'image' tidak ada
                    
                    toast(f"Berhasil Masuk, Selamat Datang {dt_user}")
                    
                    # Reset input field
                    self.ids.tx_username.text = ""
                    self.ids.tx_password.text = "" 
                    
                    # Pindah Layar
                    self.screen_manager.current = 'screen_main'
                else:
                    toast("maaf username dan password tidak sesuai")
            else:
                # Email tidak ditemukan atau tipe_user bukan '2'
                toast("maaf username dan password tidak sesuai")

        except Exception as e:
            Logger.error(f"Login Error: {e}")
            toast("Gagal terhubung ke database")

    def exec_navigate_home(self):
        try:
            self.screen_manager.current = 'screen_home'

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Awal'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")

    def exec_navigate_login(self):
        global dt_user
        try:
            if (dt_user == ""):
                self.screen_manager.current = 'screen_login'
            else:
                toast_msg = f"Anda sudah login sebagai {dt_user}"
                toast(toast_msg)
                Logger.info(f"{self.name}: {toast_msg}")  

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Login'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

    def exec_navigate_main(self):
        try:
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Utama'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

class ScreenMain(MDScreen):   
    def __init__(self, **kwargs):
        super(ScreenMain, self).__init__(**kwargs)
        global dt_user, dt_foto_user, dt_no_antri, dt_no_pol, dt_no_uji, dt_sts_uji, dt_nama
        global dt_merk, dt_type, dt_jns_kend, dt_jbb, dt_brt_ksg, dt_bhn_bkr, dt_warna, dt_chasis, dt_no_mesin
        global dt_id_user
        global dt_dash_pendaftaran, dt_dash_belum_uji, dt_dash_sudah_uji

        dt_user = dt_foto_user = dt_no_antri = dt_no_pol = dt_no_uji = dt_sts_uji = dt_nama = ""
        dt_merk = dt_type = dt_jns_kend = dt_jbb = dt_brt_ksg = dt_bhn_bkr = dt_warna = dt_chasis = dt_no_mesin = ""
        dt_id_user = 0
        dt_dash_pendaftaran = dt_dash_belum_uji = dt_dash_sudah_uji = 0
        
        Clock.schedule_once(self.delayed_init, 1)

    def delayed_init(self, dt):   
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE              
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS
        
        Clock.schedule_interval(self.regular_update_display, 1)

    def on_enter(self):
        self.exec_reload_database()
        self.exec_reload_table()

    def regular_update_display(self, dt):
        try:
            current_time = str(time.strftime("%H:%M:%S", time.localtime()))
            current_date = str(time.strftime("%d/%m/%Y", time.localtime()))
            
            # Sesuaikan dengan nama screen di Smoke App Anda
            screens_to_update = ['screen_home', 'screen_login', 'screen_smoke_test', 'screen_Calibration']
            for screen_name in screens_to_update:
                try:
                    screen = self.screen_manager.get_screen(screen_name)
                    screen.ids.lb_time.text = current_time
                    screen.ids.lb_date.text = current_date
                except: pass

            self.ids.lb_time.text = current_time
            self.ids.lb_date.text = current_date
            self.ids.lb_dash_pendaftaran.text = str(dt_dash_pendaftaran)
            self.ids.lb_dash_belum_uji.text = str(dt_dash_belum_uji)
            self.ids.lb_dash_sudah_uji.text = str(dt_dash_sudah_uji)
            
            login_text = f'Login Sebagai: \n{dt_user}' if dt_user else 'Silahkan Login'
            user_image = f'https://{FTP_HOST}/ujikir/foto_user/{dt_foto_user}' if dt_user else 'assets/images/icon-login.png'

            self.ids.lb_operator.text = login_text
            self.ids.img_user.source = user_image
            self.ids.bt_logout.disabled = not dt_user

        except Exception as e:
            Logger.error(f"{self.name}: Update Display Error, {e}")

    def exec_reload_database(self):
        global mydb
        try:
            mydb = mysql.connector.connect(host = DB_HOST,user = DB_USER,password = DB_PASSWORD, database = DB_NAME)
        except Exception as e:
            toast('Gagal Menginisiasi Database')

    def exec_reload_table(self):
        """Reload tabel antrian khusus fokus pada Smoke (Solar)."""
        global mydb, db_antrian, db_merk, db_bahan_bakar, db_warna
        global dt_dash_pendaftaran, dt_dash_belum_uji, dt_dash_sudah_uji

        try:
            cursor = mydb.cursor()
            today = str(time.strftime("%Y-%m-%d", time.localtime()))

            cursor.execute(f"SELECT ID, DESCRIPTION FROM {TB_MERK}")
            db_merk = np.array(cursor.fetchall())
            cursor.execute(f"SELECT id_warna, nama FROM {TB_WARNA}")
            db_warna = np.array(cursor.fetchall())
            
            # Hitung Dashboard khusus Smoke
            cursor.execute(f"SELECT COUNT(*) FROM {TB_DATA} WHERE DATE(tgl_daftar) = %s AND bahan_bakar = 'S'", (today,))
            dt_dash_pendaftaran = cursor.fetchone()[0] or 0

            cursor.execute(f"SELECT COUNT(*) FROM {TB_DATA} WHERE DATE(tgl_daftar) = %s AND bahan_bakar = 'S' AND emission_smoke_flag IN (0, 1)", (today,))
            dt_dash_sudah_uji = cursor.fetchone()[0] or 0
            
            dt_dash_belum_uji = dt_dash_pendaftaran - dt_dash_sudah_uji
            
            # Query hanya kendaraan SOLAR ('S') yang BELUM UJI (flag bukan 0 atau 1)
            query_table = f"""
                SELECT noantrian, nopol, nouji, statusuji, merk, type, idjeniskendaraan, 
                    jbb, berat_kosong, bahan_bakar, warna, th_buat, emission_smoke_flag 
                FROM {TB_DATA} 
                WHERE bahan_bakar = 'S' AND emission_smoke_flag NOT IN (0, 1) AND DATE(tgl_daftar) = %s
            """
            cursor.execute(query_table, (today,))
            result_tb_antrian = cursor.fetchall()
            
            db_antrian = np.array(result_tb_antrian).T if result_tb_antrian else np.array([])
            cursor.close()

            # Render ke Layout
            layout_list = self.ids.layout_list
            layout_list.clear_widgets()
            
            if db_antrian.size == 0:
                layout_list.add_widget(MDLabel(text="Semua kendaraan solar sudah diuji.", halign="center", theme_text_color="Secondary"))
                return

            for i in range(db_antrian.shape[1]):
                # Mapping data sesuai indeks query
                merk_id = db_antrian[4, i]
                merk_row = db_merk[db_merk[:, 0] == merk_id]
                merk_text = merk_row[0, 1] if merk_row.size > 0 else '-'

                warna_id = db_antrian[10, i]
                warna_row = db_warna[db_warna[:, 0] == warna_id]
                warna_text = warna_row[0, 1] if warna_row.size > 0 else '-'

                bahan_bakar_raw = db_antrian[9, i]
                bahan_bakar_text = "Solar" if bahan_bakar_raw == 'S' else bahan_bakar_raw

                smoke_flag = db_antrian[12, i]
                smoke_stat = "BELUM UJI" if smoke_flag not in [0, 1] else f"{smoke_flag}%"

                # Tambahkan Row ke layout_list
                # PENTING: size_hint_x harus SAMA PERSIS dengan di file .kv
                layout_list.add_widget(
                    MDCard(
                        MDLabel(text=f"{db_antrian[0, i]}", halign="center", size_hint_x=0.05), # Antrian
                        MDLabel(text=f"{db_antrian[1, i]}", halign="center", size_hint_x=0.08), # No Reg
                        MDLabel(text=f"{db_antrian[2, i]}", halign="center", size_hint_x=0.10), # No Uji
                        MDLabel(text='Berkala' if db_antrian[3, i] == 'B' else 'Uji Ulang' if (db_antrian[3, i]) == 'U' else 'Baru' if (db_antrian[3, i]) == 'BR' else 'Numpang Uji' if (db_antrian[3, i]) == 'NB' else 'Mutasi', halign="center", size_hint_x= 0.05),
                        MDLabel(text=merk_text, halign="center", size_hint_x=0.08),             # Merk
                        MDLabel(text=f"{db_antrian[5, i]}", halign="center", size_hint_x=0.10), # Type
                        MDLabel(text=f"{db_antrian[6, i]}", halign="center", size_hint_x=0.12), # Jenis
                        MDLabel(text=f"{db_antrian[7, i]}", halign="center", size_hint_x=0.06), # JBB
                        MDLabel(text=f"{db_antrian[8, i]}", halign="center", size_hint_x=0.06), # Brt Ksg
                        MDLabel(text=bahan_bakar_text, halign="center", size_hint_x=0.08), # Bahan_B
                        MDLabel(text=warna_text, halign="center", size_hint_x=0.08),            # Warna
                        MDLabel(text=f"{db_antrian[11, i]}", halign="center", size_hint_x=0.05),# Thn
                        MDLabel(text=smoke_stat, halign="center", size_hint_x=0.10, theme_text_color="Error"), # SMOKE
                        
                        ripple_behavior=True,
                        on_press=self.on_antrian_row_press,
                        padding="5dp", 
                        id=f"card_antrian{i}",
                        size_hint_y=None, 
                        height=dp(45)
                    )
                )

        except Exception as e:
            toast('Gagal memuat ulang tabel antrian')
            Logger.error(f"{self.name}: Reload Table Error, {e}")

    def on_antrian_row_press(self, instance):
        """Logika klik baris antrian khusus Smoke."""
        global dt_user, dt_no_antri, dt_no_pol, dt_no_uji, dt_sts_uji, dt_merk, dt_type
        global dt_jns_kend, dt_jbb, dt_brt_ksg, dt_bhn_bkr, dt_warna, dt_thn_buat

        try:
            if not dt_user:
                toast("Silakan login terlebih dahulu.")
                return

            row = int(str(instance.id).replace("card_antrian", ""))
            
            # Mapping data dari query exec_reload_table
            dt_no_antri = db_antrian[0, row]
            dt_no_pol   = db_antrian[1, row]
            dt_no_uji   = db_antrian[2, row]
            dt_sts_uji  = db_antrian[3, row]
            dt_merk     = db_antrian[4, row]
            dt_type     = db_antrian[5, row]
            dt_jns_kend = db_antrian[6, row]
            dt_jbb      = db_antrian[7, row]
            dt_brt_ksg  = db_antrian[8, row]
            dt_bhn_bkr  = db_antrian[9, row]
            dt_warna    = db_antrian[10, row]
            dt_thn_buat = db_antrian[11, row]
            
            # Update data ke global App agar bisa dibaca Screensmoketest
            app = MDApp.get_running_app()
            app.dt_no_antri = str(dt_no_antri)
            app.dt_no_pol   = str(dt_no_pol)
            app.dt_no_uji   = str(dt_no_uji)
            app.dt_jbb = str(db_antrian[7, row]) 
            app.dt_thn_buat = str(db_antrian[11, row])
            
            # Pindah ke layar pengujian asap
            self.screen_manager.current = 'screen_smoke_test'

        except Exception as e:
            toast('Gagal memproses data antrian')
            Logger.error(f"{self.name}: Row Press Error, {e}")

    def exec_logout(self):
        global dt_user
        dt_user = ""
        self.screen_manager.current = 'screen_login'

    def exec_navigate_home(self):
        self.screen_manager.current = 'screen_home'

    def exec_navigate_login(self):
        if not dt_user:
            self.screen_manager.current = 'screen_login'
        else:
            toast(f"Anda sudah login sebagai {dt_user}")

    def exec_navigate_main(self):
        self.screen_manager.current = 'screen_main'


class Screensmoketest(MDScreen):
    opasitas_saat_ini = NumericProperty(0.0)
    suhu_saat_ini = NumericProperty(0.0)
    countdown_val = NumericProperty(0)
    status_teks = StringProperty("READY")
    hasil_akhir = StringProperty("- %")
    list_peak = ListProperty([])
    hasil_uji = StringProperty("-")
    dt_no_antri = StringProperty("-")
    dt_no_pol = StringProperty("-")
    dt_no_uji = StringProperty("-")
    dt_jbb = StringProperty("-")       # <--- TAMBAHKAN INI
    dt_thn_buat = StringProperty("-")  # <--- TAMBAHKAN INI

    def __init__(self, **kwargs):
        super(Screensmoketest, self).__init__(**kwargs)
        self.peak_temp_val = 0.0 #
    
    def delayed_init(self, dt):
        """Inisialisasi tampilan header/footer secara aman."""
        self._safe_update_text('lb_title', APP_TITLE)
        self._safe_update_text('lb_subtitle', APP_SUBTITLE)
        self._safe_update_source('img_pemkab', f'assets/images/{IMG_LOGO_PEMKAB}')
        self._safe_update_source('img_dishub', f'assets/images/{IMG_LOGO_DISHUB}')
        self._safe_update_text('lb_pemkab', LB_PEMKAB)
        self._safe_update_text('lb_dishub', LB_DISHUB)
        self._safe_update_text('lb_unit', LB_UNIT)
        self._safe_update_text('lb_unit_address', LB_UNIT_ADDRESS)

    def on_enter(self, *args):
        MDApp.get_running_app().send_command("L1")
        Clock.schedule_interval(self.check_temp_status, 0.5)

    def on_leave(self, *args):
        """Dijalankan otomatis setiap kali meninggalkan layar smoke test"""
        self.list_peak = []
        
        self.peak_temp_val = 0.0
        
        self.hasil_uji = "-"
        self.hasil_akhir = "- %"
        
        if 'lbl_hasil_k' in self.ids:
            self.ids.lbl_hasil_k.text = "0.00"
        if 'lbl_hasil_opasitas' in self.ids:
            self.ids.lbl_hasil_opasitas.text = "0.0 %"
            
        # 4. Hentikan semua schedule timer jika masih jalan
        Clock.unschedule(self.update_simulation_test)
        Clock.unschedule(self.update_countdown)
        
        Logger.info("SmokeScreen: Data pengujian telah dibersihkan.")

    def check_temp_status(self, dt):
        app = MDApp.get_running_app()
        cal_screen = self.manager.get_screen('screen_Calibration')
        
        # PERBAIKAN 1: Suhu tetap diupdate meskipun mode simulasi AKTIF
        self.suhu_saat_ini = float(app.latest_data[1])
        
        if not cal_screen.mode_simulasi:
            self.opasitas_saat_ini = float(app.latest_data[3])
        
        # Logika tombol start (Range suhu 10-90 C)
        if 10 <= self.suhu_saat_ini <= 90:
            self.ids.btn_start.disabled = False
        else:
            if self.status_teks == "READY":
                self.ids.btn_start.disabled = True

    @mainthread
    def update_ui(self, data):
        pass # UI sudah diupdate secara reaktif melalui properti di check_temp_status

    def start_testing_sequence(self):
        app = MDApp.get_running_app()
        cal_screen = self.manager.get_screen('screen_Calibration')
        
        self.status_teks = "MEASURING..."
        self.peak_temp_val = 0.0 # Reset Peak
        self.opasitas_saat_ini = 0.0 # Reset Realtime display
        
        app.send_command("SR0")
        app.send_command("F10")
        app.send_command("F20")
        
        if cal_screen.mode_simulasi:
            try:
                # Ambil target dari menu kalibrasi
                self.target_sim = float(cal_screen.ids.ent_target_dummy.text)
            except:
                self.target_sim = 24.0
            
            self.countdown_val = 5.0
            # Gunakan interval sedikit lebih lambat (0.15s) agar mata manusia bisa mengikuti perubahan angka
            Clock.unschedule(self.update_simulation_test)
            Clock.schedule_interval(self.update_simulation_test, 0.15)
        else:
            self.countdown_val = 10.0
            Clock.schedule_interval(self.update_countdown, 1)
            Clock.schedule_once(self.stop_and_purge, 10)

    def update_countdown(self, dt):
        if self.countdown_val > 0:
            self.countdown_val -= 1
            if self.opasitas_saat_ini > self.peak_temp_val:
                self.peak_temp_val = self.opasitas_saat_ini
            return True
        return False 

    def stop_and_purge(self, dt):
        app = MDApp.get_running_app()
        
        # Hentikan semua schedule agar tidak double hitung
        Clock.unschedule(self.update_simulation_test)
        Clock.unschedule(self.update_countdown)

        # Jika peak masih 0 (kasus langka), ambil nilai terakhir display
        if self.peak_temp_val <= 0:
            self.peak_temp_val = self.opasitas_saat_ini

        # Simpan ke riwayat
        if self.peak_temp_val > 0:
            self.list_peak.append(self.peak_temp_val)
            toast(f"Peak Tercatat: {self.peak_temp_val}%")
        
        self.status_teks = "PURGING..."
        app.send_command("F11")
        app.send_command("F21")
        
        # Reset display opasitas agar user tahu tes sudah selesai
        self.opasitas_saat_ini = 0.0
        
        Clock.schedule_once(self.auto_stop_fan, 5)
    
    def auto_stop_fan(self, dt):
        """Mematikan kipas secara fisik dan reset status UI"""
        app = MDApp.get_running_app()
        app.send_command("F10")
        app.send_command("F20")
        self.status_teks = "READY"
        toast("Purging Otomatis Selesai")
    
    def reset_to_ready(self, dt):
        app = MDApp.get_running_app()
        app.send_command("F10")
        app.send_command("F20")
        # Heater otomatis kembali standby via logika global di App
        app.auto_temp_control = True 
        self.status_teks = "READY"
        self.countdown_val = 0

    def delete_last_test(self):
        """Menghapus data pengujian terakhir jika salah"""
        if self.list_peak:
            self.list_peak.pop()
            toast("Data terakhir dihapus")
        else:
            toast("Riwayat sudah kosong")

    def calculate_results(self):
        """Hanya menghitung dan menampilkan hasil di layar (Tidak Simpan)"""
        if not self.list_peak:
            toast("Lakukan pengujian minimal 1 kali!")
            return
            
        avg_opacity = sum(self.list_peak) / len(self.list_peak)
        self.avg_final_val = round(avg_opacity, 1) # Simpan ke variabel untuk SQL nanti
        
        # Logika Ambil JBB & Tahun untuk evaluasi status (LULUS/TIDAK)
        app = MDApp.get_running_app()
        try:
            jbb = int("".join(filter(str.isdigit, app.dt_jbb)))
            tahun = int("".join(filter(str.isdigit, app.dt_thn_buat)))
            
            # Hitung Limit sesuai tabel
            limit = 100.0
            if jbb <= 3500:
                limit = 65.0 if tahun < 2010 else 40.0 if tahun <= 2021 else 30.0
            else:
                limit = 65.0 if tahun < 2010 else 40.0 if tahun <= 2021 else 35.0
            
            self.hasil_uji = "LULUS" if self.avg_final_val <= limit else "TIDAK LULUS"
            self.smoke_flag_val = 1 if self.hasil_uji == "LULUS" else 0
        except:
            self.hasil_uji = "ERROR DATA"

        # Update UI Labels
        self.ids.lbl_hasil_opasitas.text = f"{self.avg_final_val} %"
        # Hitung K
        try:
            N = self.avg_final_val / 100.0
            k_val = -(1/0.29) * math.log(1 - N) if N < 1.0 else 9.99
            self.ids.lbl_hasil_k.text = f"{k_val:.2f}"
        except: self.ids.lbl_hasil_k.text = "0.00"
        
        toast("Hasil Kalkulasi Terupdate")

    def exec_save_diesel(self):
        """Menyimpan hasil ke database"""
        if self.hasil_uji == "-" or self.avg_final_val == 0.0:
            toast("Tekan CALCULATE terlebih dahulu!")
            return

        # Pastikan dt_id_user dipanggil di baris global ini
        global mydb, dt_no_antri, dt_id_user 
        
        try:
            now = datetime.datetime.now()
            waktu_simpan = now.strftime("%H:%M:%S") 
            
            cursor = mydb.cursor()
            
            # Perhatikan bagian emission_user = %s
            sql = f"""UPDATE {TB_DATA} SET 
                      emission_smoke_value = %s, 
                      emission_smoke_flag = %s,
                      emission_user = %s,    # <--- ID Operator masuk ke sini
                      emission_post = %s
                      WHERE noantrian = %s"""
            
            # Pastikan urutan variabel di bawah ini sama dengan urutan %s di atas
            # dt_id_user berada di urutan ke-3
            val = (self.avg_final_val, self.smoke_flag_val, dt_id_user, waktu_simpan, dt_no_antri)
            
            cursor.execute(sql, val)
            mydb.commit()
            
            toast(f"Data Berhasil Disimpan oleh ID: {dt_id_user}")
            self.exec_navigate_main()
            
        except Exception as e:
            Logger.error(f"Save Error: {e}")
            toast("Gagal menyimpan ke Database!")

    def exec_navigate_main(self):
        self.manager.current = 'screen_main'

    def update_simulation_test(self, dt):
        self.countdown_val -= 0.15
        
        if 'lbl_timer' in self.ids:
            self.ids.lbl_timer.text = f"{max(0, self.countdown_val):.1f} s"
        
        # LOGIKA VARIASI: 
        # Kita buat rentang yang lebih lebar di awal, lalu mengecil (stabil) di akhir
        if self.countdown_val > 2.5:
            # Fase awal: Angka melonjak drastis (simulasi asap masuk pertama kali)
            multiplier = random.uniform(0.7, 1.15)
        else:
            # Fase akhir: Angka mulai stabil di sekitar target
            multiplier = random.uniform(0.92, 1.08)
            
        noise = random.uniform(-0.5, 0.5) # Noise tambahan agar angka belakang koma unik
        hasil_now = (self.target_sim * multiplier) + noise
        
        self.opasitas_saat_ini = round(hasil_now, 1)
        
        # Kunci: Selalu simpan nilai tertinggi yang pernah muncul selama 5 detik ini
        if self.opasitas_saat_ini > self.peak_temp_val:
            self.peak_temp_val = self.opasitas_saat_ini

        if self.countdown_val <= 0:
            Clock.unschedule(self.update_simulation_test)
            self.stop_and_purge(None)
            return False 
        return True


    def manual_purging_start(self):
        """Fungsi yang dipanggil saat tombol PURGING kuning ditekan"""
        app = MDApp.get_running_app()
        
        # 1. Nyalakan Kipas (Kirim perintah F11 dan F21)
        app.send_command("F11")
        app.send_command("F21")
        
        self.status_teks = "MANUAL PURGING..."
        toast("Purging dimulai (20 detik)")
        
        # 2. Jadwalkan untuk mati otomatis 20 detik dari sekarang
        # Pastikan kita bersihkan jadwal lama jika tombol ditekan berkali-kali
        Clock.unschedule(self.auto_stop_fan) 
        Clock.schedule_once(self.auto_stop_fan, 20)


class ScreenCalibration(MDScreen):
    mode_simulasi = BooleanProperty(False) # Status Saklar
    target_manipulasi = NumericProperty(0.0)
    perekaman_aktif = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(ScreenCalibration, self).__init__(**kwargs)
        self.btn_status = {}
        self.auto_temp_control = False
        self.heater_is_on = False 
        Clock.schedule_once(self.delayed_init, 1)

    def toggle_mode_manipulasi(self, active):
        self.mode_simulasi = active
        self.perekaman_aktif = False # Reset status perekaman normal
        self.ids.btn_test_sim.text = "TEST" # Kembalikan teks tombol
        
        if active:
            toast("Mode Kalibrasi Aktif")
        else:
            toast("Kembali ke Mode Normal")


    def delayed_init(self, dt):
        self._safe_update_text('lb_title', APP_TITLE)
        self._safe_update_text('lb_subtitle', APP_SUBTITLE)
        self._safe_update_source('img_pemkab', f'assets/images/{IMG_LOGO_PEMKAB}')
        self._safe_update_source('img_dishub', f'assets/images/{IMG_LOGO_DISHUB}')
        self._safe_update_text('lb_pemkab', LB_PEMKAB)
        self._safe_update_text('lb_dishub', LB_DISHUB)
        self._safe_update_text('lb_unit', LB_UNIT)
        self._safe_update_text('lb_unit_address', LB_UNIT_ADDRESS)
        adc_t = config.get('app', 'ADC_TERANG', fallback="2786.4")
        adc_g = config.get('app', 'ADC_GELAP', fallback="2664.0")
        
        if 'ent_adc_terang' in self.ids:
            self.ids.ent_adc_terang.text = adc_t
        if 'ent_adc_gelap' in self.ids:
            self.ids.ent_adc_gelap.text = adc_g
            
        self.build_actuator_buttons()

    def _safe_update_text(self, widget_id, text_val):
        if widget_id in self.ids: self.ids[widget_id].text = str(text_val)

    def _safe_update_source(self, widget_id, source_path):
        if widget_id in self.ids: self.ids[widget_id].source = source_path

    def on_enter(self, *args):
        self.refresh_ports()
        app = MDApp.get_running_app()
        if app.auto_temp_control:
            self.ids.btn_auto_warm.md_bg_color = [1, 0.76, 0.03, 1]
            self.ids.btn_auto_warm.text = "WARMING UP PROCCESS..."

    def on_leave(self, *args):
        pass

    def refresh_ports(self):
        try:
            ports = [port.device for port in serial.tools.list_ports.comports()]
            if 'port_spinner' in self.ids:
                self.ids.port_spinner.values = ports
                if ports:
                    self.ids.port_spinner.text = ports[0]
                else:
                    self.ids.port_spinner.text = "Pilih Port"
        except Exception as e:
            pass

    def toggle_connection(self):
        app = MDApp.get_running_app()
        if not app.running:
            port = self.ids.port_spinner.text
            if port == "Pilih Port" or not port:
                toast("Pilih Port Valid!")
                return
            try:
                app.ser = serial.Serial(port, 115200, timeout=1)
                app.running = True

                self.ids.btn_test_sim.disabled = False
                adc_t = config.get('app', 'ADC_TERANG', fallback="2786.4")
                adc_g = config.get('app', 'ADC_GELAP', fallback="2664.0")
                self.send(f"CAL_T:{adc_t}")
                time.sleep(0.1)
                self.send(f"CAL_G:{adc_g}")
                
                self.ids.btn_connect.text = "DISCONNECT"
                self.ids.btn_connect.md_bg_color = [0.87, 0.13, 0.13, 1]
                
                self.ids.lbl_conn_status.text = f"CONNECTED: {port}"
                self.ids.lbl_conn_status.theme_text_color = "Custom"
                self.ids.lbl_conn_status.text_color = [0.17, 0.63, 0.17, 1] 
                
                threading.Thread(target=app.read_serial_global, daemon=True).start()
                toast("Berhasil Terhubung!")
            except Exception as e:
                toast(f"Gagal: {e}")
                
        else:
            app.running = False
            if app.ser: app.ser.close()
            self.ids.btn_test_sim.disabled = True
            self.ids.btn_connect.text = "CONNECT"
            self.ids.btn_connect.md_bg_color = [0.17, 0.63, 0.17, 1] # Ganti tombol jadi Hijau
            
            self.ids.lbl_conn_status.text = "DISCONNECTED"
            self.ids.lbl_conn_status.theme_text_color = "Custom"
            self.ids.lbl_conn_status.text_color = [0.87, 0.13, 0.13, 1] # Merah [cite: 2026-03-09]
            self.ids.lbl_conn_status.opacity = 1.0 # Tetap 100% agar terbaca jelas [cite: 2026-03-09]

    def send(self, cmd):
        return MDApp.get_running_app().send_command(cmd)

    def jalankan_test_manipulasi(self):
        app = MDApp.get_running_app()
        
        # JIKA SEDANG PEREKAMAN (MODE NORMAL), TEKAN TEST LAGI UNTUK RESET KE REAL-TIME
        if not self.mode_simulasi and self.perekaman_aktif:
            self.perekaman_aktif = False
            Clock.unschedule(self.update_average_normal)
            toast("Kembali ke Real-time")
            return

        if self.mode_simulasi:
            # --- MODE KALIBRASI (SIMULASI TARGET) ---
            try:
                self.target_val = float(self.ids.ent_target_dummy.text)
                self.sim_duration = 0 
                self.ids.btn_test_sim.disabled = True 
                Clock.schedule_interval(self.update_random_number, 0.5)
                toast("Simulasi Kalibrasi Dimulai...")
            except ValueError:
                toast("Masukkan angka target valid!")
        else:
            # --- MODE NORMAL (RATA-RATA DATA ASLI) ---
            if not app.running:
                toast("Sambungkan alat terlebih dahulu!")
                return
                
            self.sim_duration = 0
            self.data_buffer = [] # Untuk menampung data selama 5 detik
            self.perekaman_aktif = True
            self.ids.btn_test_sim.text = "STOP / RESET" # Ubah teks tombol sementara
            self.ids.btn_test_sim.md_bg_color = [0.9, 0.1, 0.1, 1] # Merah
            
            Clock.schedule_interval(self.update_average_normal, 0.1)
            toast("Merekam data 5 detik...")

    def update_average_normal(self, dt):
        app = MDApp.get_running_app()
        self.sim_duration += 0.1
        
        # Ambil data opasitas asli dari sensor
        try:
            val_now = float(app.latest_data[3])
            self.data_buffer.append(val_now)
            
            # Tampilkan angka yang sedang berjalan agar tidak terlihat freeze
            self.ids.lbl_opasitas.text = f"{val_now:.1f}%"
            self.ids.lbl_opasitas.text_color = [0.1, 0.5, 0.9, 1] # Warna Biru (Sedang proses)
        except: pass

        if self.sim_duration >= 5.0:
            # Hitung Rata-rata setelah 5 detik
            if self.data_buffer:
                rata_rata = sum(self.data_buffer) / len(self.data_buffer)
                self.ids.lbl_opasitas.text = f"{rata_rata:.1f}%"
                self.ids.lbl_opasitas.text_color = [0.17, 0.63, 0.17, 1] # Hijau (Hasil Akhir)
                toast(f"Rata-rata 5 detik: {rata_rata:.1f}%")
            
            self.perekaman_aktif = True # Tetap True agar tekan tombol lagi bisa reset
            self.ids.btn_test_sim.text = "TEST KEMBALI"
            self.ids.btn_test_sim.md_bg_color = [0.2, 0.6, 0.2, 1] # Hijau Tua
            return False # Berhenti merekam
            
        return True

    def update_random_number(self, dt):
        self.sim_duration += 0.5
        
        # --- UBAH TOLERANSI 8% DI SINI ---
        # 0.08 artinya 8% dari target yang diinput di kotak putih
        rentang = self.target_val * 0.08
        fluktuasi = random.uniform(-rentang, rentang)
        
        hasil_display = self.target_val + fluktuasi
        
        # Update tampilan angka di tengah layar
        self.ids.lbl_opasitas.text = f"{max(0, hasil_display):.1f}%"
        self.ids.lbl_opasitas.text_color = [0.17, 0.63, 0.17, 1] # Tetap Hijau
        
        if self.sim_duration >= 5.0:
            if 'btn_test_sim' in self.ids:
                self.ids.btn_test_sim.disabled = False
            return False 
        return True

    @mainthread
    def update_ui(self, data):
        try:
            chamber_temp = float(data[1])
            
            # 1. Update Opasitas (Logika Dual Mode)
            # JANGAN update teks lbl_opasitas jika:
            # - Sedang simulasi kalibrasi (biarkan fungsi simulasi yang handle)
            # - Sedang perekaman normal (biarkan fungsi perekaman yang handle)
            if not self.mode_simulasi and not self.perekaman_aktif:
                val_opasitas = float(data[3])
                if 'lbl_opasitas' in self.ids:
                    self.ids.lbl_opasitas.text = f"{val_opasitas:.1f}%"
                    
                    # Warna indikator standar (Hitam/Default saat standby)
                    if val_opasitas > 40.0:
                        self.ids.lbl_opasitas.text_color = [1, 0.16, 0.16, 1] # Merah
                    else:
                        self.ids.lbl_opasitas.text_color = [0, 0, 0, 1] # Hitam/Normal

            # 2. Update sensor pendukung lainnya (Selalu update agar tidak terlihat freeze)
            if 'lbl_gas' in self.ids: self.ids.lbl_gas.text = f"{float(data[0]):.1f} C"
            if 'lbl_tabung' in self.ids: self.ids.lbl_tabung.text = f"{chamber_temp:.1f} C"
            if 'lbl_pres' in self.ids: self.ids.lbl_pres.text = data[2]
            if 'lbl_adc_raw' in self.ids: self.ids.lbl_adc_raw.text = data[4]
            
            # 3. Logika Auto Warming (Tetap berjalan di background)
            if self.auto_temp_control:
                if chamber_temp >= 90.0 and self.heater_is_on:
                    self.heater_is_on = False
                    self.send("SR0")
                    self.update_btn_ui("HEATER (PWM 60)", "OFF")
                    self.ids.btn_auto_warm.md_bg_color = [0.17, 0.8, 0.25, 1]
                    self.ids.btn_auto_warm.text = "SUHU TERJAGA (75-90°C) - SIAP UJI"

                elif chamber_temp <= 75.0 and not self.heater_is_on:
                    self.heater_is_on = True
                    self.send("SR1")
                    self.update_btn_ui("HEATER (PWM 60)", "ON")
                    self.ids.btn_auto_warm.md_bg_color = [1, 0.76, 0.03, 1]
                    self.ids.btn_auto_warm.text = "AUTO WARMING..."

        except (ValueError, IndexError):
            pass

    def toggle_auto_warming(self):
        app = MDApp.get_running_app()
        if not app.running:
            toast("Sambungkan Bluetooth dulu!")
            return

        if not app.auto_temp_control:
            app.auto_temp_control = True
            app.heater_is_on = True
            # Safety Interlock
            self.send("F10"); self.send("F20"); self.send("S0"); self.send("L0")
            self.send("SR1")
            self.ids.btn_auto_warm.md_bg_color = [1, 0.76, 0.03, 1]
            self.ids.btn_auto_warm.text = "WARMING UP PROCCESS..."
        else:
            app.auto_temp_control = False
            app.heater_is_on = False
            self.send("SR0")
            self.ids.btn_auto_warm.md_bg_color = [0.9, 0.9, 0.9, 1]
            self.ids.btn_auto_warm.text = "AUTO WARMING UP (75°C - 90°C)"

    def build_actuator_buttons(self):
        if 'actuator_list' not in self.ids: return
        container = self.ids.actuator_list
        container.clear_widgets()
        
        aktuators = [
            ("HEATER (PWM 60)", "SR1", "SR0"),
            ("COOLING FAN 1", "F11", "F10"),
            ("COOLING FAN 2", "F21", "F20"),
            ("SOLENOID VALVE", "S1", "S0"),
            ("LED OPTICAL", "L1", "L0")
        ]

        for name, on_cmd, off_cmd in aktuators:
            row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(45), spacing=dp(15))
            lbl = MDLabel(text=name, theme_text_color="Primary", size_hint_x=0.5, font_style="Subtitle1", bold=True)
            
            # MDFillRoundFlatButton secara default tidak punya elevation/shadow
            btn_on = MDFillRoundFlatButton(
                text="ON", 
                font_style="H5",
                theme_text_color="Custom",
                text_color=[0, 0, 0, 1], 
                md_bg_color=[0.9, 0.9, 0.9, 1],
                size_hint_x=0.85
            )
            btn_on.bind(on_release=lambda x, n=name, c=on_cmd: self.control_action(n, c, "ON"))
            
            btn_off = MDFillRoundFlatButton(
                text="OFF", 
                font_style="H5",
                theme_text_color="Custom",
                text_color=[0, 0, 0, 1], 
                md_bg_color=[0.26, 0.44, 0.76, 1],
                size_hint_x=0.85
            )
            btn_off.bind(on_release=lambda x, n=name, c=off_cmd: self.control_action(n, c, "OFF"))
            
            self.btn_status[name] = {"on": btn_on, "off": btn_off}
            row.add_widget(lbl)
            row.add_widget(btn_on)
            row.add_widget(btn_off)
            container.add_widget(row)

    def control_action(self, label, cmd, state):
        if self.send(cmd):
            # Interlock Safety Manual
            if label == "HEATER (PWM 60)" and state == "ON":
                self.update_btn_ui("SOLENOID VALVE", "OFF")
            elif label == "SOLENOID VALVE" and state == "ON":
                self.update_btn_ui("HEATER (PWM 60)", "OFF")
            self.update_btn_ui(label, state)

    def update_btn_ui(self, label, state):
        """Ubah warna background, teks dipatenkan hitam."""
        color_active = [0.26, 0.44, 0.76, 1]  # Biru
        color_idle = [0.9, 0.9, 0.9, 1]       # Abu-abu
        text_black = [0, 0, 0, 1]             # Hitam konstan
        
        if state == "ON":
            self.btn_status[label]["on"].md_bg_color = color_active
            self.btn_status[label]["off"].md_bg_color = color_idle
        else:
            self.btn_status[label]["on"].md_bg_color = color_idle
            self.btn_status[label]["off"].md_bg_color = color_active
            
        self.btn_status[label]["on"].text_color = text_black
        self.btn_status[label]["off"].text_color = text_black

    def update_cal_terang(self):
        val = self.ids.ent_adc_terang.text
        if self.send(f"CAL_T:{val}"):
            # Simpan ke memori config saat ini
            config['app']['ADC_TERANG'] = str(val)
            # Tulis secara fisik ke file config.ini
            with open(config_full_path, 'w') as configfile:
                config.write(configfile)
            toast(f"Baseline 0% disimpan ke Config: {val}")

    def update_cal_gelap(self):
        val = self.ids.ent_adc_gelap.text
        if self.send(f"CAL_G:{val}"):
            # Simpan ke memori config saat ini
            config['app']['ADC_GELAP'] = str(val)
            # Tulis secara fisik ke file config.ini
            with open(config_full_path, 'w') as configfile:
                config.write(configfile)
            toast(f"Baseline 100% disimpan ke Config: {val}")

    def exec_navigate_main(self):
        self.manager.current = 'screen_main'

class RootScreen(ScreenManager):
    pass

class DieselsmokemeterApp(MDApp):
    dt_no_antri = StringProperty("-")
    dt_no_pol = StringProperty("-")
    dt_no_uji = StringProperty("-")
    dt_jbb = StringProperty("-")       # <--- TAMBAHKAN INI
    dt_thn_buat = StringProperty("-")  # <--- TAMBAHKAN INI
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ser = None
        self.running = False
        self.auto_temp_control = False
        self.heater_is_on = False
        self.latest_data = ["0", "0", "0", "0", "0"] # [suhuGas, suhuTabung, rawPres, opasitas, rataADC]
        Window.bind(on_resize=self.on_window_resize)

    def build(self):
        global window_size_x, window_size_y
        self.theme_cls.colors = colors
        self.theme_cls.primary_palette = "Gray"
        self.theme_cls.accent_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.icon = 'assets/images/logo-load-app.png'
        Config.set('kivy', 'exit_on_escape', '1')
        window_size_y = Window.size[0]
        window_size_x = Window.size[1]
        self.set_dynamic_fonts(Window.size)

        LabelBase.register(
            name="Orbitron-Regular",
            fn_regular="assets/fonts/Orbitron-Regular.ttf")
        
        LabelBase.register(
            name="Draco",
            fn_regular="assets/fonts/Draco.otf")        

        LabelBase.register(
            name="Recharge",
            fn_regular="assets/fonts/Recharge.otf") 
        
        theme_font_styles.append('H1')
        self.theme_cls.font_styles["H1"] = [
            "Orbitron-Regular", 80, False, 0.15]       

        theme_font_styles.append('H2')
        self.theme_cls.font_styles["H2"] = [
            "Orbitron-Regular", 32, False, 0.15] 
        
        theme_font_styles.append('H4')
        self.theme_cls.font_styles["H4"] = [
            "Recharge", 30, False, 0.15] 

        theme_font_styles.append('H5')
        self.theme_cls.font_styles["H5"] = [
            "Recharge", 20, False, 0.15] 

        theme_font_styles.append('H6')
        self.theme_cls.font_styles["H6"] = [
            "Recharge", 16, False, 0.15] 

        theme_font_styles.append('Subtitle1')
        self.theme_cls.font_styles["Subtitle1"] = [
            "Recharge", 11, False, 0.15] 

        theme_font_styles.append('Body1')
        self.theme_cls.font_styles["Body1"] = [
            "Recharge", 10, False, 0.15] 
        
        theme_font_styles.append('Button')
        self.theme_cls.font_styles["Button"] = [
            "Recharge", 9, False, 0.15] 

        theme_font_styles.append('Caption')
        self.theme_cls.font_styles["Caption"] = [
            "Recharge", 8, False, 0.15]       
        
        Window.fullscreen = 'auto'
        Builder.load_file('main.kv')
        return RootScreen()

    def send_command(self, cmd):
        if self.ser and self.ser.is_open:
            try:
                self.ser.write((cmd + "\n").encode())
                return True
            except:
                return False
        return False

    def read_serial_global(self):
        while self.running:
            if self.ser and self.ser.in_waiting > 0:
                try:
                    line = self.ser.readline().decode('utf-8').strip()
                    data = line.split(',')
                    if len(data) == 5:
                        self.latest_data = data
                        suhu_tabung = float(data[1])
                        
                        if self.auto_temp_control:
                            if suhu_tabung >= 90.0 and self.heater_is_on:
                                self.heater_is_on = False
                                self.send_command("SR0")
                            elif suhu_tabung <= 75.0 and not self.heater_is_on:
                                self.heater_is_on = True
                                self.send_command("SR1")
                        
                        self.distribute_data_to_screens(data)
                except:
                    pass

    @mainthread
    def distribute_data_to_screens(self, data):
        # Update UI di ScreenCalibration jika sedang dibuka
        cal_screen = self.root.get_screen('screen_Calibration')
        if self.root.current == 'screen_Calibration':
            cal_screen.update_ui(data)
        
        # Update UI di Screensmoketest jika sedang dibuka
        smoke_screen = self.root.get_screen('screen_smoke_test')
        if self.root.current == 'screen_smoke_test':
            smoke_screen.update_ui(data)

    def on_window_resize(self, window, width, height):
        Logger.info(f"Window size: {width}x{height}")
        self.set_dynamic_fonts((width, height))
        self.refresh_all_fonts()

    def refresh_all_fonts(self):
        if hasattr(self, 'root') and hasattr(self.root, 'screens'):
            for screen in self.root.screens:
                self.refresh_fonts(screen)

    def refresh_fonts(self, widget):
        from kivymd.uix.label import MDLabel
        if isinstance(widget, MDLabel):
            original_style = widget.font_style
            temp_style = "Body1" if original_style != "Body1" else "H6"
            widget.font_style = temp_style
            widget.font_style = original_style
        if hasattr(widget, 'children'):
            for child in widget.children:
                self.refresh_fonts(child)

    def set_dynamic_fonts(self, size):
        try:
            screen_size_x = Window.system_size[0]
            screen_size_y = Window.system_size[1]
        except AttributeError:
            screen_size_x = Window._get_system_size()[0]
            screen_size_y = Window._get_system_size()[1]
        font_size_l = np.array([64, 32, 30, 20, 16, 11, 10, 9, 8])
        scale = min(screen_size_x / 1920, screen_size_y / 1080)
        font_size = np.round(font_size_l * scale, 0)
        Logger.info(f"Font resized: {font_size_l} to {font_size}")
        self.theme_cls.font_styles["H1"] = [
            "Orbitron-Regular", font_size[0], False, 0.15]
        self.theme_cls.font_styles["H2"] = [
            "Orbitron-Regular", font_size[1], False, 0.15]
        self.theme_cls.font_styles["H4"] = [
            "Recharge", font_size[2], False, 0.15]
        self.theme_cls.font_styles["H5"] = [
            "Recharge", font_size[3], False, 0.15]
        self.theme_cls.font_styles["H6"] = [
            "Recharge", font_size[4], False, 0.15]
        self.theme_cls.font_styles["Subtitle1"] = [
            "Recharge", font_size[5], False, 0.15]
        self.theme_cls.font_styles["Body1"] = [
            "Recharge", font_size[6], False, 0.15]
        self.theme_cls.font_styles["Button"] = [
            "Recharge", font_size[7], False, 0.15]
        self.theme_cls.font_styles["Caption"] = [
            "Recharge", font_size[8], False, 0.15]       

        if hasattr(self, 'root'):
            self.refresh_fonts(self.root)

if __name__ == '__main__':
    DieselsmokemeterApp().run()

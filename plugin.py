# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import os, time, json, ssl
from urllib.request import urlopen, Request

# Componentes Enigma2
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigSelection, getConfigListEntry, ConfigSubsection, ConfigYesNo, ConfigInteger, configfile
from enigma import eServiceReference, eTimer

# Parche de seguridad para conexiones HTTPS
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# ================= BASE DE DATOS CIUDADES =================
LOCATIONS = {
    "Spain": sorted(["A Coruña", "Albacete", "Alcala de Henares", "Algeciras", "Alicante", "Almeria", "Avila", "Badajoz", "Badalona", "Barcelona", "Bilbao", "Burgos", "Caceres", "Cadiz", "Cartagena", "Castellon", "Ceuta", "Ciudad Real", "Cordoba", "Cuenca", "Dos Hermanas", "Elche", "Fuenlabrada", "Getafe", "Gijon", "Girona", "Granada", "Guadalajara", "Huelva", "Huesca", "Jaen", "Jerez de la Frontera", "L'Hospitalet", "Las Palmas", "Leganes", "Leon", "Lleida", "Logroño", "Lugo", "Madrid", "Malaga", "Marbella", "Melilla", "Móstoles", "Murcia", "Ourense", "Oviedo", "Palencia", "Palma de Mallorca", "Pamplona", "Pontevedra", "Sabadell", "Salamanca", "San Sebastian", "Santa Cruz de Tenerife", "Santander", "Santiago de Compostela", "Segovia", "Sevilla", "Soria", "Tarragona", "Terrassa", "Teruel", "Toledo", "Valencia", "Valladolid", "Vigo", "Vitoria", "Zamora", "Zaragoza"]),
    "Morocco": sorted(["Agadir", "Al Hoceima", "Azrou", "Beni Mellal", "Berkane", "Berrechid", "Casablanca", "Chefchaouen", "Dakhla", "El Jadida", "Errachidia", "Essaouira", "Fes", "Fnideq", "Guelmim", "Ifrane", "Kenitra", "Khemisset", "Khenifra", "Khouribga", "Ksar El Kebir", "Larache", "Marrakech", "Martil", "Meknes", "Mohammedia", "Nador", "Ouarzazate", "Oujda", "Rabat", "Safi", "Sale", "Settat", "Sidi Ifni", "Sidi Kacem", "Tangier", "Tan-Tan", "Taounate", "Taroudant", "Taza", "Tetouan", "Tiznit"]),
    "France": sorted(["Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes", "Strasbourg", "Montpellier", "Avignon", "Le Pontet"])
}

METHODS = [("12", "Francia (12°)"), ("3", "Mundo Musulman (18°)"), ("2", "ISNA (15°)"), ("8", "Marruecos (Habous)"), ("4", "Meca (Umm al-Qura)")]

SURAH_LIST = ["Al-Fatiha","Al-Baqarah","Al-Imran","An-Nisa","Al-Ma'idah","Al-An'am","Al-A'raf","Al-Anfal","At-Tawbah","Yunus","Hud","Yusuf","Ar-Ra'd","Ibrahim","Al-Hijr","An-Nahl","Al-Isra","Al-Kahf","Maryam","Taha","Al-Anbiya","Al-Hajj","Al-Mu'minun","An-Nur","Al-Furqan","Ash-Shu'ara","An-Naml","Al-Qasas","Al-Ankabut","Ar-Rum","Luqman","As-Sajda","Al-Ahzab","Saba","Fatir","Ya-Sin","As-Saffat","Sad","Az-Zumar","Ghafir","Fussilat","Ash-Shura","Az-Zukhruf","Ad-Dukhan","Al-Jathiya","Al-Ahqaf","Muhammad","Al-Fath","Al-Hujurat","Qaf","Adh-Dhariyat","At-Tur","An-Najm","Al-Qamar","Ar-Rahman","Al-Waqi'a","Al-Hadid","Al-Mujadila","Al-Hashr","Al-Mumtahina","As-Saff","Al-Jumu'a","Al-Munafiqun","At-Taghabun","At-Talaq","At-Tahrim","Al-Mulk","Al-Qalam","Al-Haqqa","Al-Ma'arij","Nuh","Al-Jinn","Al-Muzzammil","Al-Muddathir","Al-Qiyama","Al-Insan","Al-Mursalat","An-Naba","An-Nazi'at","Abasa","At-Takwir","Al-Infitar","Al-Mutaffifin","Al-Inshiqaq","Al-Buruj","At-Tariq","Al-A'la","Al-Ghashiya","Al-Fajr","Al-Balad","Ash-Shams","Al-Layl","Ad-Duha","Ash-Sharh","At-Tin","Al-Alaq","Al-Qadr","Al-Bayyina","Az-Zalzala","Al-Adiyat","Al-Qari'a","At-Takathur","Al-Asr","Al-Humaza","Al-Fil","Quraysh","Al-Ma'un","Al-Kawthar","Al-Kafirun","An-Nasr","Al-Masad","Al-Ikhlas","Al-Falaq","An-Nas"]

# GLOBAL DATA
DATA = {"prayers":{}, "hijri":""}
PLUGIN_PATH = os.path.dirname(__file__)
ATHAN_FILE = os.path.join(PLUGIN_PATH, "athan.wav")
BG_PATH = os.path.join(PLUGIN_PATH, "background.png")

# ================= CONFIGURACIÓN =================
config.plugins.zouathan = ConfigSubsection()
config.plugins.zouathan.country = ConfigSelection(choices=sorted(LOCATIONS.keys()), default="Spain")
config.plugins.zouathan.city = ConfigSelection(choices=LOCATIONS["Spain"], default="Madrid")
config.plugins.zouathan.method = ConfigSelection(choices=METHODS, default="12")
config.plugins.zouathan.offset = ConfigInteger(default=0, limits=(-60, 60))
config.plugins.zouathan.play_audio = ConfigYesNo(default=True)
config.plugins.zouathan.show_popup = ConfigYesNo(default=True)

def updateCityChoices():
    try:
        p_guardado = config.plugins.zouathan.country.value
        if p_guardado in LOCATIONS:
            config.plugins.zouathan.city.setChoices(LOCATIONS[p_guardado])
    except:
        pass

def fetch():
    try:
        city = config.plugins.zouathan.city.value.replace(" ", "%20")
        country = config.plugins.zouathan.country.value.replace(" ", "%20")
        method = config.plugins.zouathan.method.value
        off = config.plugins.zouathan.offset.value
        url = "https://api.aladhan.com/v1/timingsByAddress?address=%s,%s&method=%s&tune=0,0,0,%s,%s,%s,0,0" % (city, country, method, off, off, off)
        req = Request(url, headers={'User-Agent': 'Enigma2-ZouAthan'})
        res = json.loads(urlopen(req, timeout=10).read().decode())["data"]
        for k in ["Fajr","Dhuhr","Asr","Maghrib","Isha"]:
            DATA["prayers"][k] = res["timings"][k]
        DATA["hijri"] = "%s %s %s" % (res["date"]["hijri"]["day"], res["date"]["hijri"]["month"]["en"], res["date"]["hijri"]["year"])
    except: pass

# ================= MONITOR DE FONDO Y NOTIFICACIÓN =================
class AthanNotification(Screen):
    # skin para colocar el aviso arriba a la derecha (x=1180, y=50)
    skin = """
    <screen name="AthanNotification" position="1180,50" size="680,140" flags="wfNoBorder" backgroundColor="#101010">
        <widget name="message" position="15,15" size="650,110" font="Regular;24" foregroundColor="#FFFFFF" halign="center" valign="center" transparent="1" />
    </screen>"""

    def __init__(self, session, text, timeout=200):
        Screen.__init__(self, session)
        self.session = session
        self["message"] = Label(text)
        self["actions"] = ActionMap(["OkCancelActions"], {
            "ok": self.dismiss,
            "cancel": self.dismiss
        }, -1)
        
        self.closeTimer = eTimer()
        self.closeTimer.callback.append(self.dismiss)
        self.closeTimer.start(timeout * 1000, True)

    def dismiss(self):
        self.closeTimer.stop()
        self.close()

class AthanManager:
    def __init__(self, session):
        self.session = session
        self.last_athan_time = ""
        self.checkTimer = eTimer()
        self.checkTimer.callback.append(self.checkTime)
        self.checkTimer.start(30000, False)

    def checkTime(self):
        t = time.localtime()
        time_now = time.strftime("%H:%M", t)
        p = DATA.get("prayers", {})
        if p:
            for name, p_time in p.items():
                if time_now == p_time and self.last_athan_time != time_now:
                    self.last_athan_time = time_now
                    self.lanzar_aviso(name)

    def lanzar_aviso(self, prayer_name):
        # Lanza el audio en segundo plano
        if config.plugins.zouathan.play_audio.value and os.path.exists(ATHAN_FILE):
            os.system("aplay %s &" % ATHAN_FILE)
        
        # Muestra el cartel informativo arriba a la derecha
        if config.plugins.zouathan.show_popup.value or config.plugins.zouathan.play_audio.value:
            msg = "Es la hora de %s\nPresiona OK o EXIT para silenciar." % prayer_name
            self.session.openWithCallback(self.stopAthanAudio, AthanNotification, msg, timeout=200)

    def stopAthanAudio(self, answer=None):
        try:
            os.system("killall -9 aplay > /dev/null 2>&1")
        except:
            pass




# ================= PANTALLAS =================
class ZouSettings(ConfigListScreen, Screen):
    skin = """
    <screen name="ZouSettings" position="center,center" size="750,380" title="Ajustes ZouAthan">
        <widget name="config" position="20,20" size="710,260" scrollbarMode="showOnDemand" />
        <eLabel text="AZUL: Detectar ciudad | OK: Guardar | EXIT: Salir" position="20,320" size="710,30" font="Regular;22" halign="center" foregroundColor="#FACC2E" />
    </screen>"""
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        updateCityChoices()
        ConfigListScreen.__init__(self, self.list, session=session, on_change=self.changedConfig)
        self.createConfigList()
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions"], {"ok": self.save, "cancel": self.close, "blue": self.detectByIP}, -2)

    def createConfigList(self):
        self.list = [
            getConfigListEntry("País:", config.plugins.zouathan.country),
            getConfigListEntry("Ciudad:", config.plugins.zouathan.city),
            getConfigListEntry("Método (Grados):", config.plugins.zouathan.method),
            getConfigListEntry("Ajuste minutos (+/-):", config.plugins.zouathan.offset),
            getConfigListEntry("Activar SONIDO (Athan):", config.plugins.zouathan.play_audio),
            getConfigListEntry("Activar AVISO (Mensaje):", config.plugins.zouathan.show_popup),
        ]
        self["config"].l.setList(self.list)

    def changedConfig(self):
        cur = self["config"].getCurrent()
        if cur and cur[1] == config.plugins.zouathan.country:
            new_country = config.plugins.zouathan.country.value
            config.plugins.zouathan.city.setChoices(LOCATIONS.get(new_country, ["Madrid"]))
            self.createConfigList()

    def detectByIP(self):
        try:
            res = json.loads(urlopen("http://ip-api.com/json", timeout=5).read().decode())
            if res["status"] == "success":
                country, city = res["country"], res["city"]
                if country not in LOCATIONS:
                    LOCATIONS[country] = [city]
                    clist = config.plugins.zouathan.country.choices
                    clist.append(country)
                    config.plugins.zouathan.country.setChoices(sorted(clist))
                config.plugins.zouathan.country.value = country
                if city not in LOCATIONS.get(country, []):
                    LOCATIONS[country].append(city)
                    LOCATIONS[country].sort()
                config.plugins.zouathan.city.setChoices(LOCATIONS[country])
                config.plugins.zouathan.city.value = city
                config.plugins.zouathan.country.save()
                config.plugins.zouathan.city.save()
                configfile.save()
                self.createConfigList()
                self.session.open(MessageBox, "Detectado y Guardado:\n%s (%s)" % (city, country), MessageBox.TYPE_INFO, timeout=5)
        except: pass

    def save(self):
        for x in self["config"].list:
            x[1].save()
        configfile.save()
        fetch()
        self.close()

class SurahScreen(Screen):
    skin = """
    <screen name="SurahScreen" position="center,center" size="850,600" title="Noble Corán" backgroundColor="#101010">
        <widget name="list" position="20,20" size="810,430" font="Regular;28" itemHeight="50" scrollbarMode="showOnDemand" />
        <widget name="counter" position="20,460" size="810,40" font="Regular;32" foregroundColor="#FACC2E" halign="center" />
        <widget name="status" position="20,510" size="810,40" font="Regular;26" foregroundColor="#00FF7F" halign="center" />
    </screen>"""
    def __init__(self, session):
        Screen.__init__(self, session)
        list_data = [("%03d - %s" % (i+1, name), i+1) for i, name in enumerate(SURAH_LIST)]
        self["list"] = MenuList(list_data)
        self["status"] = Label("Seleccione y pulse OK")
        self["counter"] = Label("00:00:00")
        self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.playSelected, "cancel": self.exitSurah}, -1)
        self.elapsed_seconds = 0
        self.countTimer = eTimer()
        self.countTimer.callback.append(self.updateCounter)

    def playSelected(self):
        selection = self["list"].getCurrent()
        if selection:
            url = "https://server8.mp3quran.net/afs/%03d.mp3" % selection[1]
            self["status"].setText("Reproduciendo Sura %03d..." % selection[1])
            self.session.nav.playService(eServiceReference(4097, 0, url))
            self.elapsed_seconds = 0
            self.countTimer.start(1000, False)

    def updateCounter(self):
        self.elapsed_seconds += 1
        m, s = divmod(self.elapsed_seconds, 60)
        h, m = divmod(m, 60)
        self["counter"].setText("%02d:%02d:%02d" % (h, m, s))

    def exitSurah(self):
        self.countTimer.stop()
        self.close()

class ZouAthan(Screen):
    skin = """
    <screen name="ZouAthan" position="center,center" size="1200,600" title="ZouAthan Pro" flags="wfNoBorder" backgroundColor="transparent">
        <widget name="background_img" position="0,0" size="1200,600" zPosition="-1" scale="1" alphatest="on" />
        <widget name="clock" position="60,30" size="400,55" font="Regular;50" halign="left" transparent="1" />
        <widget name="date_hijri" position="60,100" size="400,35" font="Regular;28" foregroundColor="#FACC2E" halign="left" transparent="1" />
        <widget name="city_label" position="60,140" size="400,35" font="Regular;24" foregroundColor="#00FF7F" halign="left" transparent="1" />
        <eLabel text="FAJR" position="60,210" size="200,40" font="Regular;32" foregroundColor="#FACC2E" halign="center" transparent="1" />
        <widget name="Fajr" position="60,260" size="200,60" font="Regular;46" halign="center" transparent="1" />
        <eLabel text="DHUHR" position="285,210" size="200,40" font="Regular;32" foregroundColor="#FACC2E" halign="center" transparent="1" />
        <widget name="Dhuhr" position="285,260" size="200,60" font="Regular;46" halign="center" transparent="1" />
        <eLabel text="ASR" position="510,210" size="200,40" font="Regular;32" foregroundColor="#FACC2E" halign="center" transparent="1" />
        <widget name="Asr" position="510,260" size="200,60" font="Regular;46" halign="center" transparent="1" />
        <eLabel text="MAGHRIB" position="735,210" size="200,40" font="Regular;32" foregroundColor="#FACC2E" halign="center" transparent="1" />
        <widget name="Maghrib" position="735,260" size="200,60" font="Regular;46" halign="center" transparent="1" />
        <eLabel text="ISHA" position="960,210" size="200,40" font="Regular;32" foregroundColor="#FACC2E" halign="center" transparent="1" />
        <widget name="Isha" position="960,260" size="200,60" font="Regular;46" halign="center" transparent="1" />
        <widget name="hint" position="0,530" size="1200,50" font="Regular;28" foregroundColor="#00FF00" halign="center" transparent="1" />
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self["background_img"] = Pixmap()
        self["clock"] = Label(""); self["date_hijri"] = Label(""); self["city_label"] = Label("")
        self["hint"] = Label("OK: Corán | MENU: Ajustes | EXIT: Salir")
        for pray in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]: self[pray] = Label("--:--")
        self["actions"] = ActionMap(["OkCancelActions", "MenuActions"], {"ok": self.openSurah, "cancel": self.close, "menu": self.openSettings}, -1)
        self.timer = eTimer()
        self.timer.callback.append(self.update)
        self.timer.start(1000, False)
        self.onLayoutFinish.append(self.load_res)

    def load_res(self):
        if os.path.exists(BG_PATH):
            self["background_img"].instance.setPixmapFromFile(BG_PATH)
        updateCityChoices()
        fetch()

    def openSurah(self): self.session.open(SurahScreen)
    def openSettings(self): self.session.open(ZouSettings)
    def update(self):
        self["clock"].setText(time.strftime("%H:%M:%S"))
        self["date_hijri"].setText(DATA.get("hijri", ""))
        self["city_label"].setText(config.plugins.zouathan.city.value)
        p = DATA.get("prayers", {})
        for pray in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]: self[pray].setText(p.get(pray, "--:--"))

# ================= PLUGIN START =================
athan_monitor = None
def sessionstart(reason, **kwargs):
    global athan_monitor
    if reason == 0 and "session" in kwargs:
        updateCityChoices()
        fetch()
        athan_monitor = AthanManager(kwargs["session"])

def main(session, **kwargs): session.open(ZouAthan)

def Plugins(**kwargs):
    return [
        PluginDescriptor(name="ZouAthan", where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main, icon="plugin.png"),
        PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=sessionstart)
    ]

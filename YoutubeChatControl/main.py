import pytchat
import pyautogui
import os
import configparser
import tkinter as tk
from tkinter import scrolledtext, simpledialog, ttk
import threading
import queue
import webbrowser
import xml.etree.ElementTree as ET
import subprocess

ARANLIK_TEMA = "#2E2E2E"
AÇIK_TEMA = "#F0F0F0"
YAZI_RENGI = "#FFFFFF"
DUGME_RENGI = "#007BFF"
DUGME_RENGI_HOVER = "#0056b3"
LOG_RENGI = "#00FF00"

def dil_paketlerini_bul():
    dil_paketleri = []
    langs_klsr = 'langs'
    for dosya in os.listdir(langs_klsr):
        if dosya.endswith('.xml'):
            dil_paketleri.append(dosya[:-4])
    return dil_paketleri

def dil_yukle(dil_adi):
    dil_dosyasi = dil_adi + ".xml"
    dil_yolu = os.path.join('langs', dil_dosyasi)

    if not os.path.exists(dil_yolu):
        print(f"Dil dosyası bulunamadı: {dil_yolu}")
        return {}

    tree = ET.parse(dil_yolu)
    root = tree.getroot()

    dil_dict = {}
    for elem in root:
        dil_dict[elem.tag] = elem.text

    return dil_dict

def dil_secimi_kaydet(dil_adi, pencere):
    config = configparser.ConfigParser()
    config.read('settings.ini')
    config.set('Ayarlar', 'dil', dil_adi)

    with open('settings.ini', 'w') as configfile:
        config.write(configfile)

    global dil
    dil = dil_yukle(dil_adi)
    print(f"Dil değiştirildi: {dil_adi}")
    pencere.destroy()

def dil_secimi_penceresi():
    pencere = tk.Tk()
    pencere.title("Dil Seçimi")

    dil_paketleri = dil_paketlerini_bul()
    dil_combo = ttk.Combobox(pencere, values=dil_paketleri)
    dil_combo.set(config.get('Ayarlar', 'dil'))
    dil_combo.pack(padx=10, pady=10)

    dil_sec_btn = tk.Button(pencere, text="Dil Seç", command=lambda: dil_secimi_kaydet(dil_combo.get(), pencere))
    dil_sec_btn.pack(padx=10, pady=10)

    pencere.mainloop()

config = configparser.ConfigParser()
config.read('settings.ini')
mevcut_dil = config.get('Ayarlar', 'dil')
dil = dil_yukle(mevcut_dil)

def video_id_al():
    video_id = simpledialog.askstring("VIDEO ID", dil["video_id_mesaj"])
    return video_id

def yasakli_komutlar():
    config = configparser.ConfigParser()
    config.read('settings.ini')
    return config.get('Komutlar', 'yasakli_komutlar').split(',')

def komut_aktif_mi(komut):
    config = configparser.ConfigParser()
    config.read('settings.ini')
    return config.getboolean('Komutlar', komut)

def fareyi_hareket_ettir(yon, mesafe=10):
    mevcut_x, mevcut_y = pyautogui.position()
    if yon == dil["sag"]:
        pyautogui.moveTo(mevcut_x + mesafe, mevcut_y)
    elif yon == dil["sol"]:
        pyautogui.moveTo(mevcut_x - mesafe, mevcut_y)
    elif yon == dil["yukari"]:
        pyautogui.moveTo(mevcut_x, mevcut_y - mesafe)
    elif yon == dil["asagi"]:
        pyautogui.moveTo(mevcut_x, mevcut_y + mesafe)
    elif yon == dil["tikla"]:
        pyautogui.click()
    else:
        log_ekle(dil["gecersiz_komut"])

def tarayıcı_oku(url):
    try:
        webbrowser.open(url)
        print(f"URL açıldı: {url}")
    except Exception as e:
        print(f"URL açılırken hata oluştu: {e}")

def yazi_yaz(metin):
    pyautogui.write(metin)

def komut_izinli_mi(komut):
    for yasakli_komut in yasakli_komutlar():
        if yasakli_komut in komut:
            return False
    return True

def komut_isle(mesaj):
    print(f"Gelen mesaj: {mesaj}")
    parcalar = mesaj.split()
    print(f"Komut parçaları: {parcalar}")

    if parcalar[0] == "!mouse" and len(parcalar) >= 2 and komut_aktif_mi('fare'):
        yon = parcalar[1]
        mesafe = int(parcalar[2]) if len(parcalar) == 3 else 10
        print(f"Fare hareketi: {yon} {mesafe}")
        fareyi_hareket_ettir(yon, mesafe)
    elif parcalar[0] == "!cmd" and len(parcalar) >= 2 and komut_aktif_mi('cmd'):
        komut = ' '.join(parcalar[1:])
        print(f"Komut çalıştırma: {komut}")
        if komut_izinli_mi(komut):
            try:
                subprocess.Popen(['cmd', '/c', komut], creationflags=subprocess.CREATE_NEW_CONSOLE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            except Exception as e:
                print("Komut çalıştırılırken hata oluştu:", str(e))
    elif parcalar[0] == "!keyboard" and len(parcalar) >= 2 and komut_aktif_mi('klavye'):
        metin = ' '.join(parcalar[1:])
        print(f"Klavye yazısı: {metin}")
        yazi_yaz(metin)
    elif parcalar[0] == "!url" and len(parcalar) >= 2 and komut_aktif_mi('url'):
        url = parcalar[1]
        print(f"URL açma: {url}")
        tarayıcı_oku(url)
    else:
        print(dil["gecersiz_komut_format"])


def log_ekle(mesaj):
    log_alani.insert(tk.END, mesaj + "\n")
    log_alani.see(tk.END)
    log_alani.config(fg=LOG_RENGI)

def sohbeti_ayri_pencereye_goster():
    sohbet_pencere = tk.Toplevel()
    sohbet_pencere.title(dil["sohbet_pencere_baslik"])
    sohbet_pencere.attributes("-topmost", True)
    sohbet_pencere.config(bg=ARANLIK_TEMA)

    global sohbet_alani
    sohbet_alani = scrolledtext.ScrolledText(sohbet_pencere, wrap=tk.WORD, width=50, height=30, bg=ARANLIK_TEMA, fg=YAZI_RENGI)
    sohbet_alani.grid(column=0, row=0, padx=10, pady=10)

    return sohbet_pencere, sohbet_alani

def chat_dinle(queue, chat):
    while chat.is_alive():
        for c in chat.get().sync_items():
            mesaj = f"{c.author.name}: {c.message}"
            queue.put(mesaj)
            if c.message.startswith("!"):
                queue.put(dil["komut_alindi"].format(komut=c.message))
                komut_isle(c.message)

def queue_dinle(sohbet_alani, queue):
    while not queue.empty():
        mesaj = queue.get_nowait()
        sohbet_alani.insert(tk.END, mesaj + "\n")
        sohbet_alani.see(tk.END)
    sohbet_alani.after(100, queue_dinle, sohbet_alani, queue)

def sohbet_baslat():
    video_id = video_id_al()
    if not video_id:
        log_ekle(dil["video_id_yok"])
        return
    
    global chat
    chat = pytchat.create(video_id=video_id)
    q = queue.Queue()
    threading.Thread(target=chat_dinle, args=(q, chat), daemon=True).start()
    queue_dinle(sohbet_alani, q)
    log_ekle(dil["sohbet_basladi"])

def sohbet_durdur():
    global chat
    chat.terminate()
    log_ekle(dil["sohbet_dur"])

def kontrol_paneli():
    panel_pencere = tk.Toplevel()
    panel_pencere.title(dil["kontrol_panel_baslik"])
    panel_pencere.attributes("-topmost", True)
    panel_pencere.config(bg=ARANLIK_TEMA)

    baslik = tk.Label(panel_pencere, text="YoutubeChatControl", font=("Arial", 24), bg=ARANLIK_TEMA, fg=YAZI_RENGI)
    baslik.grid(column=0, row=0, padx=10, pady=10)

    baslat_buton = tk.Button(panel_pencere, text=dil["sohbeti_baslat"], command=sohbet_baslat, bg=DUGME_RENGI, fg=YAZI_RENGI)
    baslat_buton.grid(column=0, row=1, padx=10, pady=10)

    durdur_buton = tk.Button(panel_pencere, text=dil["sohbeti_durdur"], command=sohbet_durdur, bg=DUGME_RENGI, fg=YAZI_RENGI)
    durdur_buton.grid(column=0, row=2, padx=10, pady=10)

    dil_sec_buton = tk.Button(panel_pencere, text=dil["dil_sec"], command=dil_secimi_penceresi, bg=DUGME_RENGI, fg=YAZI_RENGI)
    dil_sec_buton.grid(column=0, row=3, padx=10, pady=10)

    global log_alani
    log_alani = scrolledtext.ScrolledText(panel_pencere, wrap=tk.WORD, width=50, height=15, bg=ARANLIK_TEMA, fg=YAZI_RENGI)
    log_alani.grid(column=0, row=4, padx=10, pady=10)

    global sohbet_alani
    sohbet_pencere, sohbet_alani = sohbeti_ayri_pencereye_goster()

    panel_pencere.mainloop()

kontrol_paneli()

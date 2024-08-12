import pytchat
import pyautogui
import os
import configparser
import tkinter as tk
from tkinter import scrolledtext, simpledialog
import threading
import queue
import webbrowser

# renkler
ARANLIK_TEMA = "#2E2E2E"
AÇIK_TEMA = "#F0F0F0"
YAZI_RENGI = "#FFFFFF"
DUGME_RENGI = "#007BFF"
DUGME_RENGI_HOVER = "#0056b3"
LOG_RENGI = "#00FF00"


def video_id_al():
    video_id = simpledialog.askstring("Video ID", "Lütfen video ID'nizi girin:")
    return video_id

global chat

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
    if yon == "sağ":
        pyautogui.moveTo(mevcut_x + mesafe, mevcut_y)
    elif yon == "sol":
        pyautogui.moveTo(mevcut_x - mesafe, mevcut_y)
    elif yon == "yukarı":
        pyautogui.moveTo(mevcut_x, mevcut_y - mesafe)
    elif yon == "aşağı":
        pyautogui.moveTo(mevcut_x, mevcut_y + mesafe)
    elif yon == "tıkla":
        pyautogui.click()
    else:
        log_ekle("Geçersiz yön! Yönler: sağ, sol, yukarı, aşağı, tıkla")

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
    parcalar = mesaj.split()
    if parcalar[0] == "!fare" and len(parcalar) >= 2 and komut_aktif_mi('fare'):
        yon = parcalar[1]
        mesafe = int(parcalar[2]) if len(parcalar) == 3 else 10
        fareyi_hareket_ettir(yon, mesafe)
    elif parcalar[0] == "!cmd" and len(parcalar) >= 2 and komut_aktif_mi('cmd'):
        komut = ' '.join(parcalar[1:])
        if komut_izinli_mi(komut):
            try:
                os.system(komut)
            except Exception as e:
                print("Komut çalıştırılırken hata oluştu:", str(e))
    elif parcalar[0] == "!klavye" and len(parcalar) >= 2 and komut_aktif_mi('klavye'):
        metin = ' '.join(parcalar[1:])
        yazi_yaz(metin)
    elif parcalar[0] == "!url" and len(parcalar) >= 2 and komut_aktif_mi('url'):
        url = parcalar[1]
        tarayıcı_oku(url)
    else:
        print("Geçersiz komut formatı veya tanınmayan komut.")

def log_ekle(mesaj):
    log_alani.insert(tk.END, mesaj + "\n")
    log_alani.see(tk.END)
    log_alani.config(fg=LOG_RENGI)

def sohbeti_ayri_pencereye_goster():
    sohbet_pencere = tk.Toplevel()
    sohbet_pencere.title("YouTube Sohbeti")
    sohbet_pencere.attributes("-topmost", True)
    sohbet_pencere.config(bg=ARANLIK_TEMA)

    sohbet_alani = scrolledtext.ScrolledText(sohbet_pencere, wrap=tk.WORD, width=50, height=30, bg=ARANLIK_TEMA, fg=YAZI_RENGI)
    sohbet_alani.grid(column=0, row=0, padx=10, pady=10)
    
    return sohbet_pencere, sohbet_alani

def chat_dinle(queue, chat):
    while chat.is_alive():
        for c in chat.get().sync_items():
            mesaj = f"{c.author.name}: {c.message}"
            queue.put(mesaj)
            if c.message.startswith("!"):
                queue.put(f"Komut alındı: {c.message}")
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
        log_ekle("Video ID girilmedi. Sohbet başlatılamadı.")
        return
    
    chat = pytchat.create(video_id=video_id)
    q = queue.Queue()
    threading.Thread(target=chat_dinle, args=(q, chat), daemon=True).start()
    queue_dinle(sohbet_alani, q)
    log_ekle("Sohbet dinlemeye başlandı.")

def sohbet_durdur():
    chat.terminate()
    log_ekle("Sohbet dinlemeyi durduruldu.")

def kontrol_paneli():
    panel_pencere = tk.Toplevel()
    panel_pencere.title("Kontrol Paneli")
    panel_pencere.attributes("-topmost", True)
    panel_pencere.config(bg=ARANLIK_TEMA)

    baslik = tk.Label(panel_pencere, text="YoutubeChatControl", font=("Arial", 24), bg=ARANLIK_TEMA, fg=YAZI_RENGI)
    baslik.grid(column=0, row=0, padx=10, pady=10)

    baslat_buton = tk.Button(panel_pencere, text="Sohbeti Başlat", command=sohbet_baslat, bg=DUGME_RENGI, fg=YAZI_RENGI)
    baslat_buton.grid(column=0, row=1, padx=10, pady=10)
    baslat_buton.bind("<Enter>", lambda e: baslat_buton.config(bg=DUGME_RENGI_HOVER))
    baslat_buton.bind("<Leave>", lambda e: baslat_buton.config(bg=DUGME_RENGI))

    durdur_buton = tk.Button(panel_pencere, text="Sohbeti Durdur", command=sohbet_durdur, bg=DUGME_RENGI, fg=YAZI_RENGI)
    durdur_buton.grid(column=0, row=2, padx=10, pady=10)
    durdur_buton.bind("<Enter>", lambda e: durdur_buton.config(bg=DUGME_RENGI_HOVER))
    durdur_buton.bind("<Leave>", lambda e: durdur_buton.config(bg=DUGME_RENGI))

    sparrow_yazi = tk.Label(panel_pencere, text="made by Sparrow", fg="blue", cursor="hand2", bg=ARANLIK_TEMA)
    sparrow_yazi.grid(column=0, row=3, padx=10, pady=10)
    sparrow_yazi.bind("<Button-1>", lambda e: webbrowser.open_new("https://www.youtube.com/channel/UCoxY4EKZIQQvqA477nBHyMA"))

    return panel_pencere

def gui_baslat():
    pencere = tk.Tk()
    pencere.title("YouTube Chat Komut Yöneticisi")
    pencere.attributes("-topmost", True)
    pencere.config(bg=ARANLIK_TEMA)

    global log_alani
    log_alani = scrolledtext.ScrolledText(pencere, wrap=tk.WORD, width=50, height=30, bg=ARANLIK_TEMA, fg=YAZI_RENGI)
    log_alani.grid(column=0, row=0, padx=10, pady=10, sticky='nsew')

    global sohbet_pencere, sohbet_alani
    sohbet_pencere, sohbet_alani = sohbeti_ayri_pencereye_goster()

    kontrol_paneli()

    pencere.mainloop()
    sohbet_pencere.mainloop()

if __name__ == "__main__":
    gui_baslat()

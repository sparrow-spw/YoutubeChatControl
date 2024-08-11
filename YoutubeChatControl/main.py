import pytchat
import pyautogui
import subprocess
import os
import configparser

def ayarlardan_video_id_al():
    config = configparser.ConfigParser()
    config.read('settings.ini')
    return config.get('YouTube', 'video_id')

chat = pytchat.create(video_id=ayarlardan_video_id_al())

def yasakli_komutlar():
    config = configparser.ConfigParser()
    config.read('settings.ini')
    return config.get('Komutlar', 'yasakli_komutlar').split(',')

def komut_aktif_mi(komut):
    config = configparser.ConfigParser()
    config.read('settings.ini')
    return config.getboolean('Komutlar', komut)

def komut_calistir(komut):
    try:
        sonuc = subprocess.run(komut, shell=True, capture_output=True, text=True)
        print(f"Komut Çıktısı: {sonuc.stdout}")
        if sonuc.stderr:
            print(f"Hata: {sonuc.stderr}")
    except Exception as e:
        print(f"Komut çalıştırma hatası: {e}")

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
        print("Geçersiz yön! Yönler: sağ, sol, yukarı, aşağı, tıkla")

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
                if os.name == 'nt':
                    tam_komut = f'{komut} & timeout /t 5'
                    subprocess.Popen(['cmd', '/c', tam_komut], creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:  # linux için
                    tam_komut = f'{komut}; sleep 5'
                    subprocess.Popen(['xterm', '-e', tam_komut])
            except Exception as e:
                print("Komut çalıştırılırken hata oluştu:", str(e))
        else:
            print("Bu komut yasaklı komutlar listesine dahil.")
    elif parcalar[0] == "!klavye" and len(parcalar) >= 2 and komut_aktif_mi('klavye'):
        metin = ' '.join(parcalar[1:])
        yazi_yaz(metin)
    else:
        print("Geçersiz komut formatı veya tanınmayan komut.")

while chat.is_alive():
    for c in chat.get().sync_items():
        if c.message.startswith("!"):
            komut_isle(c.message)

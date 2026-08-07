from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Lidya Akıllı Ev API", version="1.0")

# Evdeki cihazların anlık durumunu tutan basit bir veritabanı (sözlük)
ev_cihazlari = {
    "salon_lambasi": {"durum": "kapali", yuzde: 0},
    "klima": {"durum": "kapali", "sicaklik": 22},
    "muzik_calar": {"durum": "kapali", "sarki": "Yok"}
}

class CihazIstegi(BaseModel.lower: str = None) # İsteğe bağlı parametreler için
    cihaz_adi: str
    islem: str  # "ac", "kapat", "ayarla"
    deger: int = None  # Sıcaklık veya parlaklık için

@app.get("/")
def ana_sayfa():
    return {"mesaj": "Lidya Akıllı Ev Sistemleri Aktif! 🏠✨"}

@app.get("/durum")
def cihazlari_getir():
    return ev_cihazlari

@app.post("/kontrol")
def cihazı_kontrol_et(istek: CihazIstegi):
    c_adi = istek.cihaz_adi.lower()
    islem = istek.islem.lower()
    
    if c_adi not in ev_cihazlari:
        return {"hata": f"{c_adi} adında bir cihaz bulunamadı!"}
    
    if islem == "ac":
        ev_cihazlari[c_adi]["durum"] = "acik"
        mesaj = f"{c_adi} başarıyla açıldı! 💡"
    elif islem == "kapat":
        ev_cihazlari[c_adi]["durum"] = "kapali"
        mesaj = f"{c_adi} kapatıldı. 🌙"
    elif islem == "ayarla" and istek.degisiklik is not None:
        ev_cihazlari[c_adi]["durum"] = "acik"
        # Eğer klima ise sıcaklık, lamba ise parlaklık ayarla
        if "sicaklik" in ev_cihazlari[c_adi]:
            ev_cihazlari[c_adi]["sicaklik"] = istek.deger
            mesaj = f"{c_adi} sıcaklığı {istek.deger}°C olarak ayarlandı. 🌡️"
        else:
            mesaj = f"{c_adi} güncellendi."
    else:
        return {"hata": "Geçersiz işlem!"}
        
    return {"durum": "basarili", "mesaj": mesaj, "guncel_veri": ev_cihazlari[c_adi]}

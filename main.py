from fastapi import FastAPI, Depends
from pydantic import BaseModel
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sqlalchemy.orm import Session
import database

# Veritabanı Tablolarını Oluştur
database.veritabani_olustur()

app = FastAPI(
    title="Lidya ML API",
    description="Lidya için Duygu Analizi ve Veritabanı Servisi",
    version="2.0"
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

data = {
    'cumle': [
        'Bu uygulama harika çalışıyor',
        'Çok başarılı bir proje tebrik ederim',
        'Arayüz mükemmel ve çok hızlı',
        'Hiç beğenmedim sürekli hata veriyor',
        'Çok kötü bir deneyimdi hiç çalışmıyor',
        'Tam bir zaman kaybı berbat'
    ],
    'etiket': ['pozitif', 'pozitif', 'pozitif', 'negatif', 'negatif', 'negatif']
}

df = pd.DataFrame(data)
vectorizer = CountVectorizer(ngram_range=(1, 2))
X = vectorizer.fit_transform(df['cumle'])
y = df['etiket']

model = MultinomialNB()
model.fit(X, y)

class MetinIstegi(BaseModel):
    metin: str

@app.get("/")
def ana_sayfa():
    return {"mesaj": "Lidya ML & DB Servisi Çalışıyor!"}

@app.post("/tahmin")
def duygu_analizi_yap(istek: MetinIstegi, db: Session = Depends(get_db)):
    metin_sayisal = vectorizer.transform([istek.metin])
    tahmin = model.predict(metin_sayisal)[0].upper()
    
    yeni_kayit = database.AnalizKaydi(metin=istek.metin, tahmin=tahmin)
    db.add(yeni_kayit)
    db.commit()
    db.refresh(yeni_kayit)
    
    return {
        "id": yeni_kayit.id,
        "girilen_metin": istek.metin,
        "duygu_tahmini": tahmin,
        "tarih": yeni_kayit.tarih
    }

@app.get("/gecmis")
def gecmis_analizleri_getir(db: Session = Depends(get_db)):
    kayitlar = db.query(database.AnalizKaydi).order_by(database.AnalizKaydi.id.desc()).all()
    return kayitlar
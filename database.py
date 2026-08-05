from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# SQLite veritabanı dosyası oluşturuluyor
SQLALCHEMY_DATABASE_URL = "sqlite:///./lidya_ml.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Veritabanı Tablo Modeli
class AnalizKaydi(Base):
    __tablename__ = "analizler"

    id = Column(Integer, primary_key=True, index=True)
    metin = Column(String, index=True)
    tahmin = Column(String)
    tarih = Column(DateTime, default=datetime.datetime.utcnow)

# Tabloları oluşturma fonksiyonu
def veritabani_olustur():
    Base.metadata.create_all(bind=engine)
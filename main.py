from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class MetinModeli(BaseModel):
    metin: str

@app.post("/tahmin")
def duygu_tahmini(veri: MetinModeli):
    # Şimdilik test amaçlı her metne POZITIF diyoruz
    # Daha sonra buraya kendi eğittiğin ML modelini bağlayabilirsin
    return {"duygu_tahmini": "POZITIF"}
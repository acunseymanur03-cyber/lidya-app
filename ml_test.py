import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# 1. VERİ SETİ (Modeli eğitmek için küçük bir veri kümesi oluşturuyoruz)
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

# 2. METİNLERİ SAYILARA DÖNÜŞTÜRME (Yapay zeka kelimeleri değil, sayıları anlar)
vectorizer = CountVectorizer(ngram_range=(1, 2))
X = vectorizer.fit_transform(df['cumle'])  # Cümleleri sayısal matrise çevirir
y = df['etiket']                          # Hedef etiketlerimiz (Pozitif/Negatif)

# 3. MODELİ OLUŞTURMA VE EĞİTME (Naive Bayes Algoritması)
model = MultinomialNB()
model.fit(X, y)

# 4. YENİ BİR CÜMLE İLE TEST ETME
yeni_cumle = ["Proje berbat değil, çok harika"]
yeni_cumle_sayisal = vectorizer.transform(yeni_cumle)

# Tahmin yap
tahmin = model.predict(yeni_cumle_sayisal)

print(f"\nCümle: '{yeni_cumle[0]}'")
print(f"Modelin Tahmini: {tahmin[0].upper()}\n")
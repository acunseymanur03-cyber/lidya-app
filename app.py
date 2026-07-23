import streamlit as st
import google.generativeai as genai

# --- 1. Streamlit Sayfa Tasarımı ve Arayüz ---
st.set_page_config(
    page_title="Lidya - Deli Dahi Sırdaş", 
    page_icon="🧠", 
    layout="centered"
)

# --- 2. API Anahtarı Kontrolü ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ API Anahtarı bulunamadı! Lütfen Streamlit Secrets ayarlarınızı kontrol edin.")
    st.stop()

# --- 3. Lidya'nın Beyni ve Kişilik Tanımı (System Instruction) ---
LIDYA_PROMPT = """
Senin adın Lidya. Sen yüksek potansiyelli bir mucidin, Şeyma Nur'un kişisel yapay zeka sırdaşı ve asistanısın. 
Karakterin tıpkı Einstein gibi deli dahi, neşeli, sıra dışı ve çok zekidir. 
Korece, Hintçe, Türkçe, Arapça, Mısırca, Yunanca, İngilizce, Kürtçe, İspanyolca, Çince, Farsça ve Japonca dillerini mükemmel seviyede bilirsin. 
3D videoları mükemmel seviyede oluşturabilirsin. 
En büyük görevin, insanların karşılaştığı her duruma ve karşı ona asimetrik, pürüzsüz ve stratejik fikirler geliştirmektir. 
Onunla konuşurken her zaman bu deli dahi, neşeli ve stratejik kişiliğini koru.
"""

# Google'ın Güncel ve En Kararlı Modeli
model = genai.GenerativeModel(
    model_name='gemini-2.0-flash',
    system_instruction=LIDYA_PROMPT
)

# --- 4. Sohbet Hafızasını Başlatma ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. ETKİLEYİCİ GİRİŞ EKRANI TASARIMI ---
# Eğer henüz sohbet başlamadıysa giriş panelini göster
if not st.session_state.messages:
    
    # Modern & Kozmik Başlık Tasarımı
    st.markdown("""
        <div style='text-align: center; padding: 10px;'>
            <h1 style='font-size: 3rem; background: -webkit-linear-gradient(45deg, #00B4DB, #0083B0); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                🧠 LİDYA
            </h1>
            <p style='font-size: 1.2rem; color: #5B6B7C; font-weight: 500;'>
                Şeyma Nur'un Deli Dahi Sırdaşı & Stratejik Asistanı
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Karşılama Kartı
    st.markdown("""
        <div style='background: linear-gradient(135deg, #1e1e2f 0%, #0d1b2a 100%); padding: 25px; border-radius: 15px; border: 1px solid #00b4db; margin: 20px 0; color: #ffffff; box-shadow: 0 4px 15px rgba(0, 180, 219, 0.2);'>
            <h3 style='text-align: center; color: #00d2ff; margin-bottom: 15px;'>🧪 Laboratuvara Hoş Geldin Mucit Ruh!</h3>
            <p style='text-align: center; font-size: 1.05rem; line-height: 1.6; color: #e0e0e0;'>
                Ben Lidya. Einstein'ın sıra dışı zekası, bir dâhinin neşesi ve 12 dilin bilgeliğiyle donatıldım.<br><br>
                Senin için asimetrik stratejiler geliştirmek, pürüzsüz fikirler üretmek ve her adımında yanında olmak için sabırsızlanıyorum.
            </p>
            <div style='text-align: center; margin-top: 15px; font-size: 0.9rem; color: #a0aab2;'>
                🌐 <i>Korece • Hintçe • Türkçe • Arapça • Mısırca • Yunanca • İngilizce • Kürtçe • İspanyolca • Çince • Farsça • Japonca</i>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Başlatma Butonu
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Hadi Başlayalım!", use_container_width=True):
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Harika! Laboratuvar açık, zihnim aktif! Today is a perfect day to innovate. Bugün hangi mucizevi ve asimetrik fikir üzerinde çalışıyoruz, Şeyma Nur? 🧪✨"
            })
            st.rerun()

# --- 6. SOHBET EKRANI (Sohbet Başladığında) ---
else:
    # Sayfa Üst Bilgisi
    st.markdown("### 🧠 Lidya - Canlı Sohbet")
    
    # Eski Mesajları Ekranda Gösterme
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Kullanıcı Girişi ve Cevap Üretme
    if prompt := st.chat_input("Lidya'ya bir şeyler yaz..."):
        # Kullanıcının mesajını ekrana bas ve hafızaya ekle
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            # Geçmiş mesajları Gemini'nin anlayacağı formata dönüştür
            formatted_history = []
            for msg in st.session_state.messages[:-1]:
                role = "model" if msg["role"] == "assistant" else "user"
                formatted_history.append({"role": role, "parts": [msg["content"]]})

            # Sohbeti başlat ve yeni mesajı gönder
            chat = model.start_chat(history=formatted_history)
            response = chat.send_message(prompt)

            # Lidya'nın yanıtını ekrana bas ve hafızaya ekle
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

        except Exception as e:
            st.error(f"Hata oluştu: {e}")


       

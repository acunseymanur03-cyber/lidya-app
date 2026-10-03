import streamlit as st
import os
from groq import Groq
from gtts import gTTS

# Sayfa Ayarları
st.set_page_config(page_title="Lidya - Akıllı Ev Asistanı", page_icon="🧠", layout="centered")

# CSS Stilleri
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stTextInput > div > div > input {
        background-color: #262730;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Oturum Durumu Başlangıcı
if "user_name" not in st.session_state:
    st.session_state.user_name = "Şeymanur"

if "language" not in st.session_state:
    st.session_state.language = "Türkçe"

if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "sohbet_1"

if st.session_state.current_chat_id not in st.session_state.all_chats:
    st.session_state.all_chats[st.session_state.current_chat_id] = []

# --- KENAR ÇUBUĞU (SİDEBAR) ---
with st.sidebar:
    st.markdown("### ⚙️ Ayarlar & Yönetim")
    
    # İsim Değiştirme
    yeni_isim = st.text_input("Adını Değiştir:", value=st.session_state.user_name)
    if yeni_isim != st.session_state.user_name:
        st.session_state.user_name = yeni_isim
        st.rerun()

    # Dil Seçimi
    secilen_dil = st.selectbox("Dil Seçimi / Language:", ["Türkçe", "English"], index=0 if st.session_state.language == "Türkçe" else 1)
    if secilen_dil != st.session_state.language:
        st.session_state.language = secilen_dil
        st.rerun()

    st.write("---")
    
    # Model Seçimi (Klavye hatası olmasın diye menüye aldık!)
    model_secimi = st.selectbox("Yapay Zeka Modeli:", ["llama-3.1-8b-instant", "llama3-8b-8192"])

    st.write("---")

    # Yeni Sohbet Oluştur
    if st.button("➕ Yeni Sohbet Oluştur"):
        yeni_id = f"sohbet_{len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[yeni_id] = []
        st.session_state.current_chat_id = yeni_id
        st.rerun()

    # Sohbeti Sil
    if st.button("🗑️ Aktif Sohbeti Temizle"):
        st.session_state.all_chats[st.session_state.current_chat_id] = []
        st.rerun()

# Ana Başlık
st.markdown("### 🧠 Lidya - Akıllı Ev Asistanı")
st.markdown(f"Hoş geldin {st.session_state.user_name}! Evdeki cihazları yönetmek için buradayım. 🏠💡")

# Groq API Anahtarı Kontrolü
api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
if not api_key:
    st.error("⚠️ GROQ_API_KEY anahtarı bulunamadı! Lütfen Streamlit Secrets ayarlarına ekleyin.")
    st.stop()

client = Groq(api_key=api_key)

system_prompt = f"""
Senin adın Lidya. Enerjik, akıllı ev sistemlerini yönetebilen bilim odaklı bir yapay zekasın.
Şu an sohbet ettiğin kullanıcının adı: {st.session_state.user_name}.
Kullanıcıya kesinlikle kendi adıyla ({st.session_state.user_name}) hitap et. Kısa, net ve samimi ol.
Konuşma dili: {st.session_state.language}.
Eğer kullanıcı evdeki bir cihazı (salon lambası, klima, müzik çalar vb.) açmak veya kapatmak isterse yardımcı ol.
"""

current_messages = st.session_state.all_chats[st.session_state.current_chat_id]

# Geçmiş mesajları ekrana yazdır
for i, msg in enumerate(current_messages):
    avatar = "🧠" if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

    # Asistan mesajlarının altına ses oynatıcı ekle
    if msg["role"] == "assistant":
        try:
            dil_kodu = "tr" if st.session_state.language == "Türkçe" else "en"
            tts = gTTS(text=msg["content"], lang=dil_kodu, slow=False)
            audio_file = f"temp_audio_{i}.mp3"
            tts.save(audio_file)
            with open(audio_file, "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3")
        except Exception:
            pass

# C. MESAJ GİRİŞİ
st.write("---")
prompt = st.chat_input(f"Mesajını buraya yaz, {st.session_state.user_name}...")

if prompt:
    current_messages.append({"role": "user", "content": prompt})

    formatted_messages = [{"role": "system", "content": system_prompt}]
    for m in current_messages:
        formatted_messages.append({"role": m["role"], "content": m["content"]})

    try:
        with st.spinner("Lidya düşünüyor ve evi kontrol ediyor... 🧪"):
            response = client.chat.completions.create(
                model=model_secimi,
                messages=formatted_messages,
            )

        bot_reply = response.choices[0].message.content

        current_messages.append({"role": "assistant", "content": bot_reply})
        st.session_state.all_chats[st.session_state.current_chat_id] = current_messages
        st.rerun()

    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")

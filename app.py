import streamlit as st
import os
from groq import Groq
from gtts import gTTS

# Sayfa Ayarları
st.set_page_config(page_title="Lidya - AI Assistant", page_icon="🧠", layout="centered")

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

# Çoklu Dil Sözlüğü
translations = {
    "Türkçe": {
        "sidebar_title": "⚙️ Ayarlar & Yönetim",
        "name_label": "Adını Değiştir:",
        "lang_label": "Dil Seçimi / Language:",
        "new_chat": "➕ Yeni Sohbet Oluştur",
        "clear_chat": "🗑 Geçmişi Temizle",
        "title": "🧠 Lidya - Yapay Zeka Asistanı",
        "welcome": f"Hoş geldin {{user_name}}! Seninle sohbet etmek için buradayım. 🧠✨",
        "placeholder": f"Mesajını buraya yaz, {{user_name}}...",
        "spinner": "Lidya düşünüyor... 🧪",
        "error": "Bir hata oluştu: "
    },
    "English": {
        "sidebar_title": "⚙ Settings & Management",
        "name_label": "Change Name:",
        "lang_label": "Language / Dil Seçimi:",
        "new_chat": "➕ New Chat",
        "clear_chat": "🗑️ Clear Chat",
        "title": "🧠 Lidya - AI Assistant",
        "welcome": f"Welcome {{user_name}}! I'm here to chat with you. 🧠✨",
        "placeholder": f"Type your message here, {{user_name}}...",
        "spinner": "Lidya is thinking... 🧪",
        "error": "An error occurred: "
    },
    "Deutsch": {
        "sidebar_title": "⚙️ Einstellungen & Verwaltung",
        "name_label": "Name ändern:",
        "lang_label": "Sprache / Language:",
        "new_chat": "➕ Neuer Chat",
        "clear_chat": "🗑 Chat leeren",
        "title": "🧠 Lidya - KI-Assistent",
        "welcome": f"Willkommen {{user_name}}! Ich bin hier, um mit dir zu chatten. 🧠✨",
        "placeholder": f"Schreibe deine Nachricht hier, {{user_name}}...",
        "spinner": "Lidya denkt nach... 🧪",
        "error": "Ein Fehler ist aufgetreten: "
    },
    "Français": {
        "sidebar_title": "⚙ Paramètres & Gestion",
        "name_label": "Changer le nom :",
        "lang_label": "Langue / Language:",
        "new_chat": "➕ Nouvelle discussion",
        "clear_chat": "🗑️ Effacer la discussion",
        "title": "🧠 Lidya - Assistant IA",
        "welcome": f"Bienvenue {{user_name}} ! Je suis là pour discuter avec vous. 🧠✨",
        "placeholder": f"Tapez votre message ici, {{user_name}}...",
        "spinner": "Lidya réfléchit... 🧪",
        "error": "Une erreur s'est produite : "
    }
}

t = translations[st.session_state.language]

# --- KENAR ÇUBUĞU (SİDEBAR) ---
with st.sidebar:
    st.markdown(f"### {t['sidebar_title']}")
    
    # İsim Değiştirme
    yeni_isim = st.text_input(t["name_label"], value=st.session_state.user_name)
    if yeni_isim != st.session_state.user_name:
        st.session_state.user_name = yeni_isim
        st.rerun()

    # Dil Seçimi
    secilen_dil = st.selectbox(t["lang_label"], list(translations.keys()), index=list(translations.keys()).index(st.session_state.language))
    if secilen_dil != st.session_state.language:
        st.session_state.language = secilen_dil
        st.rerun()

    st.write("---")

    # Yeni Sohbet Oluştur
    if st.button(t["new_chat"]):
        yeni_id = f"sohbet_{len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[yeni_id] = []
        st.session_state.current_chat_id = yeni_id
        st.rerun()

    # Sohbeti Temizle
    if st.button(t["clear_chat"]):
        st.session_state.all_chats[st.session_state.current_chat_id] = []
        st.rerun()

# Ana Başlık ve Karşılama
st.markdown(f"### {t['title']}")
st.markdown(t["welcome"].format(user_name=st.session_state.user_name))

# Groq API Anahtarı Kontrolü
api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
if not api_key:
    st.error("⚠️ GROQ_API_KEY bulunamadı! Lütfen Streamlit Secrets ayarlarına ekleyin.")
    st.stop()

client = Groq(api_key=api_key)

# Kesin ve net sohbet modeli
aktif_model = "llama-3.1-8b-instant"

system_prompt = f"""
Senin adın Lidya. Enerjik, bilim odaklı ve akıllı bir yapay zekasın.
Şu an sohbet ettiğin kullanıcının adı: {st.session_state.user_name}.
Kullanıcıya kesinlikle kendi adıyla ({st.session_state.user_name}) hitap et. Kısa, net, samimi ve yardımcı ol.
Konuşma/yanıt dili: {st.session_state.language}. Kullanıcı hangi dilde konuşuyorsa veya arayüzde hangi dil seçiliyse o dilde yanıt ver.
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
            lang_map = {"Türkçe": "tr", "English": "en", "Deutsch": "de", "Français": "fr"}
            dil_kodu = lang_map.get(st.session_state.language, "tr")
            tts = gTTS(text=msg["content"], lang=dil_kodu, slow=False)
            audio_file = f"temp_audio_{i}.mp3"
            tts.save(audio_file)
            with open(audio_file, "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3")
        except Exception:
            pass

# Mesaj Girişi
st.write("---")
prompt = st.chat_input(t["placeholder"].format(user_name=st.session_state.user_name))

if prompt:
    current_messages.append({"role": "user", "content": prompt})

    formatted_messages = [{"role": "system", "content": system_prompt}]
    for m in current_messages:
        formatted_messages.append({"role": m["role"], "content": m["content"]})

    try:
        with st.spinner(t["spinner"]):
            response = client.chat.completions.create(
                model=aktif_model,
                messages=formatted_messages,
            )

        bot_reply = response.choices[0].message.content

        current_messages.append({"role": "assistant", "content": bot_reply})
        st.session_state.all_chats[st.session_state.current_chat_id] = current_messages
        st.rerun()

    except Exception as e:
        st.error(f"{t['error']}{e}")

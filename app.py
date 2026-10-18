import streamlit as st
import os
from groq import Groq

st.set_page_config(page_title="Lidya - AI Assistant", page_icon="🧠", layout="centered")

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
translations = {
    "Türkçe": {
        "sidebar_title": "⚙️ Ayarlar & Yönetim",
        "name_label": "Adını Değiştir:",
        "lang_label": "Dil Seçimi / Language:",
        "new_chat": "➕ Yeni Sohbet Oluştur",
        "clear_chat": "🗑 Geçmişi Temizle",
        "title": "🧠 Lidya - Yapay Zeka Asistanı",
        "welcome": "Hoş geldin Şeymanur! Seninle sohbet etmek için buradayım. 🧠✨",
        "placeholder": "Mesajını buraya yaz, Şeymanur...",
        "spinner": "Lidya düşünüyor... 🧪",
        "error": "Bir hata oluştu: "
    }
}

t = translations[st.session_state.language]

with st.sidebar:
    st.markdown(f"### {t['sidebar_title']}")
    yeni_isim = st.text_input(t["name_label"], value=st.session_state.user_name)
    if yeni_isim != st.session_state.user_name:
        st.session_state.user_name = yeni_isim
        st.rerun()
    st.write("---")
    if st.button(t["new_chat"]):
        yeni_id = f"sohbet_{len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[yeni_id] = []
        st.session_state.current_chat_id = yeni_id
        st.rerun()
    if st.button(t["clear_chat"]):
        st.session_state.all_chats[st.session_state.current_chat_id] = []
        st.rerun()

st.markdown(f"### {t['title']}")
st.markdown(t["welcome"])

api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
if not api_key:
    st.error("⚠️ GROQ_API_KEY bulunamadı!")
    st.stop()

client = Groq(api_key=api_key)
m_ad = "llama-3.1-8b-instant"

system_instruction = "Senin adın Lidya. Kullanıcının adı: Şeymanur. Kısa, samimi ve Türkçe yanıt ver."

current_messages = st.session_state.all_chats[st.session_state.current_chat_id]

for msg in current_messages:
    avatar = "🧠" if msg["role"] == "assistant" else None
    with st.chat_message("user" if msg["role"] == "user" else "assistant", avatar=avatar):
        st.markdown(msg["content"])

st.write("---")
prompt = st.chat_input(t["placeholder"])

if prompt:
    current_messages.append({"role": "user", "content": prompt})
    try:
        with st.spinner(t["spinner"]):
            messages = [{"role": "system", "content": system_instruction}]
            for m in current_messages:
                messages.append({"role": m["role"], "content": m["content"]})
            chat_completion = client.chat.completions.create(model=m_ad, messages=messages)
            bot_reply = chat_completion.choices[0].message.content
        current_messages.append({"role": "assistant", "content": bot_reply})
        st.session_state.all_chats[st.session_state.current_chat_id] = current_messages
        st.rerun()
    except Exception as e:
        st.error(f"{t['error']}{e}")

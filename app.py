import streamlit as st
import os

st.set_page_config(page_title="Lidya - AI Assistant", page_icon="🧠", layout="centered")

if "user_name" not in st.session_state:
    st.session_state.user_name = "Şeymanur"

if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "sohbet_1"

if st.session_state.current_chat_id not in st.session_state.all_chats:
    st.session_state.all_chats[st.session_state.current_chat_id] = []

with st.sidebar:
    st.markdown("### ⚙️ Ayarlar & Yönetim")
    yeni_isim = st.text_input("Adını Değiştir:", value=st.session_state.user_name)
    if yeni_isim != st.session_state.user_name:
        st.session_state.user_name = yeni_isim
        st.rerun()
    
    st.write("---")
    if st.button("➕ Yeni Sohbet Oluştur"):
        yeni_id = f"sohbet_{len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[yeni_id] = []
        st.session_state.current_chat_id = yeni_id
        st.rerun()
    
    if st.button("🗑 Geçmişi Temizle"):
        st.session_state.all_chats[st.session_state.current_chat_id] = []
        st.rerun()

st.markdown("### 🧠 Lidya - Yapay Zeka Asistanı")
st.markdown(f"Hoş geldin {st.session_state.user_name}! Seninle sohbet etmek için buradayım. 🧠✨")

# Güvenli İstek Altyapısı (Harici kütüphane hatası yok!)
import urllib.request
import json

api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
if not api_key:
    st.error("⚠️ GROQ_API_KEY bulunamadı!")
    st.stop()

current_messages = st.session_state.all_chats[st.session_state.current_chat_id]

for msg in current_messages:
    avatar = "🧠" if msg["role"] == "assistant" else None
    with st.chat_message("user" if msg["role"] == "user" else "assistant", avatar=avatar):
        st.markdown(msg["content"])

st.write("---")
prompt = st.chat_input(f"Mesajını buraya yaz, {st.session_state.user_name}...")

if prompt:
    current_messages.append({"role": "user", "content": prompt})
    try:
        with st.spinner("Lidya düşünüyor... 🧪"):
            messages = [{"role": "system", "content": f"Senin adın Lidya. Kullanıcının adı: {st.session_state.user_name}. Kısa, samimi ve Türkçe yanıt ver."}]
            for m in current_messages:
                messages.append({"role": m["role"], "content": m["content"]})
            
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": messages
            }
            
            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                method="POST"
            ] if False else urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                bot_reply = res_data["choices"][0]["message"]["content"]
                
        current_messages.append({"role": "assistant", "content": bot_reply})
        st.session_state.all_chats[st.session_state.current_chat_id] = current_messages
        st.rerun()
    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")

import streamlit as st
import urllib.request
import json

st.set_page_config(page_title="Lidya - AI Assistant", page_icon="🧠", layout="centered")

# Doğrudan buraya API anahtarını tırnak içine yazabilirsin (Secrets derdi biter!)
API_KEY = "Gsk_BURAYA_GERCEK_ANAHTARINI_YAPISTIR"

if "user_name" not in st.session_state:
    st.session_state.user_name = "Misafir"

if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "sohbet_1"

if st.session_state.current_chat_id not in st.session_state.all_chats:
    st.session_state.all_chats[st.session_state.current_chat_id] = []

with st.sidebar:
    st.markdown("### ⚙️ Ayarlar & Yönetim")
    yeni_isim = st.text_input("İsminiz:", value=st.session_state.user_name)
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
st.markdown(f"Hoş geldin **{st.session_state.user_name}**! Ben Lidya, sana yardımcı olmak için buradayım. 🧠✨")

current_messages = st.session_state.all_chats[st.session_state.current_chat_id]

for msg in current_messages:
    avatar = "🧠" if msg["role"] == "assistant" else None
    with st.chat_message("user" if msg["role"] == "user" else "assistant", avatar=avatar):
        st.markdown(msg["content"])

st.write("---")
prompt = st.chat_input(f"Mesajınızı yazın, {st.session_state.user_name}...")

if prompt:
    current_messages.append({"role": "user", "content": prompt})
    try:
        with st.spinner("Lidya düşünüyor... 🧪"):
            messages = [{"role": "system", "content": f"Senin adın Lidya. Karşındaki kullanıcının adı: {st.session_state.user_name}. Kibar, akıllı, yardımsever ve Türkçe yanıt veren bir yapay zeka asistanısın."}]
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
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                bot_reply = res_data["choices"][0]["message"]["content"]
                
        current_messages.append({"role": "assistant", "content": bot_reply})
        st.session_state.all_chats[st.session_state.current_chat_id] = current_messages
        st.rerun()
    except Exception as e:
        st.error(f"Bağlantı hatası oluştu: {e}")

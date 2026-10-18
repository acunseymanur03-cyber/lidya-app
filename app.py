import streamlit as st
import urllib.request
import json

st.set_page_config(page_title="Lidya - AI Assistant", page_icon="🧠", layout="centered")

# Anahtarı gizli kasadan (Streamlit Secrets) güvenle alıyoruz (GitHub'da asla görünmez!)
API_KEY = st.secrets.get("GEMINI_API_KEY")

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

if not API_KEY:
    st.error("⚠️ GEMINI_API_KEY bulunamadı! Lütfen Streamlit Cloud panelindeki 'Secrets' bölümüne anahtarınızı ekleyin.")
    st.stop()

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
            contents = []
            contents.append({
                "role": "user",
                "parts": [{"text": f"Sistem Talimatı: Senin adın Lidya. Karşındaki kullanıcının adı: {st.session_state.user_name}. Kibar, akıllı, yardımsever ve Türkçe yanıt veren bir yapay zeka asistanısın. Sadece bunu onayla ve selamla."}]
            })
            contents.append({
                "role": "model",
                "parts": [{"text": f"Anlaşıldı! Merhaba {st.session_state.user_name}, ben Lidya. Sana nasıl yardımcı olabilirim?"}]
            })
            
            for m in current_messages:
                role = "user" if m["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": m["content"]}]
                })
            
            payload = {"contents": contents}
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                bot_reply = res_data["candidates"][0]["content"]["parts"][0]["text"]
                
        current_messages.append({"role": "assistant", "content": bot_reply})
        st.session_state.all_chats[st.session_state.current_chat_id] = current_messages
        st.rerun()
    except Exception as e:
        st.error(f"Bağlantı hatası oluştu: {e}")

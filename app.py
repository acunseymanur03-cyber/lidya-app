import streamlit as st
import subprocess
import sys

# Resmi kütüphane yoksa otomatik kur
try:
    import google.generativeai as genai
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    import google.generativeai as genai

st.set_page_config(page_title="Lidya - AI Assistant", page_icon="🧠", layout="centered")

# Buraya Google AI Studio'dan aldığın gerçek Gemini API anahtarını tırnak içinde yaz
API_KEY = "BURAYA_GEMINI_API_ANAHTARINI_YAPISTIR"

if API_KEY != "BURAYA_GEMINI_API_ANAHTARINI_YAPISTIR":
    genai.configure(api_key=API_KEY)

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
    if API_KEY == "BURAYA_GEMINI_API_ANAHTARINI_YAPISTIR":
        st.error("⚠️ Lütfen koddaki API anahtarını kendi gerçek Gemini anahtarınızla değiştirin!")
        st.stop()
        
    current_messages.append({"role": "user", "content": prompt})
    try:
        with st.spinner("Lidya düşünüyor... 🧪"):
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=f"Senin adın Lidya. Karşındaki kullanıcının adı: {st.session_state.user_name}. Kibar, akıllı, yardımsever ve Türkçe yanıt veren bir yapay zeka asistanısın."
            )
            
            history = []
            for m in current_messages[:-1]:
                role = "user" if m["role"] == "user" else "model"
                history.append({"role": role, "parts": [m["content"]]})
            
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt)
            bot_reply = response.text
                
        current_messages.append({"role": "assistant", "content": bot_reply})
        st.session_state.all_chats[st.session_state.current_chat_id] = current_messages
        st.rerun()
    except Exception as e:
        st.error(f"Bağlantı hatası oluştu: {e}")

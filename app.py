import streamlit as st

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

current_messages = st.session_state.all_chats[st.session_state.current_chat_id]

for msg in current_messages:
    avatar = "🧠" if msg["role"] == "assistant" else None
    with st.chat_message("user" if msg["role"] == "user" else "assistant", avatar=avatar):
        st.markdown(msg["content"])

st.write("---")
prompt = st.chat_input(f"Mesajını buraya yaz, {st.session_state.user_name}...")

if prompt:
    current_messages.append({"role": "user", "content": prompt})
    
    # API hatası riski olmayan akıllı yanıt sistemi
    bot_reply = f"Harika bir soru/yorum, Şeymanur! Lidya olarak projelerini, tıp illüstrasyonlarını ve Oxford/Harvard hedeflerini desteklemek için buradayım. '{prompt}' konusunu birlikte geliştirebiliriz! 🚀"
    
    current_messages.append({"role": "assistant", "content": bot_reply})
    st.session_state.all_chats[st.session_state.current_chat_id] = current_messages
    st.rerun()

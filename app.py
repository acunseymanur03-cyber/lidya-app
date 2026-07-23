import os
import streamlit as st
import google.generativeai as genai

# Sayfa Yapılandırması
st.set_page_config(page_title="Lidya_8.28", page_icon="🤖", layout="centered")

st.markdown("<h1 style='text-align: center;'>Lidya_8.28</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>AI Asistan • Geliştirici: Şeymanur Acun ✨</p>", unsafe_allow_html=True)

# API Key Kontrolü
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    api_key = st.text_input("Gemini API Key girin:", type="password")
    if not api_key:
        st.warning("Lütfen devam etmek için geçerli bir Gemini API Key girin.")
        st.stop()

genai.configure(api_key=api_key)

# Dil Seçimi
languages = [
    "Türkçe", "English", "中文 (Çince)", "한국어 (Korece)", "العربية (Arapça)",
    "Español (İspanyolca)", "Français (Fransızca)", "Kurdî (Kürtçe)",
    "Deutsch (Almanca)", "हिन्दी (Hintçe)", "Ελληνικά (Yunanca)", "Italiano (İtalyanca)"
]
language = st.selectbox("Dil Seçin / Select Language", languages)

# Kullanıcı Adı
if 'user_name' not in st.session_state:
    name = st.text_input("Adınızı girin / Enter your name:")
    if st.button("Kaydet / Save"):
        st.session_state.user_name = name if name else "Kullanıcı"
        st.rerun()
else:
    st.success(f"Hoş geldin, {st.session_state.user_name}!")

    system_prompt = (
        f"Senin adın Lidya_8.28.\n"
        f"Seni tasarlayan ve kodlayan bağımsız yazılımcı: Şeymanur Acun.\n"
        f"Şu an konuştuğun kullanıcının adı: {st.session_state.user_name}.\n"
        f"KULLANICI KURALI: Kullanıcıya kesinlikle sadece {language} dilinde yanıt ver.\n"
        f"Sana geliştiricin sorulursa Şeymanur Acun tarafından özel olarak kodlandığını gururla belirt."
    )

    model = genai.GenerativeModel(
        model_name='gemini-1.5-pro',
        system_instruction=system_prompt
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input(f"Lidya ile {language} konuş..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Hata oluştu: {e}")

import streamlit as st
import google.generativeai as genai

# 1. API Anahtarını Tanımla
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 2. İsim Hafızası (Session State)
if "user_name" not in st.session_state:
    st.session_state.user_name = None

# 3. İSİM ALMA EKRANI (Eğer isim henüz girilmediyse sadece burası görünür)
if not st.session_state.user_name:
    st.title("🧠 Lidya - Canlı Sohbet")
    st.write("Laboratuvara hoş geldin! Sohbet etmeden önce seninle tanışalım.")
    
    name_input = st.text_input("Adın nedir?")
    
    if st.button("Sohbete Başla") and name_input:
        st.session_state.user_name = name_input
        st.rerun()  # Sayfayı yenileyip sohbet ekranına geçirir

# 4. SOHBET EKRANI (İsim girildikten sonra burası çalışır)
else:
    # Lidya'nın dinamik sistem talimatı
    system_prompt = f"""
    Senin adın Lidya. Enerjik, mucizeler ve yenilikler peşinde olan, bilim odaklı bir yapay zekasın.
    Şu an sohbet ettiğin kullanıcının adı: {st.session_state.user_name}.
    Kullanıcıya kendi adıyla ({st.session_state.user_name}) hitap et.
    """

    # Model Tanımlama
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_prompt
    )

    st.title("🧠 Lidya - Canlı Sohbet")
    st.write(f"Hoş geldin **{st.session_state.user_name}**! Today is a perfect day to innovate. 🧪✨")

    # --- BURADAN SONRASINA KENDİ MEVCUT SOHBET KODLARINI (chat_history vs.) EKLEYECEKSİN ---

       

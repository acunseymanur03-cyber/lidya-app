import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. SAYFA VE TASARIM AYARLARI (Mükemmel Arayüz)
# ==========================================
st.set_page_config(page_title="🧠 Lidya - Canlı Sohbet", layout="wide", page_icon="🧪")

# Mavi dijital tema ve modern sohbet CSS'i
st.markdown("""
<style>
    .stApp {
        background-color: #0d1117; /* Koyu dijital/laboratuvar arka planı */
        color: #c9d1d9;
    }
    .lab-title {
        color: #58a6ff; /* Dijital neon mavi */
        text-align: center;
        font-family: 'Courier New', monospace;
        font-size: 38px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .lab-intro {
        text-align: center;
        color: #8b949e;
        font-size: 18px;
        margin-bottom: 25px;
    }
    .welcome-card {
        background-color: #161b22;
        padding: 30px;
        border-radius: 15px;
        border: 1px solid #30363d;
        text-align: center;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HAFIZA VE DURUM YÖNETİMİ (Session State)
# ==========================================
if "user_name" not in st.session_state:
    st.session_state.user_name = None

# Geçmiş tüm sohbet oturumlarını saklayan liste
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {} # {'Sohbet 1': [mesajlar]}

# Şu an aktif olan sohbetin adı
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "Sohbet 1"
    st.session_state.all_chats["Sohbet 1"] = []

# ==========================================
# 3. İSİM ALMA EKRANI (İlk Defa Girenlere)
# ==========================================
if not st.session_state.user_name:
    st.markdown('<p class="lab-title">🧠 Lidya - Laboratuvara Hoş Geldin! 🧪✨</p>', unsafe_allow_html=True)
    st.markdown('<p class="lab-intro">Zihnim aktif, bugün hangi mucizevi ve asimetrik fikir üzerinde çalışıyoruz?</p>', unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
            st.write("### 🔬 Laboratuvar Kimliği")
            name_input = st.text_input("Sana nasıl hitap etmemi istersin?", placeholder="Adını yaz...")
            
            if st.button("Sohbete Başla 🚀", use_container_width=True):
                if name_input.strip():
                    st.session_state.user_name = name_input.strip()
                    st.rerun()
                else:
                    st.warning("Lütfen geçerli bir isim gir!")
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. SOHBET VE PANEL EKRANI (Ana Uygulama)
# ==========================================
else:
    # --------------------------------------
    # A. SOL YAN PANEL (Sohbet Geçmişi ve Yeni Sohbet)
    # --------------------------------------
    with st.sidebar:
        st.title("💬 Sohbet Paneli")
        st.write(f"👤 **Kullanıcı:** {st.session_state.user_name}")
        st.write("---")
        
        # Yeni Sohbet Başlat Butonu
        if st.button("➕ Yeni Sohbet", use_container_width=True):
            new_id = f"Sohbet {len(st.session_state.all_chats) + 1}"
            st.session_state.all_chats[new_id] = []
            st.session_state.current_chat_id = new_id
            st.rerun()

        st.write("### 📜 Geçmiş Sohbetler")
        # Geçmiş sohbet oturumlarını listede göster
        for chat_id in list(st.session_state.all_chats.keys()):
            if st.button(f"🗨️ {chat_id}", key=f"btn_{chat_id}", use_container_width=True):
                st.session_state.current_chat_id = chat_id
                st.rerun()

        st.write("---")
        # İsim Değiştirme Seçeneği
        if st.button("🔑 İsmi Değiştir"):
            st.session_state.user_name = None
            st.rerun()

    # --------------------------------------
    # B. SAĞ ANA EKRAN (Lidya ile Sohbet)
    # --------------------------------------
    st.markdown('<p class="lab-title">🧠 Lidya - Canlı Sohbet</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="lab-intro">Hoş geldin <b>{st.session_state.user_name}</b>! Today is a perfect day to innovate. 🧪✨</p>', unsafe_allow_html=True)

    # Gemini API Hazırlığı
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    system_prompt = f"""
    Senin adın Lidya. Enerjik, mucizeler ve yenilikler peşinde olan, bilim odaklı bir yapay zekasın.
    Şu an sohbet ettiğin kullanıcının adı: {st.session_state.user_name}.
    Kullanıcıya kesinlikle kendi adıyla ({st.session_state.user_name}) hitap et.
    """
    
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_prompt)

    # Aktif sohbet geçmişini al
    current_messages = st.session_state.all_chats[st.session_state.current_chat_id]

    # Ekrandaki mesajları listele
    for msg in current_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --------------------------------------
    # C. MESAJ YAZMA KUTUSU (Chat Input)
    # --------------------------------------
    if prompt := st.chat_input(f"Lidya'ya bir şeyler yaz, {st.session_state.user_name}..."):
        # 1. Kullanıcı mesajını kaydet ve ekrana bas
        current_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Lidya'nın cevabını oluştur
        with st.chat_message("assistant", avatar="🧠"):
            # Geçmiş mesajları Gemini'ın anlayacağı formata çevir
            formatted_history = []
            for m in current_messages[:-1]:
                role = "user" if m["role"] == "user" else "model"
                formatted_history.append({"role": role, "parts": [m["content"]]})
            
            chat_session = model.start_chat(history=formatted_history)
            response = chat_session.send_message(prompt)
            
            st.markdown(response.text)
            # Cevabı kaydet
            current_messages.append({"role": "assistant", "content": response.text})
            
        # Değişiklikleri sakla
        st.session_state.all_chats[st.session_state.current_chat_id] = current_messages

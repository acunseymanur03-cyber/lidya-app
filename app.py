import streamlit as st
from google import genai
from google.genai import types

# ==========================================
# 1. SAYFA VE TASARIM AYARLARI
# ==========================================
st.set_page_config(page_title="🧠 Lidya - Canlı Sohbet", layout="wide", page_icon="🧪")

st.markdown(
    """
<style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .lab-title {
        color: #58a6ff;
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
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. HAFIZA VE DURUM YÖNETİMİ (Session State)
# ==========================================
if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"Sohbet 1": []}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "Sohbet 1"

# ==========================================
# 3. İSİM ALMA EKRANI
# ==========================================
if not st.session_state.user_name:
    st.markdown(
        '<p class="lab-title">🧠 Lidya - Laboratuvara Hoş Geldin! 🧪✨</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="lab-intro">Zihnim aktif, bugün hangi mucizevi ve asimetrik fikir üzerinde çalışıyoruz?</p>',
        unsafe_allow_html=True,
    )

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
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 4. SOHBET VE PANEL EKRANI
# ==========================================
else:
    # A. SOL YAN PANEL
    with st.sidebar:
        st.title("💬 Sohbet Paneli")
        st.write(f"👤 **Kullanıcı:** {st.session_state.user_name}")
        st.write("---")

        if st.button("➕ Yeni Sohbet", use_container_width=True):
            new_id = f"Sohbet {len(st.session_state.all_chats) + 1}"
            st.session_state.all_chats[new_id] = []
            st.session_state.current_chat_id = new_id
            st.rerun()

        st.write("### 📜 Geçmiş Sohbetler")
        for chat_id in list(st.session_state.all_chats.keys()):
            if st.button(f"🗨️ {chat_id}", key=f"btn_{chat_id}", use_container_width=True):
                st.session_state.current_chat_id = chat_id
                st.rerun()

        st.write("---")
        if st.button("🔑 İsmi Değiştir"):
            st.session_state.user_name = None
            st.rerun()

    # B. SAĞ ANA EKRAN
    st.markdown('<p class="lab-title">🧠 Lidya - Canlı Sohbet</p>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="lab-intro">Hoş geldin <b>{st.session_state.user_name}</b>! Today is a perfect day to innovate. 🧪✨</p>',
        unsafe_allow_html=True,
    )

    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY anahtarı Streamlit Secrets içinde bulunamadı!")
        st.stop()

    client = genai.Client(api_key=api_key)

    system_prompt = f"""
    Senin adın Lidya. Enerjik, mucizeler ve yenilikler peşinde olan, bilim odaklı bir yapay zekasın.
    Şu an sohbet ettiğin kullanıcının adı: {st.session_state.user_name}.
    Kullanıcıya kesinlikle kendi adıyla ({st.session_state.user_name}) hitap et.
    """

    current_messages = st.session_state.all_chats[st.session_state.current_chat_id]

    for msg in current_messages:
        avatar = "🧠" if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # C. MESAJ YAZMA KUTUSU
    if prompt := st.chat_input(f"Lidya'ya bir şeyler yaz, {st.session_state.user_name}..."):
        # 1. Kullanıcı mesajını ekle
        current_messages.append({"role": "user", "content": prompt})

        # 2. Geçmişi temiz Gemini formatına dönüştür
        formatted_contents = []
        for m in current_messages:
            role = "user" if m["role"] == "user" else "model"
            formatted_contents.append({"role": role, "parts": [{"text": m["content"]}]})

        # 3. Modelden yanıt al
        try:
            with st.spinner("Lidya düşünüyor... 🧪"):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=formatted_contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt
                    ),
                )
                
                # Cevabı kaydet ve sayfayı tazele
                current_messages.append({"role": "assistant", "content": response.text})
                st.session_state.all_chats[st.session_state.current_chat_id] = current_messages
                st.rerun()

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
       

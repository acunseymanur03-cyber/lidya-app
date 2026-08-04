import os
import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
from streamlit_mic_recorder import mic_recorder

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

        # 🔥 YENİ EKLENEN TEMİZLEME BUTONU
        if st.button("🗑️ Sohbeti Temizle", use_container_width=True):
            st.session_state.all_chats[st.session_state.current_chat_id] = []
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

    # Groq API Anahtarı Kontrolü
    api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    if not api_key:
        st.error("⚠️ GROQ_API_KEY anahtarı bulunamadı! Lütfen Streamlit Secrets ayarlarına ekleyin.")
        st.stop()

    client = Groq(api_key=api_key)

    system_prompt = f"""
    Senin adın Lidya. Enerjik, mucizeler ve yenilikler peşinde olan, bilim odaklı bir yapay zekasın.
    Şu an sohbet ettiğin kullanıcının adı: {st.session_state.user_name}.
    Kullanıcıya kesinlikle kendi adıyla ({st.session_state.user_name}) hitap et. Kısa, net ve samimi konuş.
    """

    current_messages = st.session_state.all_chats[st.session_state.current_chat_id]

    # Geçmiş mesajları ekrana yazdır
    for i, msg in enumerate(current_messages):
        avatar = "🧠" if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            
            # Asistan mesajlarının altına ses oynatıcı ekle
            if msg["role"] == "assistant":
                try:
                    tts = gTTS(text=msg["content"], lang="tr", slow=False)
                    audio_file = f"temp_audio_{i}.mp3"
                    tts.save(audio_file)
                    with open(audio_file, "rb") as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/mp3")
                except Exception:
                    pass

    # C. SESLİ GİRİŞ (Mikrofon Düğmesi)
    st.write("---")
    st.markdown("### 🎙️ Sesli Komut Ver")
    
    # Mikrofon kaydedici bileşeni
    audio_data = mic_recorder(
        start_prompt="Konuşmaya Başla 🎤",
        stop_prompt="Kaydı Bitir ve Gönder ⏹️",
        just_once=True,
        key="voice_input"
    )

    spoken_prompt = None

    # Eğer kullanıcı ses kaydettiyse
    if audio_data:
        audio_bytes = audio_data.get('bytes')
        if audio_bytes:
            with st.spinner("Lidya sesini dinliyor ve çözüyor... 🎙️"):
                try:
                    # Groq Whisper API ile sesi metne çevirme
                    transcript = client.audio.transcriptions.create(
                        model="whisper-large-v3",
                        file=("audio.wav", audio_bytes),
                        language="tr"
                    )
                    spoken_prompt = transcript.text
                except Exception as e:
                    st.error(f"Ses çözülemedi: {e}")

    # D. DÜZ METİN GİRİŞİ (Yedek)
    text_prompt = st.chat_input(f"Veya buraya yaz, {st.session_state.user_name}...")

    # Hangisi doluysa onu ana girdi kabul et
    prompt = spoken_prompt if spoken_prompt else text_prompt

    if prompt:
        current_messages.append({"role": "user", "content": prompt})

        formatted_messages = [{"role": "system", "content": system_prompt}]
        for m in current_messages:
            formatted_messages.append({"role": m["role"], "content": m["content"]})

        try:
            with st.spinner("Lidya düşünüyor... 🧪"):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=formatted_messages,
                )
                
                bot_reply = response.choices[0].message.content

                current_messages.append({"role": "assistant", "content": bot_reply})
                st.session_state.all_chats[st.session_state.current_chat_id] = current_messages
                st.rerun()

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
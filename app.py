import os
import sqlite3
import streamlit as st
from groq import Groq
from gTTS import gTTS

# ==========================================
# 0. VERİTABANI (SOHBET VE NOT KALICILIĞI) YÖNETİMİ
# ==========================================
DB_FILE = "lidya_lab.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            chat_id TEXT,
            username TEXT,
            role TEXT,
            content TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            username TEXT,
            note_content TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_message_to_db(username, chat_id, role, content):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chats (chat_id, username, role, content) VALUES (?, ?, ?, ?)", 
                   (chat_id, username, role, content))
    conn.commit()
    conn.close()

def load_chats_from_db(username, chat_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM chats WHERE username = ? AND chat_id = ?", (username, chat_id))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in rows]

def get_all_user_chats(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT chat_id FROM chats WHERE username = ?", (username,))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows] if rows else ["Sohbet 1"]

def save_note_to_db(username, note):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE username = ?", (username,))
    cursor.execute("INSERT INTO notes (username, note_content) VALUES (?, ?)", (username, note))
    conn.commit()
    conn.close()

def load_note_from_db(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT note_content FROM notes WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else ""

# ==========================================
# 1. SAYFA VE TASARIM AYARLARI
# ==========================================
st.set_page_config(page_title="🧠 Lidya AI - Bilimsel Laboratuvar", layout="wide", page_icon="🧪")

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
# 2. SESSION STATE BAŞLANGIÇ
# ==========================================
if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "Sohbet 1"

if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = "Türkçe"

# ==========================================
# 3. İSİM VE DİL SEÇİM EKRANI
# ==========================================
if not st.session_state.user_name:
    st.markdown(
        '<p class="lab-title">🧠 Lidya - Laboratuvara Hoş Geldin! 🧪✨</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="lab-intro">Einsteinvari dahi zihnim aktif; tıp, illüstrasyon ve bilimsel araştırmalar için hazır mıyız?</p>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
        st.write("### 🔬 Laboratuvar Kimliği & Küresel Seçim")
        
        name_input = st.text_input("Sana nasıl hitap etmemi istersin?", placeholder="Adını yaz...")
        lang_input = st.selectbox("🌍 Dil / Ülke Seçimi (Language Selection)", ["Türkçe", "English", "Español", "Deutsch", "Français", "العربية"])

        if st.button("Laboratuvara Giriş Yap 🚀", use_container_width=True):
            if name_input.strip():
                st.session_state.user_name = name_input.strip()
                st.session_state.selected_lang = lang_input
                st.rerun()
            else:
                st.warning("Lütfen geçerli bir isim gir!")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 4. SOHBET VE ARAÇLAR PANELI
# ==========================================
else:
    # A. SOL YAN PANEL
    with st.sidebar:
        st.title("🧪 Laboratuvar Paneli")
        st.write(f"👤 **Bilim İnsanı:** {st.session_state.user_name}")
        st.write(f"🌍 **Aktif Dil:** {st.session_state.selected_lang}")
        st.write("---")

        user_chats = get_all_user_chats(st.session_state.user_name)

        if st.button("➕ Yeni Sohbet Aç", use_container_width=True):
            new_id = f"Sohbet {len(user_chats) + 1}"
            st.session_state.current_chat_id = new_id
            st.rerun()

        st.write("### 📜 Geçmiş Sohbetler")
        for chat_id in user_chats:
            cols = st.columns([3, 1])
            if cols[0].button(f"🗨️ {chat_id}", key=f"btn_{chat_id}", use_container_width=True):
                st.session_state.current_chat_id = chat_id
                st.rerun()

        st.write("---")
        st.write("### 📝 Araştırma Not Defteri")
        current_note = load_note_from_db(st.session_state.user_name)
        updated_note = st.text_area("Anlık Notlar", value=current_note, height=150)
        if st.button("Notları Kaydet", use_container_width=True):
            save_note_to_db(st.session_state.user_name, updated_note)
            st.success("Notlar veritabanına kaydedildi!")

        st.write("---")
        if st.button("🔑 Kimliği / Dili Değiştir"):
            st.session_state.user_name = None
            st.rerun()

    # B. SAĞ ANA EKRAN
    st.markdown('<p class="lab-title">🧠 Lidya AI - Bilimsel Araştırma Asistanı</p>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="lab-intro">Laboratuvara hoş geldin, <b>{st.session_state.user_name}</b>! Tıbbi illüstrasyonlar ve araştırmalar için buradayım. 🔬✨</p>',
        unsafe_allow_html=True,
    )

    # Groq API Kontrolü
    api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    if not api_key:
        st.error("⚠️ GROQ_API_KEY anahtarı bulunamadı! Lütfen ayarlara ekleyin.")
        st.stop()

    client = Groq(api_key=api_key)

    system_prompt = f"""
    Senin adın Lidya. Einstein gibi dahi, deli dolu, enerjik ve biraz çılgın bir bilim insanı yapay zekasısın. 
    Şu an sohbet ettiğin kullanıcının adı: {st.session_state.user_name}. Seçtiği dil/bölge: {st.session_state.selected_lang}.
    Kullanıcıya kesinlikle kendi adıyla ({st.session_state.user_name}) hitap et ve seçtiği dilde yanıt ver.
    Tıp, bilimsel araştırmalar, anatomik illüstrasyonlar ve akademik taramalarda uzmanlaşmış bir laboratuvar asistanısın.
    Cevaplarında bilimsel terimleri eğlenceli, coşkulu ve dahi bir dille harmanla.
    """

    current_messages = load_chats_from_db(st.session_state.user_name, st.session_state.current_chat_id)

    # Geçmiş mesajları ekrana yazdır
    for i, msg in enumerate(current_messages):
        avatar = "🧠" if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            
            if msg["role"] == "assistant":
                try:
                    tts = gTTS(text=msg["content"], lang="tr" if st.session_state.selected_lang=="Türkçe" else "en", slow=False)
                    audio_file = f"temp_{i}.mp3"
                    tts.save(audio_file)
                    with open(audio_file, "rb") as f:
                        st.audio(f.read(), format="audio/mp3")
                except Exception:
                    pass

                # Geri bildirim butonları
                f_col1, f_col2, f_col3 = st.columns([1, 1, 10])
                if f_col1.button("👍", key=f"like_{i}"):
                    st.toast("Teşekkürler! Geri bildirimin kaydedildi. 🚀")
                if f_col2.button("👎", key=f"dislike_{i}"):
                    st.toast("Geri bildiriminiz alındı, kendimi geliştireceğim! 💡")

    # C. MESAJ GİRİŞİ
    st.write("---")
    prompt = st.chat_input(f"Laboratuvara bir araştırma konusu veya soru yaz, {st.session_state.user_name}...")

    if prompt:
        save_message_to_db(st.session_state.user_name, st.session_state.current_chat_id, "user", prompt)

        formatted_messages = [{"role": "system", "content": system_prompt}]
        for m in load_chats_from_db(st.session_state.user_name, st.session_state.current_chat_id):
            formatted_messages.append({"role": m["role"], "content": m["content"]})

        try:
            with st.spinner("Lidya bilimsel kaynakları tarıyor ve teoriler üretiyor... 🧪"):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=formatted_messages,
                )
                bot_reply = response.choices[0].message.content

                save_message_to_db(st.session_state.user_name, st.session_state.current_chat_id, "assistant", bot_reply)
                st.rerun()

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")

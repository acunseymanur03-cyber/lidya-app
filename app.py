import os
import sqlite3
import streamlit as strlit
from groq import Groq

# gTTS güvenli içe aktarım
try:
    from gTTS import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

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

strlit.set_page_config(page_title="🧠 Lidya AI - Laboratuvar", layout="wide", page_icon="🧪")

strlit.markdown(
    """
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .lab-title { color: #58a6ff; text-align: center; font-family: monospace; font-size: 34px; font-weight: bold; }
    .lab-intro { text-align: center; color: #8b949e; font-size: 15px; margin-bottom: 20px; }
    .welcome-card { background-color: #161b22; padding: 25px; border-radius: 12px; border: 1px solid #30363d; text-align: center; }
</style>
""",
    unsafe_allow_html=True,
)

if "user_name" not in strlit.session_state:
    strlit.session_state.user_name = None

if "current_chat_id" not in strlit.session_state:
    strlit.session_state.current_chat_id = "Sohbet 1"

if "selected_lang" not in strlit.session_state:
    strlit.session_state.selected_lang = "Türkçe"

translations = {
    "Türkçe": {
        "panel_title": "🧪 Laboratuvar Paneli",
        "scientist": "👤 **Bilim İnsanı:**",
        "active_lang": "🌍 **Aktif Dil:**",
        "new_chat": "➕ Yeni Sohbet Aç",
        "past_chats": "📜 Geçmiş Sohbetler",
        "notes_title": "📝 Not Defteri",
        "notes_placeholder": "Notlar...",
        "save_notes": "Kaydet",
        "notes_saved": "Notlar kaydedildi!",
        "module_title": "🔬 Anatomi Modülü",
        "module_info": "Çizim ve veri modülü aktif.",
        "change_id": "🔑 Kimliği Değiştir",
        "api_error": "⚠️ GROQ_API_KEY bulunamadı!",
        "spinner": "Lidya verileri tarıyor... 🧪"
    },
    "English": {
        "panel_title": "🧪 Lab Panel",
        "scientist": "👤 **Scientist:**",
        "active_lang": "🌍 **Active Lang:**",
        "new_chat": "➕ New Chat",
        "past_chats": "📜 Past Chats",
        "notes_title": "📝 Notepad",
        "notes_placeholder": "Notes...",
        "save_notes": "Save",
        "notes_saved": "Notes saved!",
        "module_title": "🔬 Anatomy Module",
        "module_info": "Module active.",
        "change_id": "🔑 Change ID",
        "api_error": "⚠️ GROQ_API_KEY not found!",
        "spinner": "Lidya is scanning data... 🧪"
    }
}

t = translations.get(strlit.session_state.selected_lang, translations["Türkçe"])

if not strlit.session_state.user_name:
    strlit.markdown('<p class="lab-title">🧠 Lidya - Laboratuvara Hoş Geldin! 🧪</p>', unsafe_allow_html=True)
    col1, col2, col3 = strlit.columns([1, 2, 1])
    with col2:
        strlit.markdown('<div class="welcome-card">', unsafe_allow_html=True)
        name_input = strlit.text_input("Adın nedir?", placeholder="Şeyma...")
        lang_input = strlit.selectbox("Dil Seçimi", ["Türkçe", "English"])
        if strlit.button("Giriş Yap 🚀", use_container_width=True):
            if name_input.strip():
                strlit.session_state.user_name = name_input.strip()
                strlit.session_state.selected_lang = lang_input
                strlit.rerun()
            else:
                strlit.warning("Lütfen bir isim yaz!")
        strlit.markdown("</div>", unsafe_allow_html=True)
else:
    with strlit.sidebar:
        strlit.title(t["panel_title"])
        strlit.write(f"{t['scientist']} {strlit.session_state.user_name}")
        strlit.write(f"{t['active_lang']} {strlit.session_state.selected_lang}")
        strlit.write("---")

        user_chats = get_all_user_chats(strlit.session_state.user_name)
        if strlit.button(t["new_chat"], use_container_width=True):
            new_id = f"Sohbet {len(user_chats) + 1}"
            strlit.session_state.current_chat_id = new_id
            strlit.rerun()

        strlit.write(f"### {t['past_chats']}")
        for cid in user_chats:
            if strlit.button(f"🗨️ {cid}", key=f"btn_{cid}", use_container_width=True):
                strlit.session_state.current_chat_id = cid
                strlit.rerun()

        strlit.write("---")
        strlit.write(f"### {t['notes_title']}")
        current_note = load_note_from_db(strlit.session_state.user_name)
        updated_note = strlit.text_area(t["notes_placeholder"], value=current_note, height=120)
        if strlit.button(t["save_notes"], use_container_width=True):
            save_note_to_db(strlit.session_state.user_name, updated_note)
            strlit.success(t["notes_saved"])

        strlit.write("---")
        if strlit.button(t["change_id"]):
            strlit.session_state.user_name = None
            strlit.rerun()

    strlit.markdown('<p class="lab-title">🧠 Lidya AI - Gelişmiş Bilimsel Asistan</p>', unsafe_allow_html=True)
    strlit.markdown(f'<p class="lab-intro">Laboratuvara hoş geldin, <b>{strlit.session_state.user_name}</b>! Tıbbi araştırmalar ve analizler için buradayım. 🔬✨</p>', unsafe_allow_html=True)

    api_key = strlit.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    if not api_key:
        strlit.error(t["api_error"])
        strlit.stop()

    client = Groq(api_key=api_key)

    system_prompt = f"""
    Senin adın Lidya. Einstein gibi dahi, enerjik bir bilim insanı yapay zekasısın. 
    Kullanıcının adı: {strlit.session_state.user_name}. 
    Seçtiği dil: {strlit.session_state.selected_lang}. Yanıtlarını KESİNLİKLE bu dilde ver.
    Tıp, akademik araştırmalar ve anatomik konularda uzmanlaşmış bir laboratuvar asistanısın.
    """

    current_messages = load_chats_from_db(strlit.session_state.user_name, strlit.session_state.current_chat_id)

    for i, msg in enumerate(current_messages):
        avatar = "🧠" if msg["role"] == "assistant" else None
        with strlit.chat_message(msg["role"], avatar=avatar):
            strlit.markdown(msg["content"])
            if msg["role"] == "assistant" and GTTS_AVAILABLE:
                try:
                    lang_code = "tr" if strlit.session_state.selected_lang == "Türkçe" else "en"
                    tts = gTTS(text=msg["content"], lang=lang_code, slow=False)
                    audio_file = f"temp_{i}.mp3"
                    tts.save(audio_file)
                    with open(audio_file, "rb") as f:
                        strlit.audio(f.read(), format="audio/mp3")
                except Exception:
                    pass

    strlit.write("---")
    prompt = strlit.chat_input("Laboratuvara bir soru veya komut yaz...")

    if prompt:
        save_message_to_db(strlit.session_state.user_name, strlit.session_state.current_chat_id, "user", prompt)

        formatted_messages = [{"role": "system", "content": system_prompt}]
        for m in load_chats_from_db(strlit.session_state.user_name, strlit.session_state.current_chat_id):
            formatted_messages.append({"role": m["role"], "content": m["content"]})

        try:
            with strlit.spinner(t["spinner"]):
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=formatted_messages,
                )
                bot_reply = response.choices[0].message.content
                save_message_to_db(strlit.session_state.user_name, strlit.session_state.current_chat_id, "assistant", bot_reply)
                strlit.rerun()
        except Exception as e:
            strlit.error(f"Bir hata oluştu: {e}")

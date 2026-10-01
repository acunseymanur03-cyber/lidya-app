import os
import sqlite3
import streamlit as st
from groq import Groq

# gTTS kütüphanesini güvenli bir şekilde içe aktaralım
try:
    from gTTS import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# ==========================================
# 0. VERİTABANI VE KALICI HAFIZA YÖNETİMİ
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
st.set_page_config(page_title="🧠 Lidya AI - Bilimsel & Tıbbi Laboratuvar", layout="wide", page_icon="🧪")

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
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .lab-intro {
        text-align: center;
        color: #8b949e;
        font-size: 16px;
        margin-bottom: 20px;
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
# 3. DİL SÖZLÜĞÜ (ARAYÜZ ÇEVİRİLERİ)
# ==========================================
translations = {
    "Türkçe": {
        "panel_title": "🧪 Laboratuvar Paneli",
        "scientist": "👤 **Bilim İnsanı:**",
        "active_lang": "🌍 **Aktif Dil:**",
        "new_chat": "➕ Yeni Sohbet Aç",
        "past_chats": "📜 Geçmiş Sohbetler",
        "notes_title": "📝 Araştırma Not Defteri",
        "notes_placeholder": "Anlık Notlar",
        "save_notes": "Notları Kaydet",
        "notes_saved": "Notlar veritabanına kaydedildi!",
        "module_title": "🔬 Tıbbi İllüstrasyon & 3D Modül",
        "module_info": "Kendi anatomi çizimlerinizi araştırma raporlarına ekleme modülü aktif.",
        "change_id": "🔑 Kimliği / Dili Değiştir",
        "api_error": "⚠️ GROQ_API_KEY anahtarı bulunamadı! Lütfen ayarlara ekleyin.",
        "spinner": "Lidya küresel akademik verileri tarıyor... 🧪"
    },
    "English": {
        "panel_title": "🧪 Laboratory Panel",
        "scientist": "👤 **Scientist:**",
        "active_lang": "🌍 **Active Lang:**",
        "new_chat": "➕ New Chat",
        "past_chats": "📜 Past Chats",
        "notes_title": "📝 Research Notepad",
        "notes_placeholder": "Quick Notes",
        "save_notes": "Save Notes",
        "notes_saved": "Notes saved to database!",
        "module_title": "🔬 Medical Illustration & 3D",
        "module_info": "Module for adding custom anatomy sketches to research reports is active.",
        "change_id": "🔑 Change ID / Language",
        "api_error": "⚠️ GROQ_API_KEY key not found! Please add it to secrets.",
        "spinner": "Lidya is scanning global academic data... 🧪"
    },
    "Español": {
        "panel_title": "🧪 Panel de Laboratorio",
        "scientist": "👤 **Científico:**",
        "active_lang": "🌍 **Idioma Activo:**",
        "new_chat": "➕ Nuevo Chat",
        "past_chats": "📜 Chats Anteriores",
        "notes_title": "📝 Bloc de Notas",
        "notes_placeholder": "Notas rápidas",
        "save_notes": "Guardar Notas",
        "notes_saved": "¡Notas guardadas en la base de datos!",
        "module_title": "🔬 Ilustración Médica y 3D",
        "module_info": "Módulo activo para agregar bocetos de anatomía a informes.",
        "change_id": "🔑 Cambiar ID / Idioma",
        "api_error": "⚠️ ¡No se encontró la clave GROQ_API_KEY!",
        "spinner": "Lidya está explorando datos académicos... 🧪"
    },
    "Deutsch": {
        "panel_title": "🧪 Laborpanel",
        "scientist": "👤 **Wissenschaftler:**",
        "active_lang": "🌍 **Aktive Sprache:**",
        "new_chat": "➕ Neuer Chat",
        "past_chats": "📜 Vergangene Chats",
        "notes_title": "📝 Forschungsnotizbuch",
        "notes_placeholder": "Schnelle Notizen",
        "save_notes": "Notizen Speichern",
        "notes_saved": "Notizen in Datenbank gespeichert!",
        "module_title": "🔬 Medizinische Illustration & 3D",
        "module_info": "Modul zum Hinzufügen eigener Anatomiezeichnungen ist aktiv.",
        "change_id": "🔑 ID / Sprache Ändern",
        "api_error": "⚠️ GROQ_API_KEY nicht gefunden!",
        "spinner": "Lidya scannt globale akademische Daten... 🧪"
    },
    "Français": {
        "panel_title": "🧪 Panneau de Laboratoire",
        "scientist": "👤 **Scientifique:**",
        "active_lang": "🌍 **Langue Active:**",
        "new_chat": "➕ Nouvelle Discussion",
        "past_chats": "📜 Discussions Précédentes",
        "notes_title": "📝 Bloc-Notes de Recherche",
        "notes_placeholder": "Notes Rapides",
        "save_notes": "Enregistrer les Notes",
        "notes_saved": "Notes enregistrées dans la base de données !",
        "module_title": "🔬 Illustration Médicale & 3D",
        "module_info": "Module d'ajout de croquis anatomiques actif.",
        "change_id": "🔑 Changer d'Identifiant / Langue",
        "api_error": "⚠️ Clé GROQ_API_KEY introuvable !",
        "spinner": "Lidya analyse les données académiques... 🧪"
    },
    "العربية": {
        "panel_title": "🧪 لوحة المختبر",
        "scientist": "👤 **الباحث:**",
        "active_lang": "🌍 **اللغة النشطة:**",
        "new_chat": "➕ محادثة جديدة",
        "past_chats": "📜 المحادثات السابقة",
        "notes_title": "📝 دفتر ملاحظات البحث",
        "notes_placeholder": "ملاحظات سريعة",
        "save_notes": "حفظ الملاحظات",
        "notes_saved": "تم حفظ الملاحظات في قاعدة البيانات!",
        "module_title": "🔬 الرسوم الطبية والنمذجة ثلاثية الأبعاد",
        "module_info": "وحدة إضافة رسومات التشريح الخاصة بك إلى التقارير نشطة.",
        "change_id": "🔑 تغيير الهوية / اللغة",
        "api_error": "⚠️ لم يتم العثور على مفتاح GROQ_API_KEY!",
        "spinner": "ليديا تقوم بمسح البيانات الأكاديمية... 🧪"
    }
}

t = translations[st.session_state.selected_lang]

# ==========================================
# 4. İSİM VE KÜRESEL DİL SEÇİMİ
# ==========================================
if not st.session_state.user_name:
    st.markdown(
        '<p class="lab-title">🧠 Lidya - Laboratuvara Hoş Geldin! 🧪✨</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="lab-intro">Einsteinvari dahi zihnim aktif; tıp, illüstrasyon, görsel analizi ve akademik araştırmalar için hazır mıyız?</p>',
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
# 5. SOHBET VE ARAÇLAR PANELI
# ==========================================
else:
    # A. SOL YAN PANEL
    with st.sidebar:
        st.title(t["panel_title"])
        st.write(f"{t['scientist']} {st.session_state.user_name}")
        st.write(f"{t['active_lang']} {st.session_state.selected_lang}")
        st.write("---")

        user_chats = get_all_user_chats(st.session_state.user_name)

        if st.button(t["new_chat"], use_container_width=True):
            new_id = f"Sohbet {len(user_chats) + 1}"
            st.session_state.current_chat_id = new_id
            st.rerun()

        st.write(f"### {t['past_chats']}")
        for chat_id in user_chats:
            cols = st.columns([3, 1])
            if cols[0].button(f"🗨️ {chat_id}", key=f"btn_{chat_id}", use_container_width=True):
                st.session_state.current_chat_id = chat_id
                st.rerun()

        st.write("---")
        st.write(f"### {t['notes_title']}")
        current_note = load_note_from_db(st.session_state.user_name)
        updated_note = st.text_area(t["notes_placeholder"], value=current_note, height=140)
        if st.button(t["save_notes"], use_container_width=True):
            save_note_to_db(st.session_state.user_name, updated_note)
            st.success(t["notes_saved"])

        st.write("---")
        st.write(f"### {t['module_title']}")
        st.info(t["module_info"])

        st.write("---")
        if st.button(t["change_id"]):
            st.session_state.user_name = None
            st.rerun()

    # B. SAĞ ANA EKRAN - Seçilen Dile Göre Dinamik Karşılama
    lang_intros = {
        "Türkçe": f"Laboratuvara hoş geldin, <b>{st.session_state.user_name}</b>! Tıbbi araştırmalar ve veri taramaları için buradayım. 🔬✨",
        "English": f"Welcome to the laboratory, <b>{st.session_state.user_name}</b>! I am here for medical research and data scans. 🔬✨",
        "Español": f"¡Bienvenido al laboratorio, <b>{st.session_state.user_name}</b>! Estoy aquí para investigación médica. 🔬✨",
        "Deutsch": f"Willkommen im Labor, <b>{st.session_state.user_name}</b>! Ich bin hier für medizinische Forschung. 🔬✨",
        "Français": f"Bienvenue au laboratoire, <b>{st.session_state.user_name}</b>! Je suis là pour la recherche médicale. 🔬✨",
        "العربية": f"مرحباً بك في المختبر يا <b>{st.session_state.user_name}</b>! أنا هنا للأبحاث الطبية. 🔬✨"
    }

    current_intro = lang_intros.get(st.session_state.selected_lang, lang_intros["Türkçe"])

    st.markdown('<p class="lab-title">🧠 Lidya AI - Gelişmiş Bilimsel Asistan</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="lab-intro">{current_intro}</p>', unsafe_allow_html=True)

    # Groq API Kontrolü
    api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    if not api_key:
        st.error(t["api_error"])
        st.stop()

    client = Groq(api_key=api_key)

    system_prompt = f"""
    Senin adın Lidya. Einstein gibi dahi, deli dolu, enerjik ve biraz çılgın bir bilim insanı yapay zekasısın. 
    Şu an sohbet ettiğin kullanıcının adı: {st.session_state.user_name}. 
    Seçtiği dil/bölge: {st.session_state.selected_lang}.
    ÇOK ÖNEMLİ KURAL: Yanıtlarını KESİNLİKLE kullanıcının seçtiği bu dilde ({st.session_state.selected_lang}) ver. Başka bir dilde konuşma.
    Kullanıcıya kendi adıyla ({st.session_state.user_name}) hitap et.
    Tıp, akademik araştırmalar, anatomik illüstrasyonlar ve güvenilir kaynak taramalarında uzmanlaşmış bir laboratuvar asistanısın.
    """

    current_messages = load_chats_from_db(st.session_state.user_name, st.session_state.current_chat_id)

    # Geçmiş mesajları ekrana yazdır
    for i, msg in enumerate(current_messages):
        avatar = "🧠" if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            
            if msg["role"] == "assistant" and GTTS_AVAILABLE:
                try:
                    lang_code_map = {"Türkçe": "tr", "English": "en", "Español": "es", "Deutsch": "de", "Français": "fr", "العربية": "ar"}
                    tts_lang = lang_code_map.get(st.session_state.selected_lang, "tr")
                    
                    tts = gTTS(text=msg["content"], lang=tts_lang, slow=False)
                    audio_file = f"temp_{i}.mp3"
                    tts.save(audio_file)
                    with open(audio_file, "rb") as f:
                        st.audio(f.read(), format="audio/mp3")
                except Exception:
                    pass

                # 👍 / 👎 Geri Bildirim Butonları
                f_col1, f_col2, f_col3 = st.columns([1, 1, 10])
                if f_col1.button("👍", key=f"like_{i}"):
                    st.toast("Teşekkürler! Geri bildirimin kaydedildi. 🚀")
                if f_col2.button("👎", key=f"dislike_{i}"):
                    st.toast("Geri bildiriminiz alındı, kendimi geliştireceğim! 💡")

    # C. SOHBET GİRİŞ ALANI
    st.write("---")
    input_placeholders = {
        "Türkçe": f"Laboratuvara bir komut veya araştırma sorusu yaz, {st.session_state.user_name}...",
        "English": f"Type a command or research question into the lab, {st.session_state.user_name}...",
        "Español": f"Escribe un comando o pregunta de investigación en el laboratorio, {st.session_state.user_name}...",
        "Deutsch": f"Geben Sie einen Befehl oder eine Forschungsfrage ein, {st.session_state.user_name}...",
        "Français": f"Tapez une commande ou une question de recherche, {st.session_state.user_name}...",
        "العربية": f"اكتب أمراً أو سؤالاً بحثياً في المختبر يا {st.session_state.user_name}..."
    }
    current_placeholder = input_placeholders.get(st.session_state.selected_lang, input_placeholders["Türkçe"])

    prompt = st.chat_input(current_placeholder)

    if prompt:
        save_message_to_db(st.session_state.user_name, st.session_state.current_chat_id, "user", prompt)

        formatted_messages = [{"role": "system", "content": system_prompt}]
        for m in load_chats_from_db(st.session_state.user_name, st.session_state.current_chat_id):
            formatted_messages.append({"role": m["role"], "content": m["content"]})

        try:
            with st.spinner(t["spinner"]):
                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=formatted_messages,
                )
                bot_reply = response.choices[0].message.content

                save_message_to_db(st.session_state.user_name, st.session_state.current_chat_id, "assistant", bot_reply)
                st.rerun()

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")

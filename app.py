import streamlit as st
import urllib.request
import urllib.error
import json
import html

# ==================================================
# SAYFA AYARLARI
# ==================================================

st.set_page_config(
    page_title="Lidya AI 2.0",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# TASARIM
# ==================================================

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(
            circle at 50% 0%,
            #25204b 0%,
            #111326 45%,
            #090b16 100%
        );
    color: #f5f3ff;
}

h1, h2, h3 {
    color: #d8c9ff !important;
}

[data-testid="stSidebar"] {
    background: #111326;
    border-right: 1px solid #39315e;
}

.stButton button {
    border-radius: 12px;
    border: 1px solid #7464c9;
    background: #29234a;
    color: white;
}

.stButton button:hover {
    background: #493b80;
    border-color: #b6a5ff;
}

[data-testid="stChatMessage"] {
    border: 1px solid #343052;
    border-radius: 16px;
    padding: 12px;
    background: rgba(28, 27, 55, 0.65);
}

.lidya-orb {
    width: 145px;
    height: 145px;
    margin: 20px auto;
    border-radius: 50%;
    background:
        radial-gradient(
            circle at 35% 30%,
            #f0e7ff,
            #a78bfa 18%,
            #6366f1 45%,
            #312e81 70%,
            #111326 100%
        );
    box-shadow:
        0 0 25px #8b5cf6,
        0 0 65px #6366f1,
        inset 0 0 25px #ddd6fe;
    animation: pulse 3s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% {
        transform: scale(1);
        box-shadow:
            0 0 25px #8b5cf6,
            0 0 65px #6366f1;
    }
    50% {
        transform: scale(1.06);
        box-shadow:
            0 0 40px #c4b5fd,
            0 0 90px #6366f1;
    }
}

.lidya-title {
    text-align: center;
    font-size: 38px;
    font-weight: 800;
    letter-spacing: 2px;
    color: #ddd6fe;
    text-shadow: 0 0 20px #8b5cf6;
}

.lidya-subtitle {
    text-align: center;
    color: #c4b5fd;
    font-size: 14px;
}

div[data-testid="stChatInput"] {
    border-color: #7464c9;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# GEMINI AYARLARI
# ==================================================

API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# Bu model adını Google AI Studio'daki güncel
# model listenden doğrula.
MODEL_NAME = "gemini-2.5-flash"

API_URL = (
    "https://generativelanguage.googleapis.com/"
    f"v1beta/models/{MODEL_NAME}:generateContent"
)


# ==================================================
# DİLLER
# ==================================================

LANGUAGES = {
    "🇹🇷 Türkçe": "Turkish",
    "🇬🇧 English": "English",
    "🇩🇪 Deutsch": "German",
    "🇫🇷 Français": "French",
    "🇪🇸 Español": "Spanish",
    "🇮🇹 Italiano": "Italian",
    "🇯🇵 日本語": "Japanese",
    "🇰🇷 한국어": "Korean",
    "🇸🇦 العربية": "Arabic",
    "🇷🇺 Русский": "Russian",
    "🇨🇳 中文": "Chinese",
    "🇵🇹 Português": "Portuguese",
    "🇮🇳 हिन्दी": "Hindi",
}


# ==================================================
# OTURUM DURUMU
# ==================================================

if "user_name" not in st.session_state:
    st.session_state.user_name = "Misafir"

if "all_chats" not in st.session_state:
    st.session_state.all_chats = {
        "sohbet_1": []
    }

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "sohbet_1"

if "lidya_language" not in st.session_state:
    st.session_state.lidya_language = "Turkish"

if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = True

if "last_reply" not in st.session_state:
    st.session_state.last_reply = ""

if "last_error" not in st.session_state:
    st.session_state.last_error = ""

if st.session_state.current_chat_id not in st.session_state.all_chats:
    st.session_state.all_chats[st.session_state.current_chat_id] = []


# ==================================================
# GEMINI FONKSİYONU
# ==================================================

def gemini_cevapla(messages):

    contents = []

    for message in messages:

        contents.append({
            "role": (
                "user"
                if message["role"] == "user"
                else "model"
            ),
            "parts": [
                {"text": message["content"]}
            ]
        })

    payload = {
        "system_instruction": {
            "parts": [{
                "text": (
                    "Sen Lidya adında yardımsever, "
                    "nazik ve güvenilir bir yapay zekâsın. "
                    "Kullanıcıya doğal ve anlaşılır yanıtlar ver. "
                    f"Yanıt dilin: {st.session_state.lidya_language}. "
                    "Kullanıcı farklı bir dilde yanıt isterse "
                    "bu isteğe uygun davran. "
                    "Kullanıcıya Lidya olarak hitap edebilirsin."
                )
            }]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048
        }
    }

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": API_KEY
        },
        method="POST"
    )

    with urllib.request.urlopen(
        request,
        timeout=60
    ) as response:

        result = json.loads(
            response.read().decode("utf-8")
        )

    candidates = result.get("candidates", [])

    if not candidates:
        raise ValueError(
            "Gemini yanıt oluşturamadı. "
            "Modeli ve API ayarlarını kontrol et."
        )

    parts = candidates[0].get(
        "content", {}
    ).get("parts", [])

    answer = "\n".join(
        part["text"]
        for part in parts
        if "text" in part
    )

    if not answer:
        raise ValueError("Boş yanıt alındı.")

    return answer


# ==================================================
# SESLİ YANIT
# ==================================================

def sesli_yanit(text, language):

    # Metni JavaScript içine güvenli biçimde aktar.
    safe_text = json.dumps(text, ensure_ascii=False)
    safe_language = json.dumps(language)

    component = f"""
    <div style="
        font-family: sans-serif;
        text-align: center;
        padding: 5px;
        color: #ddd6fe;
    ">
        <button id="speakBtn" style="
            background: linear-gradient(135deg,#6d5bd0,#4338ca);
            border: 1px solid #a78bfa;
            border-radius: 12px;
            padding: 10px 18px;
            color: white;
            font-size: 15px;
            cursor: pointer;
        ">🔊 Lidya'yı Dinle</button>

        <button id="stopBtn" style="
            background: #272445;
            border: 1px solid #7464c9;
            border-radius: 12px;
            padding: 10px 18px;
            color: white;
            font-size: 15px;
            cursor: pointer;
        ">⏹ Durdur</button>

        <p id="voiceStatus" style="font-size:12px">
            Sesli yanıt için düğmeye bas.
        </p>
    </div>

    <script>
    const text = {safe_text};
    const language = {safe_language};

    const speakBtn = document.getElementById("speakBtn");
    const stopBtn = document.getElementById("stopBtn");
    const status = document.getElementById("voiceStatus");

    speakBtn.onclick = () => {{
        if (!("speechSynthesis" in window)) {{
            status.textContent =
                "Bu tarayıcı sesli okumayı desteklemiyor.";
            return;
        }}

        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = language;
        utterance.rate = 1;
        utterance.pitch = 1;

        utterance.onstart = () => {{
            status.textContent = "Lidya konuşuyor...";
        }};

        utterance.onend = () => {{
            status.textContent = "Konuşma tamamlandı.";
        }};

        utterance.onerror = () => {{
            status.textContent =
                "Ses oluşturulamadı. Tarayıcını kontrol et.";
        }};

        window.speechSynthesis.speak(utterance);
    }};

    stopBtn.onclick = () => {{
        if ("speechSynthesis" in window) {{
            window.speechSynthesis.cancel();
            status.textContent = "Konuşma durduruldu.";
        }}
    }};
    </script>
    """

    st.components.v1.html(
        component,
        height=110
    )


# ==================================================
# YAN MENÜ
# ==================================================

with st.sidebar:

    st.markdown("## ⚙️ Lidya Ayarları")

    new_name = st.text_input(
        "İsminiz",
        value=st.session_state.user_name,
        max_chars=50
    )

    st.session_state.user_name = new_name

    selected_language = st.selectbox(
        "🌍 Konuşma dili",
        list(LANGUAGES.keys()),
        index=list(LANGUAGES.values()).index(
            st.session_state.lidya_language
        )
    )

    st.session_state.lidya_language = LANGUAGES[
        selected_language
    ]

    st.session_state.voice_enabled = st.toggle(
        "🔊 Sesli yanıt özelliği",
        value=st.session_state.voice_enabled
    )

    st.divider()

    if st.button(
        "➕ Yeni Sohbet",
        use_container_width=True
    ):

        number = 1

        while f"sohbet_{number}" in st.session_state.all_chats:
            number += 1

        new_id = f"sohbet_{number}"

        st.session_state.all_chats[new_id] = []
        st.session_state.current_chat_id = new_id
        st.session_state.last_reply = ""
        st.rerun()

    if st.button(
        "🗑 Bu Sohbeti Temizle",
        use_container_width=True
    ):

        st.session_state.all_chats[
            st.session_state.current_chat_id
        ] = []

        st.session_state.last_reply = ""
        st.rerun()

    st.divider()
    st.markdown("### 💬 Sohbet Geçmişi")

    for chat_id in list(st.session_state.all_chats.keys()):

        number = chat_id.replace("sohbet_", "")

        if st.button(
            f"💭 Sohbet {number}",
            key=f"chat_{chat_id}",
            use_container_width=True
        ):

            st.session_state.current_chat_id = chat_id
            st.session_state.last_reply = ""
            st.rerun()


# ==================================================
# ANA EKRAN
# ==================================================

st.markdown(
    '<div class="lidya-title">LIDYA AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="lidya-subtitle">'
    '✨ Kişisel yapay zekâ asistanın ✨'
    '</div>',
    unsafe_allow_html=True
)

# Animasyonlu hologram
st.markdown(
    '<div class="lidya-orb"></div>',
    unsafe_allow_html=True
)

st.markdown(
    f"### Merhaba, {html.escape(st.session_state.user_name)}! 💜"
)

st.write(
    "Ben Lidya. Seninle konuşmaya hazırım."
)

st.caption(
    "🌍 Dil: " + st.session_state.lidya_language
)


# ==================================================
# API KONTROLÜ
# ==================================================

if not API_KEY:

    st.error(
        "GEMINI_API_KEY bulunamadı. "
        "Streamlit Cloud Secrets ayarını kontrol et."
    )

    st.stop()


# ==================================================
# MESAJLARI GÖSTER
# ==================================================

current_chat_id = st.session_state.current_chat_id

current_messages = st.session_state.all_chats[
    current_chat_id
]

for message in current_messages:

    avatar = (
        "🧠"
        if message["role"] == "assistant"
        else "🙂"
    )

    with st.chat_message(
        message["role"],
        avatar=avatar
    ):

        st.markdown(message["content"])


# ==================================================
# SESLİ SON YANIT
# ==================================================

if (
    st.session_state.voice_enabled
    and st.session_state.last_reply
):

    sesli_yanit(
        st.session_state.last_reply,
        st.session_state.lidya_language
    )


# ==================================================
# MESAJ GÖNDERME
# ==================================================

prompt = st.chat_input(
    f"Lidya'ya mesaj yaz, {st.session_state.user_name}..."
)

if prompt:

    current_messages.append({
        "role": "user",
        "content": prompt
    })

    try:

        with st.spinner("Lidya düşünüyor... ✨"):

            reply = gemini_cevapla(
                current_messages
            )

        current_messages.append({
            "role": "assistant",
            "content": reply
        })

        st.session_state.all_chats[
            current_chat_id
        ] = current_messages

        st.session_state.last_reply = reply
        st.rerun()

    except urllib.error.HTTPError as error:

        details = error.read().decode(
            "utf-8",
            errors="replace"
        )

        try:
            data = json.loads(details)
            message = data.get(
                "error", {}
            ).get("message", details)
        except json.JSONDecodeError:
            message = details

        current_messages.pop()

        st.error(
            f"Gemini API hatası: HTTP {error.code}"
        )

        st.warning(message)

    except urllib.error.URLError as error:

        current_messages.pop()

        st.error(
            f"Bağlantı hatası: {error.reason}"
        )

    except Exception as error:

        current_messages.pop()

        st.error(
            f"Beklenmeyen hata: {error}"
        )


# ==================================================
# ALT BİLGİ
# ==================================================

st.divider()

st.markdown(
    "<div style='text-align:center;color:#a5a0ca'>"
    "💜 Lidya AI 2.0 · Senin dijital asistanın"
    "</div>",
    unsafe_allow_html=True
        )

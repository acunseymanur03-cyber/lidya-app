import os
import json
import urllib.request
import urllib.error

import streamlit as st
import streamlit.components.v1 as components


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Lidya AI",
    page_icon="💜",
    layout="wide",
)


# --------------------------------------------------
# GEMINI CONFIG
# --------------------------------------------------

API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# Hata mesajının önerdiği model
MODEL_NAME = "gemini-3.8-flash"

API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/interactions"
)


# --------------------------------------------------
# PAGE STYLE
# --------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(
                circle at top,
                #30204f 0%,
                #141326 45%,
                #090914 100%
            );
        color: white;
    }

    h1, h2, h3, p, label {
        color: #f4efff !important;
    }

    .hero {
        text-align: center;
        padding: 25px 10px 5px 10px;
    }

    .hero-title {
        font-size: 52px;
        font-weight: 800;
        letter-spacing: 3px;
        background: linear-gradient(
            90deg,
            #f6d7ff,
            #bb9aff,
            #83e8ff
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle {
        color: #d3c8f5;
        font-size: 17px;
    }

    .orb {
        width: 150px;
        height: 150px;
        margin: 25px auto;
        border-radius: 50%;
        background: radial-gradient(
            circle at 30% 25%,
            #ffffff,
            #d5a8ff 15%,
            #8c54ed 40%,
            #402078 70%,
            #161126 100%
        );
        box-shadow:
            0 0 25px #b77cff,
            0 0 60px #8255ff,
            inset -10px -10px 25px #24103f;
        animation: float 3s ease-in-out infinite,
                   glow 2s ease-in-out infinite alternate;
    }

    @keyframes float {
        0%, 100% {
            transform: translateY(0px) rotate(0deg);
        }
        50% {
            transform: translateY(-12px) rotate(5deg);
        }
    }

    @keyframes glow {
        from {
            box-shadow: 0 0 25px #b77cff,
                        0 0 45px #8255ff;
        }
        to {
            box-shadow: 0 0 35px #d5a8ff,
                        0 0 80px #8255ff;
        }
    }

    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(200, 170, 255, 0.18);
        border-radius: 16px;
        padding: 12px;
    }

    .stButton button {
        border-radius: 12px;
        border: 1px solid #a984ff;
        background: linear-gradient(
            90deg,
            #6840ad,
            #8c54ed
        );
        color: white;
    }

    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# LANGUAGE
# --------------------------------------------------

LANGUAGES = {
    "Türkçe": "Turkish",
    "English": "English",
    "Français": "French",
    "Deutsch": "German",
    "Español": "Spanish",
    "Italiano": "Italian",
    "日本語": "Japanese",
}

with st.sidebar:
    st.title("⚙️ Settings")

    selected_language = st.selectbox(
        "🌍 Response language",
        list(LANGUAGES.keys()),
        index=0,
    )

    voice_enabled = st.checkbox(
        "🔊 Read responses aloud",
        value=False,
    )

    st.divider()

    st.caption("Lidya AI")
    st.caption("Created with Python and Streamlit.")

    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.rerun()


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">LIDYA AI</div>
        <div class="subtitle">
            Your intelligent companion for ideas, learning and creativity.
        </div>
        <div class="orb"></div>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------
# GEMINI INTERACTIONS API
# --------------------------------------------------

def ask_lidya(messages, language):
    """
    Send the conversation to Gemini's Interactions API.
    Returns the model's text response.
    """

    if not API_KEY:
        return (
            "API anahtarı bulunamadı. Streamlit Cloud'da "
            "Settings → Secrets bölümüne GEMINI_API_KEY ekle."
        )

    conversation = []

    for message in messages:
        role = message["role"]

        if role == "assistant":
            role = "model"

        conversation.append(
            {
                "role": role,
                "content": message["content"],
            }
        )

    payload = {
        "model": MODEL_NAME,
        "input": conversation,
        "system_instruction": (
            "You are Lidya AI, a friendly, thoughtful and helpful "
            "AI assistant. Give accurate answers, explain concepts "
            "clearly, and be honest when you are uncertain. "
            f"Respond in {language}, unless the user asks for "
            "another language. Do not claim to have capabilities "
            "you do not have."
        ),
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": API_KEY,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=60,
        ) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

        # Extract text from the Interactions API response.
        if result.get("output_text"):
            return result["output_text"]

        output = result.get("output", [])

        text_parts = []

        for item in output:
            if not isinstance(item, dict):
                continue

            if item.get("type") == "text":
                text_parts.append(item.get("text", ""))

            for content_item in item.get("content", []):
                if (
                    isinstance(content_item, dict)
                    and content_item.get("type") == "text"
                ):
                    text_parts.append(
                        content_item.get("text", "")
                    )

        answer = "\n".join(
            part for part in text_parts if part
        )

        if answer:
            return answer

        return (
            "Modelden yanıt geldi ancak metin içeriği "
            "beklenen biçimde bulunamadı. API yanıtını kontrol et."
        )

    except urllib.error.HTTPError as error:
        details = error.read().decode(
            "utf-8",
            errors="replace",
        )

        return (
            f"Gemini API hatası (HTTP {error.code}).\n\n"
            f"{details[:1500]}"
        )

    except urllib.error.URLError as error:
        return (
            "Bağlantı hatası oluştu. İnternet bağlantısını "
            f"ve API erişimini kontrol et.\n\n{error}"
        )

    except Exception as error:
        return f"Beklenmeyen bir hata oluştu: {error}"


# --------------------------------------------------
# CHAT HISTORY
# --------------------------------------------------

for message in st.session_state.messages:
    avatar = "🧑‍💻" if message["role"] == "user" else "💜"

    with st.chat_message(
        message["role"],
        avatar=avatar,
    ):
        st.markdown(message["content"])


# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

user_prompt = st.chat_input(
    "Ask Lidya anything..."
)

if user_prompt:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_prompt,
        }
    )

    with st.chat_message(
        "user",
        avatar="🧑‍💻",
    ):
        st.markdown(user_prompt)

    with st.chat_message(
        "assistant",
        avatar="💜",
    ):
        with st.spinner("Lidya is thinking..."):
            answer = ask_lidya(
                st.session_state.messages,
                LANGUAGES[selected_language],
            )

        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    st.rerun()


# --------------------------------------------------
# TEXT-TO-SPEECH
# --------------------------------------------------

if voice_enabled and st.session_state.messages:
    last_message = st.session_state.messages[-1]

    if last_message["role"] == "assistant":
        speech_text = json.dumps(
            last_message["content"],
            ensure_ascii=False,
        )

        speech_language = {
            "Türkçe": "tr-TR",
            "English": "en-US",
            "Français": "fr-FR",
            "Deutsch": "de-DE",
            "Español": "es-ES",
            "Italiano": "it-IT",
            "日本語": "ja-JP",
        }[selected_language]

        components.html(
            f"""
            <script>
            const text = {speech_text};
            const language = "{speech_language}";

            if ("speechSynthesis" in window) {{
                window.speechSynthesis.cancel();

                const utterance =
                    new SpeechSynthesisUtterance(text);

                utterance.lang = language;
                utterance.rate = 1.0;
                utterance.pitch = 1.05;

                window.speechSynthesis.speak(utterance);
            }}
            </script>
            """,
            height=0,
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    """
    <div style="
        text-align:center;
        color:#b9a9dc;
        padding:30px 0 10px 0;
        font-size:13px;
    ">
        💜 Lidya AI · Built with curiosity and Python
    </div>
    """,
    unsafe_allow_html=True,
)

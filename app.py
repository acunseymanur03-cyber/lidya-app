import streamlit as st
import urllib.request
import urllib.error
import json

# -----------------------------------------
# SAYFA AYARLARI
# -----------------------------------------

st.set_page_config(
    page_title="Lidya - AI Assistant",
    page_icon="🧠",
    layout="centered"
)

# -----------------------------------------
# API AYARLARI
# -----------------------------------------

API_KEY = st.secrets.get("GEMINI_API_KEY", "")

MODEL_NAME = "gemini-3.8-flash"

API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/{MODEL_NAME}:generateContent"
)

# -----------------------------------------
# OTURUM AYARLARI
# -----------------------------------------

if "user_name" not in st.session_state:
    st.session_state.user_name = "Misafir"

if "all_chats" not in st.session_state:
    st.session_state.all_chats = {
        "sohbet_1": []
    }

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "sohbet_1"

if (
    st.session_state.current_chat_id
    not in st.session_state.all_chats
):
    st.session_state.current_chat_id = "sohbet_1"

# -----------------------------------------
# GEMINI API FONKSİYONU
# -----------------------------------------

def gemini_cevapla(messages):

    contents = []

    for msg in messages:
        contents.append({
            "role": (
                "user"
                if msg["role"] == "user"
                else "model"
            ),
            "parts": [
                {"text": msg["content"]}
            ]
        })

    payload = {
        "system_instruction": {
            "parts": [
                {
                    "text": (
                        "Sen Lidya adında yardımsever, "
                        "nazik ve güvenilir bir yapay zekâ "
                        "asistanısın. Kullanıcıya Türkçe "
                        "yanıt ver. Açık, anlaşılır ve "
                        "yararlı olmaya çalış."
                    )
                }
            ]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048
        }
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": API_KEY
        },
        method="POST"
    )

    with urllib.request.urlopen(
        req,
        timeout=60
    ) as response:

        data = json.loads(
            response.read().decode("utf-8")
        )

    candidates = data.get("candidates", [])

    if not candidates:
        raise ValueError(
            "Gemini yanıt oluşturamadı. "
            "İstek veya güvenlik nedeniyle "
            "yanıt üretilmemiş olabilir."
        )

    parts = candidates[0].get(
        "content", {}
    ).get("parts", [])

    cevap = "\n".join(
        part["text"]
        for part in parts
        if "text" in part
    )

    if not cevap:
        raise ValueError(
            "Gemini boş bir yanıt döndürdü."
        )

    return cevap


# -----------------------------------------
# YAN MENÜ
# -----------------------------------------

with st.sidebar:

    st.markdown("## ⚙️ Ayarlar & Yönetim")

    yeni_isim = st.text_input(
        "İsminiz:",
        value=st.session_state.user_name,
        max_chars=50
    )

    if yeni_isim != st.session_state.user_name:
        st.session_state.user_name = yeni_isim
        st.rerun()

    st.write("---")

    if st.button(
        "➕ Yeni Sohbet Oluştur",
        use_container_width=True
    ):

        yeni_numara = 1

        while (
            f"sohbet_{yeni_numara}"
            in st.session_state.all_chats
        ):
            yeni_numara += 1

        yeni_id = f"sohbet_{yeni_numara}"

        st.session_state.all_chats[yeni_id] = []
        st.session_state.current_chat_id = yeni_id

        st.rerun()

    if st.button(
        "🗑 Geçmişi Temizle",
        use_container_width=True
    ):

        st.session_state.all_chats[
            st.session_state.current_chat_id
        ] = []

        st.rerun()

    st.write("---")
    st.markdown("### 💬 Sohbetler")

    for chat_id in list(
        st.session_state.all_chats.keys()
    ):

        sohbet_no = chat_id.replace(
            "sohbet_", ""
        )

        if st.button(
            f"💭 Sohbet {sohbet_no}",
            key=f"sec_{chat_id}",
            use_container_width=True
        ):

            st.session_state.current_chat_id = chat_id
            st.rerun()


# -----------------------------------------
# ANA EKRAN
# -----------------------------------------

st.title("🧠 Lidya - Yapay Zekâ Asistanı")

st.markdown(
    f"Hoş geldin **{st.session_state.user_name}**! "
    "Ben Lidya. Sana yardımcı olmak için buradayım. 🧠✨"
)

st.caption("Sorularını yaz, birlikte çözelim!")

# -----------------------------------------
# API ANAHTARI KONTROLÜ
# -----------------------------------------

if not API_KEY:

    st.error(
        "GEMINI_API_KEY bulunamadı! "
        "Streamlit Cloud ayarlarındaki "
        "Secrets bölümüne API anahtarını eklemelisin."
    )

    st.stop()


# -----------------------------------------
# AKTİF SOHBET
# -----------------------------------------

current_chat_id = st.session_state.current_chat_id

current_messages = st.session_state.all_chats[
    current_chat_id
]

# Önceki mesajları göster

for msg in current_messages:

    avatar = (
        "🧠"
        if msg["role"] == "assistant"
        else "🙂"
    )

    with st.chat_message(
        msg["role"],
        avatar=avatar
    ):

        st.markdown(msg["content"])


# -----------------------------------------
# MESAJ GÖNDERME
# -----------------------------------------

prompt = st.chat_input(
    f"Mesajını yaz, {st.session_state.user_name}..."
)

if prompt:

    current_messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message(
        "user",
        avatar="🙂"
    ):

        st.markdown(prompt)

    try:

        with st.chat_message(
            "assistant",
            avatar="🧠"
        ):

            with st.spinner("Lidya düşünüyor... ✨"):

                bot_reply = gemini_cevapla(
                    current_messages
                )

            st.markdown(bot_reply)

        current_messages.append({
            "role": "assistant",
            "content": bot_reply
        })

        st.session_state.all_chats[
            current_chat_id
        ] = current_messages

    except urllib.error.HTTPError as e:

        hata_detayi = e.read().decode(
            "utf-8",
            errors="replace"
        )

        st.error(
            f"Gemini API hatası: HTTP {e.code}"
        )

        try:
            hata_json = json.loads(hata_detayi)
            hata_mesaji = hata_json.get(
                "error", {}
            ).get("message", hata_detayi)
        except json.JSONDecodeError:
            hata_mesaji = hata_detayi

        st.warning(
            f"Google API açıklaması: {hata_mesaji}"
        )

        # Başarısız kullanıcı mesajını geri al.
        current_messages.pop()

    except urllib.error.URLError as e:

        st.error(
            "İnternet bağlantısı kurulamadı: "
            f"{e.reason}"
        )

        current_messages.pop()

    except Exception as e:

        st.error(
            f"Beklenmeyen bir hata oluştu: {e}"
        )

        current_messages.pop()

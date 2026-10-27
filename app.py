import os
import io
import json
import html
import base64
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st
import requests
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None


# ---------------------------------------------------------
# AYARLAR
# ---------------------------------------------------------

st.set_page_config(
    page_title="Lidya AI",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_NAME = "Lidya AI"
MODEL_NAME = "openai/gpt-oss-20b"
TZ = ZoneInfo("Europe/Istanbul")

GROQ_API_KEY = (
    st.secrets.get("GROQ_API_KEY", "")
    if hasattr(st, "secrets")
    else ""
) or os.getenv("GROQ_API_KEY", "")

CF_ACCOUNT_ID = (
    st.secrets.get("CLOUDFLARE_ACCOUNT_ID", "")
    if hasattr(st, "secrets")
    else ""
) or os.getenv("CLOUDFLARE_ACCOUNT_ID", "")

CF_API_TOKEN = (
    st.secrets.get("CLOUDFLARE_API_TOKEN", "")
    if hasattr(st, "secrets")
    else ""
) or os.getenv("CLOUDFLARE_API_TOKEN", "")


# ---------------------------------------------------------
# TASARIM
# ---------------------------------------------------------

st.markdown("""
<style>
    :root {
        --purple: #a78bfa;
        --dark: #100c1c;
        --panel: #1b1530;
        --border: rgba(190,160,255,.19);
    }

    .stApp {
        background:
            radial-gradient(ellipse at top, #25163e 0%, #100c1c 48%);
        color: #f6f1ff;
    }

    section[data-testid="stSidebar"] {
        background: #120d20;
        border-right: 1px solid var(--border);
    }

    h1, h2, h3 {
        color: #f6f0ff !important;
    }

    .lidya-hero {
        padding: 34px 20px 28px 20px;
        border: 1px solid var(--border);
        border-radius: 24px;
        background: linear-gradient(135deg,
            rgba(124,58,237,.20),
            rgba(30,20,48,.70));
        text-align: center;
        margin-bottom: 22px;
    }

    .lidya-title {
        font-size: clamp(32px, 5vw, 52px);
        font-weight: 800;
        letter-spacing: -1.5px;
        margin-bottom: 8px;
    }

    .lidya-subtitle {
        color: #d7c9f8;
        font-size: 17px;
    }

    .lidya-card {
        border: 1px solid var(--border);
        background: rgba(28,21,47,.8);
        border-radius: 16px;
        padding: 18px;
        margin: 8px 0;
    }

    .small-muted {
        color: #b9abcF;
        font-size: 13px;
    }

    .university-card {
        border: 1px solid var(--border);
        border-radius: 17px;
        background: rgba(27,21,45,.85);
        padding: 16px;
        min-height: 155px;
        margin-bottom: 12px;
    }

    .stButton > button {
        border-radius: 11px;
        border: 1px solid var(--border);
    }

    [data-testid="stChatMessage"] {
        border: 1px solid rgba(190,160,255,.10);
        border-radius: 14px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# ÇEVİRİLER
# ---------------------------------------------------------

LANGUAGES = {
    "Türkçe": "tr",
    "English": "en",
    "Français": "fr",
    "Deutsch": "de",
    "Español": "es",
    "Italiano": "it",
    "日本語": "ja",
    "العربية": "ar",
    "简体中文": "zh",
}

UI = {
    "tr": {
        "home": "Ana sayfa", "chat": "Lidya ile Sohbet",
        "file": "Dosya Laboratuvarı", "medical": "Tıp ve Anatomi",
        "legal": "Hukuk Araştırmaları", "language": "Dil Öğretmeni",
        "coding": "Yazılım Mühendisliği", "science": "Bilim ve Araştırma",
        "math": "Matematik", "engineering": "Mühendislik",
        "education": "Eğitim", "business": "İşletme ve Ekonomi",
        "writing": "Yazma ve Yaratıcılık", "data": "Veri Analizi",
        "cyber": "Siber Güvenlik", "devices": "Akıllı Cihazlar",
        "image": "Görsel Atölyesi", "video": "Video Atölyesi",
        "sim": "Simülasyon Laboratuvarı", "history": "Tarih",
        "universities": "Üniversite Keşfi", "karaoke": "Ses ve Karaoke",
        "memory": "Lidya Hafızası", "settings": "Ayarlar",
        "send": "Mesajını yaz...", "upload": "Dosya ekle",
        "analyze": "Dosyayı analiz et", "clear": "Sohbeti temizle",
        "remember": "Hatırla:", "show_memory": "Hafızayı göster",
        "clear_memory": "Hafızayı temizle", "prompt": "İsteğini yaz",
        "generate": "Oluştur", "welcome": "Düşün. Öğren. Üret. Keşfet.",
    },
    "en": {
        "home": "Home", "chat": "Chat with Lidya",
        "file": "File Lab", "medical": "Medicine & Anatomy",
        "legal": "Legal Research", "language": "Language Teacher",
        "coding": "Software Engineering", "science": "Science & Research",
        "math": "Mathematics", "engineering": "Engineering",
        "education": "Education", "business": "Business & Economics",
        "writing": "Writing & Creativity", "data": "Data Analysis",
        "cyber": "Cybersecurity", "devices": "Smart Devices",
        "image": "Image Studio", "video": "Video Studio",
        "sim": "Simulation Lab", "history": "History",
        "universities": "University Explorer", "karaoke": "Audio & Karaoke",
        "memory": "Lidya Memory", "settings": "Settings",
        "send": "Write your message...", "upload": "Attach a file",
        "analyze": "Analyze file", "clear": "Clear chat",
        "remember": "Remember:", "show_memory": "Show memory",
        "clear_memory": "Clear memory", "prompt": "Write your request",
        "generate": "Generate", "welcome": "Think. Learn. Create. Explore.",
    },
}

UI["fr"] = dict(UI["en"], home="Accueil", chat="Discuter avec Lidya",
    file="Laboratoire de fichiers", medical="Médecine et anatomie",
    math="Mathématiques", history="Histoire", universities="Découvrir les universités",
    karaoke="Audio et karaoké", welcome="Réfléchir. Apprendre. Créer. Explorer.")
UI["de"] = dict(UI["en"], home="Startseite", chat="Mit Lidya chatten",
    file="Datei-Labor", medical="Medizin und Anatomie", math="Mathematik",
    history="Geschichte", universities="Universitäten entdecken",
    karaoke="Audio und Karaoke", welcome="Denken. Lernen. Gestalten. Entdecken.")
UI["es"] = dict(UI["en"], home="Inicio", chat="Hablar con Lidya",
    file="Laboratorio de archivos", medical="Medicina y anatomía",
    math="Matemáticas", history="Historia", universities="Explorar universidades",
    karaoke="Audio y karaoke", welcome="Pensar. Aprender. Crear. Explorar.")
UI["it"] = dict(UI["en"], home="Home", chat="Chatta con Lidya",
    file="Laboratorio file", medical="Medicina e anatomia", math="Matematica",
    history="Storia", universities="Esplora università",
    karaoke="Audio e karaoke", welcome="Pensa. Impara. Crea. Esplora.")
UI["ja"] = dict(UI["en"], home="ホーム", chat="Lidyaとチャット",
    file="ファイルラボ", medical="医学と解剖学", math="数学",
    history="歴史", universities="大学を探す", karaoke="音声とカラオケ",
    welcome="考える。学ぶ。創る。探求する。")
UI["ar"] = dict(UI["en"], home="الرئيسية", chat="الدردشة مع ليديا",
    file="مختبر الملفات", medical="الطب والتشريح", math="الرياضيات",
    history="التاريخ", universities="استكشاف الجامعات",
    karaoke="الصوت والكاريوكي", welcome="فكّر. تعلّم. ابتكر. اكتشف.")
UI["zh"] = dict(UI["en"], home="主页", chat="与 Lidya 聊天",
    file="文件实验室", medical="医学与解剖学", math="数学",
    history="历史", universities="探索大学", karaoke="音频与卡拉OK",
    welcome="思考。学习。创造。探索。")


# ---------------------------------------------------------
# MODÜLLER
# ---------------------------------------------------------

MODULE_KEYS = [
    "home", "chat", "file", "medical", "legal", "language", "coding",
    "science", "math", "engineering", "education", "business", "writing",
    "data", "cyber", "devices", "image", "video", "sim", "history",
    "universities", "karaoke", "memory", "settings"
]

SPECIALIST_PROMPTS = {
    "medical": (
        "Tıp ve anatomi eğitim asistanısın. Anatomik yapıları bilimsel ve "
        "anlaşılır biçimde açıkla. Tanı koyma veya doktorun yerini aldığını "
        "iddia etme. Acil belirtilerde profesyonel sağlık yardımına yönlendir."
    ),
    "legal": (
        "Hukuk araştırma asistanısın. Genel hukuki kavramları açıkla; "
        "ülke ve tarih farklarını belirt. Avukat gibi kesin kişisel hukuki "
        "tavsiye verme. Gerektiğinde resmî kaynak doğrulaması öner."
    ),
    "language": "Dil öğretmenisin. Seviyeye uygun açıklama, örnek ve alıştırmalar sun.",
    "coding": "Yazılım mühendisliği asistanısın. Çalışan, güvenli ve açıklamalı kod yaz.",
    "science": "Bilimsel araştırma asistanısın. Kanıtı, varsayımı ve belirsizliği ayır.",
    "math": "Matematik öğretmenisin. Çözümleri adım adım ve kontrol ederek anlat.",
    "engineering": "Mühendislik asistanısın. Varsayımları, birimleri ve güvenlik sınırlarını belirt.",
    "education": "Öğrenme koçusun. Konuları basitten karmaşığa öğret ve mini alıştırmalar sun.",
    "business": "İşletme ve ekonomi asistanısın. Varsayımları açıkla, kesin finansal sonuç vaat etme.",
    "writing": "Yazma ve yaratıcılık asistanısın. Özgün taslaklar, düzenleme ve geri bildirim sun.",
    "data": "Veri analizi asistanısın. Verinin sınırlarını belirt ve uygun analiz öner.",
    "cyber": "Siber güvenlik asistanısın. Savunma, güvenli kodlama ve izinli testlere odaklan.",
    "devices": "Akıllı cihazlar ve IoT asistanısın. Güvenli ve uygulanabilir açıklamalar ver.",
    "history": (
        "Tarih öğretmenisin. Olayları kronoloji, nedenler, sonuçlar ve farklı "
        "tarihçilerin yorumlarıyla açıkla. Belirsiz bilgileri kesinmiş gibi sunma."
    ),
    "chat": "Yardımsever, doğru ve açık bir genel amaçlı yapay zekâ asistanısın.",
}

MODULE_CONTEXT = {
    "medical": "Tıp ve Anatomi",
    "legal": "Hukuk Araştırmaları",
    "language": "Dil Öğretmeni",
    "coding": "Yazılım Mühendisliği",
    "science": "Bilim ve Araştırma",
    "math": "Matematik",
    "engineering": "Mühendislik",
    "education": "Eğitim",
    "business": "İşletme ve Ekonomi",
    "writing": "Yazma ve Yaratıcılık",
    "data": "Veri Analizi",
    "cyber": "Siber Güvenlik",
    "devices": "Akıllı Cihazlar",
    "history": "Tarih",
    "chat": "Genel Sohbet",
}

UNIVERSITIES = [
    {
        "name": "Harvard University",
        "domain": "harvard.edu",
        "site": "https://www.harvard.edu/",
        "admissions": "https://college.harvard.edu/admissions",
        "about": "https://college.harvard.edu/",
    },
    {
        "name": "University of Oxford",
        "domain": "ox.ac.uk",
        "site": "https://www.ox.ac.uk/",
        "admissions": "https://www.ox.ac.uk/admissions/undergraduate",
        "about": "https://www.ox.ac.uk/admissions/undergraduate",
    },
    {
        "name": "University of Cambridge",
        "domain": "cam.ac.uk",
        "site": "https://www.cam.ac.uk/",
        "admissions": "https://www.undergraduate.study.cam.ac.uk/",
        "about": "https://www.undergraduate.study.cam.ac.uk/",
    },
    {
        "name": "Massachusetts Institute of Technology",
        "domain": "mit.edu",
        "site": "https://www.mit.edu/",
        "admissions": "https://mitadmissions.org/",
        "about": "https://mitadmissions.org/",
    },
    {
        "name": "Yale University",
        "domain": "yale.edu",
        "site": "https://www.yale.edu/",
        "admissions": "https://admissions.yale.edu/",
        "about": "https://admissions.yale.edu/",
    },
    {
        "name": "Columbia University",
        "domain": "columbia.edu",
        "site": "https://www.columbia.edu/",
        "admissions": "https://undergrad.admissions.columbia.edu/",
        "about": "https://undergrad.admissions.columbia.edu/",
    },
    {
        "name": "Princeton University",
        "domain": "princeton.edu",
        "site": "https://www.princeton.edu/",
        "admissions": "https://admission.princeton.edu/",
        "about": "https://admission.princeton.edu/",
    },
    {
        "name": "Stanford University",
        "domain": "stanford.edu",
        "site": "https://www.stanford.edu/",
        "admissions": "https://admission.stanford.edu/",
        "about": "https://admission.stanford.edu/",
    },
]


# ---------------------------------------------------------
# OTURUM DURUMU
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "memory_items" not in st.session_state:
    st.session_state.memory_items = []

if "last_uploaded_text" not in st.session_state:
    st.session_state.last_uploaded_text = ""

if "last_uploaded_name" not in st.session_state:
    st.session_state.last_uploaded_name = ""

if "language" not in st.session_state:
    st.session_state.language = "Türkçe"

if "module" not in st.session_state:
    st.session_state.module = "home"


def tr_now():
    return datetime.now(TZ).strftime("%d.%m.%Y %H:%M:%S")


def ui(key):
    code = LANGUAGES.get(st.session_state.language, "tr")
    return UI.get(code, UI["en"]).get(key, UI["en"].get(key, key))


def safe_get_secret(name):
    try:
        return st.secrets.get(name, "")
    except Exception:
        return ""


def groq_client():
    key = safe_get_secret("GROQ_API_KEY") or os.getenv("GROQ_API_KEY", "")
    if not key or Groq is None:
        return None
    return Groq(api_key=key)


def ask_lidya(prompt, module="chat", history=None, file_context=""):
    client = groq_client()
    if client is None:
        return (
            "Lidya AI sohbeti için GROQ_API_KEY ayarlanmamış veya groq paketi "
            "kurulu değil. Streamlit Cloud → App settings → Secrets bölümüne "
            "GROQ_API_KEY ekleyip uygulamayı yeniden başlat."
        )

    system_prompt = (
        "Sen Lidya AI adlı eğitim ve üretkenlik asistanısın. "
        "Lidya AI projesini Şeymanur Acun geliştirmiştir. "
        "Temel dil modeli ve üçüncü taraf hizmetlerin geliştiricileri farklı "
        "olabilir; kendini bu modellerin yaratıcısı olarak tanıtma. "
        "Kullanıcının seçtiği dilde yanıt ver. Açık, yararlı ve dürüst ol. "
        "Gerçek zamanlı internet araştırması yaptığını, kaynak kontrol ettiğini "
        "veya bir dosyayı okuduğunu ancak gerçekten yaptıysan söyle. "
        "Tıbbi ve hukuki konularda sınırlarını açıkla. "
        "Seçili modül: " + MODULE_CONTEXT.get(module, module) + ". "
        + SPECIALIST_PROMPTS.get(module, SPECIALIST_PROMPTS["chat"])
    )

    if file_context:
        prompt = (
            "Kullanıcının eklediği dosyadan çıkarılan içerik aşağıdadır. "
            "Yanıtında yalnızca bu içeriği gerçekten destekleyen bilgileri "
            "dosyaya atfet; dosyanın dışındaki bilgileri ayrıca belirt.\n\n"
            "DOSYA: " + st.session_state.get("last_uploaded_name", "") +
            "\nDOSYA İÇERİĞİ:\n" + file_context[:18000] +
            "\n\nKULLANICININ İSTEĞİ:\n" + prompt
        )

    messages = [{"role": "system", "content": system_prompt}]

    for item in (history or [])[-12:]:
        if item.get("role") in ("user", "assistant"):
            messages.append({
                "role": item["role"],
                "content": item.get("content", "")[:6000],
            })

    messages.append({"role": "user", "content": prompt})

    try:
        result = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.6,
            max_tokens=1800,
        )
        return result.choices[0].message.content or "Yanıt üretilemedi."
    except Exception as exc:
        return f"Yanıt alınırken hata oluştu: {exc}"


# ---------------------------------------------------------
# DOSYA OKUMA
# ---------------------------------------------------------

def read_uploaded_file(uploaded):
    if uploaded is None:
        return ""

    name = uploaded.name.lower()
    data = uploaded.getvalue()

    try:
        if name.endswith(".pdf"):
            if PdfReader is None:
                return "PDF okumak için pypdf paketini requirements.txt dosyasına ekle."
            reader = PdfReader(io.BytesIO(data))
            pages = []
            for page in reader.pages[:60]:
                pages.append(page.extract_text() or "")
            return "\n".join(pages)[:25000]

        if name.endswith(".docx"):
            if Document is None:
                return "Word okumak için python-docx paketini requirements.txt dosyasına ekle."
            doc = Document(io.BytesIO(data))
            return "\n".join(p.text for p in doc.paragraphs)[:25000]

        if name.endswith((".txt", ".md", ".py", ".js", ".html", ".css",
                          ".json", ".csv", ".xml", ".yaml", ".yml")):
            return data.decode("utf-8", errors="replace")[:25000]

        if name.endswith((".png", ".jpg", ".jpeg", ".webp")):
            return (
                "Bu dosya bir görseldir. Görsel önizleme yapılabilir; "
                "bu sürüm görseli otomatik olarak görsel-zeka modeline "
                "göndermez. Görseldeki metni veya içeriği ayrıca yazabilirsin."
            )

        return "Bu dosya türü henüz desteklenmiyor."
    except Exception as exc:
        return f"Dosya okunamadı: {exc}"


# ---------------------------------------------------------
# GÖRSEL ÜRETİMİ
# ---------------------------------------------------------

def generate_image(prompt):
    account_id = (
        safe_get_secret("CLOUDFLARE_ACCOUNT_ID")
        or os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
    )
    token = (
        safe_get_secret("CLOUDFLARE_API_TOKEN")
        or os.getenv("CLOUDFLARE_API_TOKEN", "")
    )

    if not account_id or not token:
        st.error(
            "Görsel üretimi için CLOUDFLARE_ACCOUNT_ID ve "
            "CLOUDFLARE_API_TOKEN ayarlanmalı."
        )
        return None

    url = (
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}"
        "/ai/run/@cf/black-forest-labs/flux-1-schnell"
    )
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.post(
            url,
            headers=headers,
            json={"prompt": prompt},
            timeout=120,
        )
        response.raise_for_status()
        payload = response.json()

        result = payload.get("result", {})
        image_data = result.get("image")

        if image_data:
            if isinstance(image_data, str):
                return Image.open(io.BytesIO(base64.b64decode(image_data)))
            return None

        if "result" in payload and isinstance(payload["result"], dict):
            return None

        st.error("Görsel hizmetinden beklenen yanıt alınamadı.")
        return None
    except Exception as exc:
        st.error(f"Görsel üretimi başarısız: {exc}")
        return None


# ---------------------------------------------------------
# SES
# ---------------------------------------------------------

def transcribe_audio(audio_bytes, filename="recording.wav"):
    client = groq_client()
    if client is None:
        return "Ses yazıya çevrilemedi: Groq API anahtarı ayarlı değil."

    try:
        result = client.audio.transcriptions.create(
            file=(filename, audio_bytes),
            model="whisper-large-v3",
            response_format="text",
        )
        return str(result)
    except Exception as exc:
        return f"Ses yazıya çevrilemedi: {exc}"


# ---------------------------------------------------------
# YAN MENÜ
# ---------------------------------------------------------

with st.sidebar:
    st.markdown("## 💜 Lidya AI")
    st.caption("Düşün. Öğren. Üret. Keşfet.")

    selected_language = st.selectbox(
        "🌐 Language / Dil",
        list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.language),
    )
    st.session_state.language = selected_language

    st.markdown("---")
    st.markdown("### " + ui("settings"))

    module_labels = {
        key: ui(key) for key in MODULE_KEYS
    }

    chosen_key = st.radio(
        "Modüller",
        MODULE_KEYS,
        index=MODULE_KEYS.index(st.session_state.module),
        format_func=lambda key: (
            "🏠 " + module_labels[key] if key == "home"
            else module_labels[key]
        ),
        label_visibility="collapsed",
    )
    st.session_state.module = chosen_key

    st.markdown("---")
    st.caption("🕒 " + tr_now() + " · Türkiye")

    if st.button("🧹 " + ui("clear"), use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ---------------------------------------------------------
# ANA EKRAN
# ---------------------------------------------------------

module = st.session_state.module

if module == "home":
    st.markdown(
        """
        <div class="lidya-hero">
            <div class="lidya-title">💜 Lidya AI</div>
            <div class="lidya-subtitle">
                Düşün. Öğren. Üret. Keşfet.
            </div>
            <p class="small-muted">
                Built with curiosity and Python.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### " + ui("welcome"))
    st.write(
        "Lidya'nın bütün çalışma alanlarına sol menüden ulaşabilirsin. "
        "Bir modül seçerek sohbete, araştırmaya, dosya analizine veya "
        "simülasyonlara başlayabilirsin."
    )
    st.info(
        "Not: Bazı özellikler API anahtarı ve internet bağlantısı gerektirir. "
        "Canlı web araştırması, kalıcı kullanıcı hafızası ve gerçek metinden "
        "video üretimi bu temel sürümde otomatik olarak sağlanmaz."
    )


# ---------------------------------------------------------
# ÜNİVERSİTE KEŞFİ
# ---------------------------------------------------------

elif module == "universities":
    st.title("🎓 " + ui("universities"))
    st.write(
        "Üniversite isimlerinin yanındaki simgeler, ilgili sitelerin "
        "favicon'larıdır. Kabul koşulları, sınav politikaları ve son tarihler "
        "değişebildiğinden resmî kabul sayfasını kontrol et."
    )

    search = st.text_input("Üniversite ara")
    filtered = [
        uni for uni in UNIVERSITIES
        if search.lower() in uni["name"].lower()
    ]

    for start in range(0, len(filtered), 2):
        cols = st.columns(2)
        for offset, uni in enumerate(filtered[start:start + 2]):
            with cols[offset]:
                st.markdown('<div class="university-card">', unsafe_allow_html=True)
                a, b = st.columns([1, 4])
                with a:
                    icon_url = (
                        "https://www.google.com/s2/favicons?domain="
                        + uni["domain"] + "&sz=128"
                    )
                    st.image(icon_url, width=52)
                with b:
                    st.markdown("#### " + uni["name"])
                    st.markdown(
                        f"[Resmî site]({uni['site']}) · "
                        f"[Lisans başvuruları]({uni['admissions']})"
                    )
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Karşılaştırma ve planlama")
    st.write(
        "Üniversiteleri karşılaştırırken bölüm, başvuru takvimi, sınav "
        "gereklilikleri, maddi yardım, dil yeterliliği ve uluslararası "
        "öğrenci politikalarını her üniversitenin resmî sayfasından kontrol et."
    )
    comparison = st.multiselect(
        "Karşılaştırmak istediğin üniversiteleri seç",
        [u["name"] for u in UNIVERSITIES],
    )
    if comparison:
        for uni in UNIVERSITIES:
            if uni["name"] in comparison:
                st.markdown(
                    f"- **{uni['name']}** — "
                    f"[Resmî kabul bilgileri]({uni['admissions']})"
                )

    st.caption(
        "Bu bölüm şu anda canlı başvuru koşullarını otomatik taramaz; "
        "bağlantılar üniversitelerin resmî sitelerine gider."
    )


# ---------------------------------------------------------
# DOSYA LABORATUVARI
# ---------------------------------------------------------

elif module == "file":
    st.title("📁 " + ui("file"))
    st.write("PDF, Word, TXT, Markdown, CSV, JSON ve kod dosyalarını yükleyebilirsin.")

    uploaded = st.file_uploader(
        ui("upload"),
        type=["pdf", "docx", "txt", "md", "csv", "json", "py", "js",
              "html", "css", "xml", "yaml", "yml", "png", "jpg", "jpeg", "webp"],
        key="file_lab_upload",
    )

    if uploaded:
        st.session_state.last_uploaded_name = uploaded.name
        st.session_state.last_uploaded_text = read_uploaded_file(uploaded)
        st.success(f"Dosya alındı: {uploaded.name}")
        if uploaded.name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            st.image(uploaded, caption=uploaded.name, use_container_width=True)
        with st.expander("Çıkarılan içeriği görüntüle"):
            st.text(st.session_state.last_uploaded_text[:12000])

    task = st.text_area(
        "Dosya hakkında ne yapmamı istersin?",
        placeholder="Özetle, önemli noktaları çıkar, tabloyu açıkla...",
        height=110,
    )

    if st.button(ui("analyze"), type="primary"):
        if not uploaded:
            st.warning("Önce bir dosya yükle.")
        elif not task.strip():
            st.warning("Dosyayla ilgili isteğini yaz.")
        else:
            with st.spinner("Dosya inceleniyor..."):
                answer = ask_lidya(
                    task,
                    module="chat",
                    history=[],
                    file_context=st.session_state.last_uploaded_text,
                )
            st.markdown(answer)


# ---------------------------------------------------------
# GÖRSEL ATÖLYESİ
# ---------------------------------------------------------

elif module == "image":
    st.title("🎨 " + ui("image"))
    st.write("Bir görsel için ayrıntılı metin istemi oluştur veya API ile görsel üret.")
    prompt = st.text_area(
        ui("prompt"),
        placeholder="Örneğin: İnsan hücresinin bilimsel, etiketli eğitim illüstrasyonu...",
        height=120,
    )

    if st.button("🖼️ " + ui("generate"), type="primary"):
        if not prompt.strip():
            st.warning("Önce bir açıklama yaz.")
        else:
            with st.spinner("Görsel oluşturuluyor..."):
                image_result = generate_image(prompt)
            if image_result:
                st.image(image_result, caption="Lidya AI tarafından oluşturulan görsel")
                buffer = io.BytesIO()
                image_result.save(buffer, format="PNG")
                st.download_button(
                    "PNG olarak indir",
                    data=buffer.getvalue(),
                    file_name="lidya_ai_image.png",
                    mime="image/png",
                )


# ---------------------------------------------------------
# VİDEO ATÖLYESİ
# ---------------------------------------------------------

elif module == "video":
    st.title("🎬 " + ui("video"))
    st.info(
        "Bu bölümde tek bir görselden basit yakınlaşma animasyonu üretilebilir. "
        "Bu özellik, metinden gerçekçi yeni video üreten bir model değildir."
    )
    video_image = st.file_uploader(
        "Animasyon için bir görsel yükle",
        type=["png", "jpg", "jpeg", "webp"],
        key="video_image",
    )
    zoom_seconds = st.slider("Süre (saniye)", 2, 8, 4)

    if st.button("Animasyon oluştur", type="primary"):
        if not video_image:
            st.warning("Önce bir görsel yükle.")
        else:
            try:
                original = Image.open(video_image).convert("RGB")
                frames = []
                width, height = original.size
                frame_count = zoom_seconds * 8

                for i in range(frame_count):
                    scale = 1 + (0.12 * i / max(1, frame_count - 1))
                    new_w, new_h = int(width * scale), int(height * scale)
                    enlarged = original.resize((new_w, new_h))
                    left = max(0, (new_w - width) // 2)
                    top = max(0, (new_h - height) // 2)
                    frame = enlarged.crop((left, top, left + width, top + height))
                    frames.append(np.array(frame))

                import imageio.v2 as imageio
                with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp:
                    video_path = temp.name

                imageio.mimsave(video_path, frames, fps=8, codec="libx264")
                with open(video_path, "rb") as file_handle:
                    video_bytes = file_handle.read()

                st.video(video_bytes)
                st.download_button(
                    "MP4 videosunu indir",
                    data=video_bytes,
                    file_name="lidya_zoom_animation.mp4",
                    mime="video/mp4",
                )
            except Exception as exc:
                st.error(
                    "Animasyon oluşturulamadı. imageio-ffmpeg kurulumunu "
                    f"kontrol et. Ayrıntı: {exc}"
                )


# ---------------------------------------------------------
# SİMÜLASYON LABORATUVARI
# ---------------------------------------------------------

elif module == "sim":
    st.title("🪐 " + ui("sim"))
    sim_type = st.selectbox(
        "Simülasyon seç",
        [
            "Fonksiyon grafiği",
            "Mermi hareketi",
            "Dalga hareketi",
            "Basit yörünge modeli",
        ],
    )

    if sim_type == "Fonksiyon grafiği":
        expression = st.selectbox(
            "Fonksiyon",
            ["x²", "sin(x)", "cos(x)", "x³ - 2x", "eˣ"],
        )
        x = np.linspace(-10, 10, 500)
        y = {
            "x²": x ** 2,
            "sin(x)": np.sin(x),
            "cos(x)": np.cos(x),
            "x³ - 2x": x ** 3 - 2 * x,
            "eˣ": np.exp(np.clip(x, -10, 5)),
        }[expression]
        st.line_chart({"y": y}, x_label="Örnek noktalar", y_label="f(x)")

    elif sim_type == "Mermi hareketi":
        angle = st.slider("Atış açısı (derece)", 10, 80, 45)
        speed = st.slider("Başlangıç hızı (m/s)", 5, 100, 30)
        gravity = 9.81
        rad = np.radians(angle)
        vx = speed * np.cos(rad)
        vy = speed * np.sin(rad)
        flight_time = 2 * vy / gravity
        t = np.linspace(0, flight_time, 250)
        x = vx * t
        y = vy * t - 0.5 * gravity * t ** 2
        st.line_chart({"Yükseklik (m)": y}, x_label="Zaman örnekleri")
        st.write(f"İdeal modelde yaklaşık menzil: **{x[-1]:.1f} m**")
        st.caption("Hava direnci ve arazi yüksekliği hesaba katılmamıştır.")

    elif sim_type == "Dalga hareketi":
        amplitude = st.slider("Genlik", 1, 10, 4)
        frequency = st.slider("Frekans", 1, 10, 2)
        x = np.linspace(0, 4 * np.pi, 400)
        y = amplitude * np.sin(frequency * x)
        st.line_chart({"Dalga": y}, x_label="Konum örnekleri")

    else:
        radius = st.slider("Yörünge yarıçapı (temsili)", 1, 10, 5)
        theta = np.linspace(0, 2 * np.pi, 360)
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        st.pyplot(plt.figure())
        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.scatter([0], [0])
        ax.set_aspect("equal", adjustable="box")
        ax.set_title("Basitleştirilmiş dairesel yörünge")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        st.pyplot(fig)
        plt.close(fig)
        st.caption("Bu çizim fiziksel olarak tam bir yörünge simülatörü değildir.")


# ---------------------------------------------------------
# SES VE KARAOKE
# ---------------------------------------------------------

elif module == "karaoke":
    st.title("🎤 " + ui("karaoke"))
    st.write(
        "Kendi ses kaydını yapabilir, desteklenen ses dosyalarını dinleyebilir "
        "ve kaydını yazıya çevirebilirsin. Telifli şarkı sözleri veya "
        "altyapılar uygulamaya gömülü değildir."
    )

    audio_file = st.file_uploader(
        "Bir ses dosyası yükle",
        type=["wav", "mp3", "m4a", "ogg", "flac"],
        key="karaoke_upload",
    )
    if audio_file:
        st.audio(audio_file)
        if st.button("Ses dosyasını yazıya çevir"):
            with st.spinner("Ses yazıya çevriliyor..."):
                transcript = transcribe_audio(
                    audio_file.getvalue(), audio_file.name
                )
            st.text_area("Transkripsiyon", transcript, height=180)

    st.markdown("### Mikrofon kaydı")
    mic = st.audio_input("Sesini kaydet")
    if mic:
        st.audio(mic)
        if st.button("Kaydı yazıya çevir"):
            with st.spinner("Kayıt işleniyor..."):
                transcript = transcribe_audio(mic.getvalue(), "recording.wav")
            st.text_area("Kaydının metni", transcript, height=180)

    st.markdown("### Metni sesli dinle")
    tts_text = st.text_area("Okunacak metin", key="tts_text")
    if tts_text:
        escaped = json.dumps(tts_text, ensure_ascii=False)
        st.components.v1.html(
            f"""
            <button onclick='speakText()'
            style='padding:10px 16px;border-radius:10px;cursor:pointer;'>
            🔊 Metni sesli oku
            </button>
            <button onclick='window.speechSynthesis.cancel()'
            style='padding:10px 16px;border-radius:10px;cursor:pointer;'>
            ⏹ Durdur
            </button>
            <script>
            function speakText() {{
                const text = {escaped};
                const utterance = new SpeechSynthesisUtterance(text);
                window.speechSynthesis.speak(utterance);
            }}
            </script>
            """,
            height=75,
        )


# ---------------------------------------------------------
# LIDYA HAFIZASI
# ---------------------------------------------------------

elif module == "memory":
    st.title("🧠 " + ui("memory"))
    st.warning(
        "Bu hafıza yalnızca mevcut Streamlit oturumu boyunca tutulur. "
        "Sayfa yenilenmesi veya oturumun sona ermesi durumunda kaybolabilir. "
        "Kalıcı, kullanıcıya özel hafıza için veritabanı ve kullanıcı hesabı gerekir."
    )

    memory_text = st.text_input(
        ui("remember"),
        placeholder="Örneğin: Projemin adı Lidya AI.",
    )
    if st.button("Hafızaya ekle"):
        if memory_text.strip():
            st.session_state.memory_items.append({
                "text": memory_text.strip(),
                "time": tr_now(),
            })
            st.success("Bu oturumun hafızasına eklendi.")

    st.subheader(ui("show_memory"))
    if st.session_state.memory_items:
        for index, item in enumerate(st.session_state.memory_items, 1):
            st.write(f"{index}. {item['text']}  ·  {item['time']}")
    else:
        st.caption("Bu oturumda henüz kaydedilmiş bir bilgi yok.")

    if st.button(ui("clear_memory")):
        st.session_state.memory_items = []
        st.success("Oturum hafızası temizlendi.")


# ---------------------------------------------------------
# AYARLAR
# ---------------------------------------------------------

elif module == "settings":
    st.title("⚙️ " + ui("settings"))
    st.write("### API bağlantı durumu")
    st.write("Groq:", "Bağlı görünüyor" if groq_client() else "API anahtarı ayarlanmamış")
    st.write(
        "Cloudflare görsel API:",
        "Ayarlandı" if (CF_ACCOUNT_ID and CF_API_TOKEN) else "API bilgileri eksik",
    )
    st.write("Arayüz dili:", st.session_state.language)
    st.write("Türkiye saati:", tr_now())
    st.info(
        "API anahtarlarını kodun içine yazma. Streamlit Cloud Secrets "
        "bölümünde sakla."
    )


# ---------------------------------------------------------
# DİĞER SOHBET MODÜLLERİ
# ---------------------------------------------------------

elif module in SPECIALIST_PROMPTS:
    st.title("💜 " + ui(module))
    st.caption("🕒 " + tr_now() + " · Türkiye saati")

    # Dosya, konuşma modüllerinde de isteğe bağlı olarak eklenebilir.
    uploaded = st.file_uploader(
        "İstersen bu mesaja dosya ekle",
        type=["pdf", "docx", "txt", "md", "csv", "json", "py", "js",
              "html", "css", "xml", "yaml", "yml"],
        key=f"chat_upload_{module}",
    )

    if uploaded:
        st.session_state.last_uploaded_name = uploaded.name
        st.session_state.last_uploaded_text = read_uploaded_file(uploaded)
        st.caption(f"Eklenen dosya: {uploaded.name}")

    for item in st.session_state.messages:
        if item.get("module") != module:
            continue
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
            st.caption(item.get("time", ""))

    prompt = st.chat_input(ui("send"))

    if prompt:
        if any(
            word in prompt.lower()
            for word in ["who designed you", "who created you",
                         "seni kim yaptı", "seni kim geliştirdi",
                         "seni kim tasarladı"]
        ):
            answer = (
                "Lidya AI projesini Şeymanur Acun geliştirdi. "
                "Lidya'nın kullandığı temel yapay zekâ modeli ve diğer "
                "hizmetler ise ilgili sağlayıcılar tarafından geliştirilmiştir."
            )
        else:
            prior = [
                item for item in st.session_state.messages
                if item.get("module") == module
            ]
            with st.spinner("Lidya düşünüyor..."):
                answer = ask_lidya(
                    prompt,
                    module=module,
                    history=prior,
                    file_context=st.session_state.get("last_uploaded_text", ""),
                )

        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "time": tr_now(),
            "module": module,
        })
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "time": tr_now(),
            "module": module,
        })
        st.rerun()


# ---------------------------------------------------------
# ALT BİLGİ
# ---------------------------------------------------------

st.markdown("---")
st.caption("💜 Lidya AI · Built with curiosity and Python.")

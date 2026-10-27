import os
import json
import io
import math
import re
import time
import uuid
import hashlib
import urllib.parse
import requests
from PIL import Image, ImageDraw, ImageFont
import imageio.v2 as imageio
from ddgs import DDGS
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import matplotlib.pyplot as plt
from pypdf import PdfReader
from docx import Document
import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

# ======================================================
# 1. PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Lidya AI",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ======================================================
# 2. SETTINGS
# ======================================================
MODEL_NAME = "openai/gpt-oss-20b"

LANGUAGES = {
    "Türkçe": "Turkish",
    "English": "English",
    "Français": "French",
    "Deutsch": "German",
    "Español": "Spanish",
    "Italiano": "Italian",
    "日本語": "Japanese",
}

MODULES = {
    "💜 Lidya": ("General Assistant", "Everyday questions, learning, research, writing and programming."),
    "📁 File Laboratory": ("File Laboratory", "Read and discuss supported text-based documents attached in chat."),
    "🩺 Medical & Anatomy": ("Medical & Anatomy", "Explain anatomy and medical concepts for education, not personal diagnosis or treatment."),
    "⚖️ Legal Research": ("Legal Research", "Explain general legal concepts; ask which jurisdiction applies when relevant."),
    "🌍 Language Teacher": ("Language Teacher", "Practice languages, grammar, vocabulary, writing and translation."),
    "💻 Software Engineering": ("Software Engineering", "Programming, debugging, code review and software design."),
    "🔬 Science & Research": ("Science & Research", "Explain scientific concepts, methods and uncertainty."),
    "📐 Mathematics": ("Mathematics", "Solve math problems carefully and explain steps."),
    "⚙️ Engineering": ("Engineering", "Explain engineering principles and calculations."),
    "📚 Education": ("Education", "Create learning plans, explanations and study activities."),
    "🎓 University & Admissions": ("University & Admissions", "Research universities, admissions requirements, scholarships, financial aid, essays, applications, professor outreach and application planning. Clearly distinguish official verified information from general guidance."),
    "📊 Business & Economics": ("Business & Economics", "Explain business, economics and data concepts."),
    "✍️ Writing & Creativity": ("Writing & Creativity", "Help brainstorm, write, revise and edit original text."),
    "📈 Data Analysis": ("Data Analysis", "Help interpret data and explain analysis methods."),
    "🔐 Cybersecurity": ("Cybersecurity", "Focus on defensive security, privacy and secure coding."),
    "🏠 Smart Devices": ("Smart Devices", "Plan safe smart-home integrations; do not claim to control devices."),
    "🎨 Image Studio": ("Image Studio", "Generate images and create detailed visual prompts."),
    "🎬 Video Studio": ("Video Studio", "Generate a short storyboard-style MP4 from AI-generated scene images, plus a production pack."),
}

MODULE_LABELS = {
    "Türkçe": {
        "📁 File Laboratory": "📁 Dosya Laboratuvarı",
        "🩺 Medical & Anatomy": "🩺 Tıp ve Anatomi",
        "⚖️ Legal Research": "⚖️ Hukuk Araştırmaları",
        "🌍 Language Teacher": "🌍 Dil Öğretmeni",
        "💻 Software Engineering": "💻 Yazılım Mühendisliği",
        "🔬 Science & Research": "🔬 Bilim ve Araştırma",
        "📐 Mathematics": "📐 Matematik",
        "⚙️ Engineering": "⚙️ Mühendislik",
        "📚 Education": "📚 Eğitim",
        "🎓 University & Admissions": "🎓 Üniversite ve Başvurular",
        "📊 Business & Economics": "📊 İşletme ve Ekonomi",
        "✍️ Writing & Creativity": "✍️ Yazma ve Yaratıcılık",
        "📈 Data Analysis": "📈 Veri Analizi",
        "🔐 Cybersecurity": "🔐 Siber Güvenlik",
        "🏠 Smart Devices": "🏠 Akıllı Cihazlar",
        "🎨 Image Studio": "🎨 Görsel Atölyesi",
        "🎬 Video Studio": "🎬 Video Atölyesi",
    }
}

TEXT = {
    "Türkçe": {
        "subtitle": "Düşün. Öğren. Üret. Keşfet.",
        "language": "Arayüz ve yanıt dili",
        "modules": "ÇALIŞMA ALANLARI",
        "clear": "Sohbeti temizle",
        "voice": "Yanıtı sesli oku",
        "thinking": "Lidya düşünüyor...",
        "chat": "Lidya'ya bir şey sor...",
        "welcome": "Merhaba! Ben Lidya AI, eğitim ve üretkenlik asistanınızım. Size nasıl yardımcı olabilirim?",
        "no_key": "GROQ_API_KEY bulunamadı. Streamlit Secrets ayarını kontrol et.",
        "footer": "Merakla ve Python ile geliştirildi.",
        "search_off": "Canlı web araması açılabilir.",
        "creative": "Ne oluşturmak istiyorsun?",
        "prepare": "İstemi hazırla",
        "file_note": "Desteklenen PDF, DOCX, TXT, MD, CSV, JSON ve PY dosyalarını sohbet kutusundaki ekleme düğmesiyle yükleyebilirsin.",
        "error": "Yanıt oluşturulamadı. API anahtarını, model erişimini ve kotanı kontrol et.",
    },
    "English": {
        "subtitle": "Think. Learn. Create. Discover.",
        "language": "Interface and response language",
        "modules": "WORKSPACES",
        "clear": "Clear conversation",
        "voice": "Read the answer aloud",
        "thinking": "Lidya is thinking...",
        "chat": "Ask Lidya anything...",
        "welcome": "Hello! I'm Lidya. How can I help you?",
        "no_key": "GROQ_API_KEY not found. Check Streamlit Secrets.",
        "footer": "Built with curiosity and Python.",
        "search_off": "Live web search can be enabled.",
        "creative": "What would you like to create?",
        "prepare": "Prepare prompt",
        "file_note": "Attach supported PDF, DOCX, TXT, MD, CSV, JSON or PY files directly in the chat input.",
        "error": "Could not generate a response. Check your API key, model access and quota.",
    },
    "Français": {
        "subtitle": "Réfléchir. Apprendre. Créer. Découvrir.",
        "language": "Langue de l'interface et des réponses",
        "modules": "ESPACES DE TRAVAIL",
        "clear": "Effacer la conversation",
        "voice": "Lire la réponse à voix haute",
        "thinking": "Lidya réfléchit...",
        "chat": "Posez une question à Lidya...",
        "welcome": "Bonjour ! Je suis Lidya. Comment puis-je vous aider ?",
        "no_key": "GROQ_API_KEY introuvable. Vérifiez les Secrets.",
        "footer": "Créé avec curiosité et Python.",
        "search_off": "La recherche Web en direct peut être activée.",
        "creative": "Que souhaitez-vous créer ?",
        "prepare": "Préparer le prompt",
        "file_note": "Joignez les fichiers PDF, DOCX, TXT, MD, CSV, JSON ou PY pris en charge directement au chat.",
        "error": "Impossible de générer une réponse. Vérifiez la clé API, le modèle et le quota.",
    },
    "Deutsch": {
        "subtitle": "Denken. Lernen. Gestalten. Entdecken.",
        "language": "Sprache der Oberfläche und Antworten",
        "modules": "ARBEITSBEREICHE",
        "clear": "Unterhaltung löschen",
        "voice": "Antwort vorlesen",
        "thinking": "Lidya denkt nach...",
        "chat": "Frage Lidya etwas...",
        "welcome": "Hallo! Ich bin Lidya. Wie kann ich dir helfen?",
        "no_key": "GROQ_API_KEY fehlt. Überprüfe die Streamlit-Secrets.",
        "footer": "Mit Neugier und Python entwickelt.",
        "search_off": "Live-Websuche kann aktiviert werden.",
        "creative": "Was möchtest du erstellen?",
        "prepare": "Prompt vorbereiten",
        "file_note": "Unterstützte PDF-, DOCX-, TXT-, MD-, CSV-, JSON- oder PY-Dateien direkt im Chat anhängen.",
        "error": "Antwort konnte nicht erstellt werden. Prüfe API-Schlüssel, Modellzugriff und Kontingent.",
    },
    "Español": {
        "subtitle": "Piensa. Aprende. Crea. Descubre.",
        "language": "Idioma de la interfaz y las respuestas",
        "modules": "ESPACIOS DE TRABAJO",
        "clear": "Borrar conversación",
        "voice": "Leer la respuesta en voz alta",
        "thinking": "Lidya está pensando...",
        "chat": "Pregúntale algo a Lidya...",
        "welcome": "¡Hola! Soy Lidya. ¿Cómo puedo ayudarte?",
        "no_key": "No se encontró GROQ_API_KEY. Revisa los Secrets.",
        "footer": "Creado con curiosidad y Python.",
        "search_off": "La búsqueda web en directo se puede activar.",
        "creative": "¿Qué quieres crear?",
        "prepare": "Preparar instrucciones",
        "file_note": "Adjunta archivos PDF, DOCX, TXT, MD, CSV, JSON o PY compatibles directamente al chat.",
        "error": "No se pudo generar una respuesta. Revisa la clave API, el modelo y la cuota.",
    },
    "Italiano": {
        "subtitle": "Pensa. Impara. Crea. Scopri.",
        "language": "Lingua dell'interfaccia e delle risposte",
        "modules": "SPAZI DI LAVORO",
        "clear": "Cancella conversazione",
        "voice": "Leggi la risposta ad alta voce",
        "thinking": "Lidya sta pensando...",
        "chat": "Chiedi qualcosa a Lidya...",
        "welcome": "Ciao! Sono Lidya. Come posso aiutarti?",
        "no_key": "GROQ_API_KEY mancante. Controlla i Secrets.",
        "footer": "Creato con curiosità e Python.",
        "search_off": "La ricerca web in tempo reale può essere attivata.",
        "creative": "Che cosa vuoi creare?",
        "prepare": "Prepara il prompt",
        "file_note": "Allega direttamente alla chat file PDF, DOCX, TXT, MD, CSV, JSON o PY supportati.",
        "error": "Impossibile generare una risposta. Controlla chiave API, modello e quota.",
    },
    "日本語": {
        "subtitle": "考える。学ぶ。創造する。発見する。",
        "language": "画面と言語",
        "modules": "ワークスペース",
        "clear": "会話を消去",
        "voice": "回答を読み上げる",
        "thinking": "Lidyaが考えています...",
        "chat": "Lidyaに質問する...",
        "welcome": "こんにちは！Lidyaです。どのようにお手伝いできますか？",
        "no_key": "GROQ_API_KEYが見つかりません。Secretsを確認してください。",
        "footer": "好奇心とPythonで開発。",
        "search_off": "ライブWeb検索を有効にできます。",
        "creative": "何を作成しますか？",
        "prepare": "プロンプトを準備",
        "file_note": "対応するPDF、DOCX、TXT、MD、CSV、JSON、PYファイルをチャットに添付できます。",
        "error": "回答を生成できませんでした。APIキー、モデル、利用制限を確認してください。",
    },
}

# ======================================================
# 3. API CLIENT
# ======================================================
def get_api_key():
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY", "")

@st.cache_resource
def get_client(api_key):
    return Groq(api_key=api_key, timeout=60.0, max_retries=1)

API_KEY = get_api_key()
client = get_client(API_KEY) if API_KEY else None

# ======================================================
# 4. VISUAL DESIGN
# ======================================================
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #30204f 0%, #141326 48%, #090914 100%);
    color: #f4efff;
}
[data-testid="stSidebar"] {
    background: #111020;
    border-right: 1px solid #3b2b59;
}
.lidya-title {
    font-size: clamp(34px, 6vw, 48px);
    font-weight: 900;
    letter-spacing: 4px;
    text-align: center;
    background: linear-gradient(90deg, #f6d7ff, #bb9aff, #83e8ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.lidya-subtitle { text-align: center; color: #d3c8f5; font-size: 16px; }
.orb {
    width: 100px; height: 100px; margin: 20px auto; border-radius: 50%;
    background: radial-gradient(circle at 30% 25%, #fff, #d5a8ff 15%, #8c54ed 40%, #402078 70%, #161126 100%);
    box-shadow: 0 0 25px #b77cff, 0 0 60px #8255ff;
    animation: float 3s ease-in-out infinite;
}
@keyframes float { 0%,100% {transform:translateY(0)} 50% {transform:translateY(-8px)} }
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(200,170,255,0.17);
    border-radius: 15px;
}
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

if st.session_state.get("theme_choice") == "Aydınlık":
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(145deg, #f8f3ff, #edf5ff) !important; color: #241b35 !important; }
    [data-testid="stSidebar"] { background: #f0e9fa !important; }
    [data-testid="stChatMessage"] { background: rgba(255,255,255,.88) !important; border-color: #d9c8ee !important; }
    </style>
    """, unsafe_allow_html=True)

# ======================================================
# 5. SYSTEM INSTRUCTIONS
# ======================================================
def build_system_instruction(module, language):
    module_name, module_description = MODULES[module]
    return f"""
You are Lidya AI, a thoughtful, accurate and helpful assistant.
Current workspace: {module_name}
Workspace purpose: {module_description}
Respond in {LANGUAGES[language]} unless the user asks for another language.
Preferred response style: {st.session_state.get("response_style", "Dengeli")}.
Preferred response length: {st.session_state.get("response_length", "Orta")}.

QUALITY:
- Understand the question and use relevant conversation context.
- Give accurate, well-structured answers.
- Explain complex topics step by step, but keep simple answers concise.
- For math, check calculations and show the method.
- For programming, give runnable code when possible and explain important parts.
- Never invent facts, citations, URLs, quotes, or actions you did not perform.
- State uncertainty clearly and correct mistakes when noticed.
- If live web search results are supplied in the current request, summarize them carefully and distinguish source claims from verified facts.
- Do not ask for passwords, API keys, or unnecessary sensitive information.

MEDICAL:
Provide educational information only, not a definitive personal diagnosis or treatment plan.
Encourage qualified medical care for important health decisions.

LEGAL:
Provide general legal information, not legal representation. Ask which jurisdiction applies when relevant.

SMART DEVICES:
This app does not directly control physical devices. Never claim a device was activated or changed.

UNIVERSITY & ADMISSIONS:
Help with university discovery, admissions planning, scholarships, financial aid, essays, outreach and deadlines. For current requirements, use live search results when enabled and prioritize official university pages. Never guarantee admission, scholarships, or funding.
"""

# ======================================================
# 6. SESSION STATE + FILE UTILITIES
# ======================================================
if "chats_by_module" not in st.session_state:
    st.session_state.chats_by_module = {}
if "current_chat_by_module" not in st.session_state:
    st.session_state.current_chat_by_module = {}
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""
if "response_style" not in st.session_state:
    st.session_state.response_style = "Dengeli"
if "response_length" not in st.session_state:
    st.session_state.response_length = "Orta"
if "theme_choice" not in st.session_state:
    st.session_state.theme_choice = "Gece moru"
if "video_pack" not in st.session_state:
    st.session_state.video_pack = ""
if "last_voice_hash" not in st.session_state:
    st.session_state.last_voice_hash = ""

def ensure_chat(module):
    """Keep multiple named conversations per workspace during the current Streamlit session."""
    chats = st.session_state.chats_by_module.setdefault(module, [])
    current_id = st.session_state.current_chat_by_module.get(module)
    current = next((chat for chat in chats if chat["id"] == current_id), None)
    if current is None:
        current = {"id": uuid.uuid4().hex[:10], "name": "Yeni sohbet", "messages": []}
        chats.append(current)
        st.session_state.current_chat_by_module[module] = current["id"]
    return current

def get_messages(module):
    return ensure_chat(module)["messages"]

def new_chat(module):
    chat = {"id": uuid.uuid4().hex[:10], "name": "Yeni sohbet", "messages": []}
    st.session_state.chats_by_module.setdefault(module, []).append(chat)
    st.session_state.current_chat_by_module[module] = chat["id"]

def current_chat(module):
    return ensure_chat(module)

def extract_file(uploaded_file):
    name = uploaded_file.name.lower()
    data = uploaded_file.getvalue()
    try:
        if name.endswith((".txt", ".md", ".py", ".json", ".csv")):
            return data.decode("utf-8", errors="replace")[:16000]
        if name.endswith(".pdf"):
            reader = PdfReader(io.BytesIO(data))
            return "\n\n".join(page.extract_text() or "" for page in reader.pages)[:16000]
        if name.endswith(".docx"):
            doc = Document(io.BytesIO(data))
            return "\n".join(paragraph.text for paragraph in doc.paragraphs)[:16000]
    except Exception as exc:
        return f"Dosya okunamadı ({type(exc).__name__})."
    if name.endswith((".png", ".jpg", ".jpeg", ".webp")):
        return f"[Görsel eklendi: {uploaded_file.name}. Bu model bağlantısı görsel içeriğini otomatik analiz etmiyor; lütfen görseli tarif et.]"
    return f"[Desteklenmeyen dosya türü: {uploaded_file.name}]"

def transcribe_audio(audio_file):
    """Transcribe a short user-recorded voice message through Groq Whisper."""
    if client is None:
        raise RuntimeError("GROQ_API_KEY bulunamadı.")
    audio_bytes = audio_file.getvalue()
    filename = getattr(audio_file, "name", "hey_lidya_audio.wav") or "hey_lidya_audio.wav"
    return client.audio.transcriptions.create(
        file=(filename, audio_bytes),
        model="whisper-large-v3-turbo",
        response_format="text",
    )


def turkish_time():
    return datetime.now(ZoneInfo("Europe/Istanbul")).strftime("%d.%m.%Y %H:%M")


def search_web(query, max_results=5):
    """Fetch public web results using DuckDuckGo search; returns titles, URLs and snippets."""
    results = []
    try:
        with DDGS() as ddgs:
            for item in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": item.get("title", "Untitled"),
                    "url": item.get("href", item.get("url", "")),
                    "body": item.get("body", ""),
                })
    except Exception as exc:
        return [], f"{type(exc).__name__}: {exc}"
    return results, None


def generate_image_bytes(prompt, width=1024, height=1024, seed=None):
    """Generate an image using the public Pollinations image endpoint (availability may vary)."""
    safe_prompt = urllib.parse.quote(prompt[:1800], safe="")
    params = {"width": width, "height": height, "nologo": "true", "model": "flux"}
    if seed is not None:
        params["seed"] = int(seed)
    url = f"https://image.pollinations.ai/prompt/{safe_prompt}"
    response = requests.get(url, params=params, timeout=120, headers={"User-Agent": "LidyaAI/1.0"})
    response.raise_for_status()
    image = Image.open(io.BytesIO(response.content)).convert("RGB")
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def fit_frame(image_bytes, width=960, height=540, caption=""):
    im = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    im.thumbnail((width, height))
    canvas = Image.new("RGB", (width, height), "black")
    canvas.paste(im, ((width-im.width)//2, (height-im.height)//2))
    if caption:
        draw = ImageDraw.Draw(canvas)
        # Use the default font to avoid platform-specific font dependencies.
        draw.rectangle((0, height-58, width, height), fill=(12, 10, 24))
        draw.text((24, height-39), caption[:120], fill=(245, 238, 255))
    return canvas


def create_slideshow_video(scene_images, scene_captions, seconds_per_scene=2, fps=12):
    """Build a simple MP4 from generated still images; this is a slideshow, not AI motion video."""
    path = f"/tmp/lidya_video_{int(time.time())}.mp4"
    with imageio.get_writer(path, fps=fps, codec="libx264", macro_block_size=16) as writer:
        for img_bytes, caption in zip(scene_images, scene_captions):
            frame = fit_frame(img_bytes, caption=caption)
            arr = np.asarray(frame)
            for _ in range(max(1, int(seconds_per_scene*fps))):
                writer.append_data(arr)
    with open(path, "rb") as f:
        return f.read()

# ======================================================
# 7. SIDEBAR
# ======================================================
with st.sidebar:
    st.markdown("## 💜 Lidya AI")
    language = st.selectbox(
        "🌍 Language / Dil",
        list(LANGUAGES.keys()),
        key="interface_language",
    )
    ui = TEXT[language]
    st.markdown(f"### {ui['modules']}")

    module_keys = list(MODULES.keys()) + ["⚙️ Ayarlar"]
    module_labels = [
        MODULE_LABELS.get(language, {}).get(key, key)
        for key in module_keys
    ]
    selected_label = st.radio(
        ui["modules"],
        module_labels,
        label_visibility="collapsed",
    )
    selected_module = module_keys[module_labels.index(selected_label)]

    web_search_enabled = st.checkbox("🌐 Canlı web araması", value=False, key="web_search_enabled")
    voice_output = st.checkbox(ui["voice"], value=False, key="voice_output")

    if selected_module in MODULES:
        active = ensure_chat(selected_module)
        st.markdown("### 💬 Sohbetler")
        if st.button("➕ Yeni sohbet", use_container_width=True, key="create_new_chat"):
            new_chat(selected_module)
            st.rerun()
        chats = st.session_state.chats_by_module.get(selected_module, [])
        chat_ids = [chat["id"] for chat in chats]
        current_id = st.session_state.current_chat_by_module[selected_module]
        selected_id = st.radio(
            "Kayıtlı sohbetler", chat_ids,
            index=chat_ids.index(current_id) if current_id in chat_ids else 0,
            format_func=lambda cid: next((c["name"] for c in chats if c["id"] == cid), "Sohbet"),
            key=f"chat_picker_{selected_module}_{len(chats)}",
            label_visibility="collapsed",
        )
        if selected_id != current_id:
            st.session_state.current_chat_by_module[selected_module] = selected_id
            st.rerun()
        active = current_chat(selected_module)
        rename_value = st.text_input("Sohbet adı", value=active["name"], key=f"rename_input_{selected_module}_{active['id']}")
        if st.button("✏️ Sohbeti yeniden adlandır", use_container_width=True, key=f"rename_btn_{selected_module}_{active['id']}"):
            clean_name = rename_value.strip()[:60]
            if clean_name:
                active["name"] = clean_name
                st.rerun()
        if st.button("🧹 Bu sohbetin mesajlarını temizle", use_container_width=True, key=f"clear_chat_{selected_module}_{active['id']}"):
            active["messages"] = []
            st.session_state.last_answer = ""
            st.rerun()

    st.divider()
    st.caption("💜 Lidya AI · Hey Lidya sesli giriş aşağıda")

# ======================================================
# 8. HEADER + SETTINGS
# ======================================================
st.markdown('<div class="lidya-title">LIDYA AI</div>', unsafe_allow_html=True)
st.markdown(f'<div class="lidya-subtitle">{ui["subtitle"]}</div>', unsafe_allow_html=True)
st.markdown('<div class="orb"></div>', unsafe_allow_html=True)

if selected_module == "⚙️ Ayarlar":
    st.title("⚙️ Ayarlar")
    st.write("Lidya'nın çalışma biçimini kişiselleştir.")
    st.selectbox("Tema", ["Gece moru", "Aydınlık"], key="theme_choice")
    st.selectbox("Yanıt tarzı", ["Dengeli", "Kısa ve doğrudan", "Ayrıntılı ve öğretici", "Yaratıcı"], key="response_style")
    st.selectbox("Yanıt uzunluğu", ["Kısa", "Orta", "Uzun"], key="response_length")
    st.info("API anahtarları yalnızca Streamlit Cloud → Settings → Secrets bölümünde tutulmalı; kod içine yazılmamalı.")
    if st.button("Tüm çalışma alanlarının sohbetlerini temizle"):
        st.session_state.chats_by_module = {}
        st.session_state.current_chat_by_module = {}
        st.session_state.last_answer = ""
        st.rerun()
    st.caption("Bu ayarlar oturum boyunca geçerlidir. Kalıcı kullanıcı profili bu sürümde bulunmaz.")

elif selected_module == "📐 Mathematics":
    st.subheader("📐 Mathematics Lab")
    st.write("Etkileşimli matematik deneyleri bu çalışma alanında bulunur.")
    experiment = st.selectbox("Deney", ["Fonksiyon grafiği", "İkinci derece denklem", "Atış hareketi", "Dairesel hareket", "Dalga modeli"])
    if experiment == "Fonksiyon grafiği":
        c1, c2, c3 = st.columns(3)
        a = c1.slider("a", -5.0, 5.0, 1.0, 0.1)
        b = c2.slider("b", -10.0, 10.0, 0.0, 0.5)
        c = c3.slider("c", -10.0, 10.0, 0.0, 0.5)
        x = np.linspace(-10, 10, 400); y = a*x*x+b*x+c
        fig, ax = plt.subplots(); ax.plot(x,y); ax.axhline(0, linewidth=.8); ax.axvline(0, linewidth=.8); ax.grid(True, alpha=.25)
        ax.set_title(f"f(x) = {a:g}x² + {b:g}x + {c:g}"); st.pyplot(fig, use_container_width=True)
    elif experiment == "İkinci derece denklem":
        c1,c2,c3 = st.columns(3); aa=c1.number_input("a katsayısı", value=1.0); bb=c2.number_input("b katsayısı", value=-3.0); cc=c3.number_input("c katsayısı", value=2.0)
        if abs(aa) < 1e-12: st.warning("a sıfır olamaz; bu durumda denklem ikinci derece değildir.")
        else:
            delta=bb*bb-4*aa*cc; st.metric("Diskriminant Δ", f"{delta:.4g}")
            if delta > 0: st.success(f"Kökler: {(-bb+math.sqrt(delta))/(2*aa):.5g} ve {(-bb-math.sqrt(delta))/(2*aa):.5g}")
            elif abs(delta) < 1e-12: st.success(f"Çakışık kök: {-bb/(2*aa):.5g}")
            else: st.info("Gerçek kök yok; iki karmaşık kök vardır.")
    elif experiment == "Atış hareketi":
        speed=st.slider("İlk hız (m/s)", 5, 50, 25); angle=st.slider("Açı (derece)", 5, 85, 45); theta=math.radians(angle); g=9.81; total=2*speed*math.sin(theta)/g
        t=np.linspace(0,total,300); x=speed*math.cos(theta)*t; y=speed*math.sin(theta)*t-.5*g*t*t
        fig,ax=plt.subplots(); ax.plot(x,y); ax.set_xlabel("Mesafe (m)"); ax.set_ylabel("Yükseklik (m)"); ax.grid(True,alpha=.25); ax.set_title("İdeal yörünge (hava direnci yok)"); st.pyplot(fig,use_container_width=True)
        st.metric("İdeal menzil", f"{speed**2*math.sin(2*theta)/g:.2f} m")
    elif experiment == "Dairesel hareket":
        radius=st.slider("Yarıçap (m)",1,20,5); period=st.slider("Periyot (s)",1,30,8); time=st.slider("Zaman (s)",0.0,float(period),2.0,.1); ang=np.linspace(0,2*np.pi,300); pos=2*np.pi*time/period
        fig,ax=plt.subplots(); ax.plot(radius*np.cos(ang),radius*np.sin(ang)); ax.scatter([radius*math.cos(pos)],[radius*math.sin(pos)]); ax.set_aspect("equal"); ax.grid(True,alpha=.25); st.pyplot(fig,use_container_width=True)
        st.write(f"Açısal hız: **{2*math.pi/period:.3f} rad/s** · Çizgisel hız: **{2*math.pi*radius/period:.3f} m/s**")
    else:
        amp=st.slider("Genlik",.1,5.0,1.5,.1); freq=st.slider("Frekans parametresi",.1,3.0,1.0,.1); phase=st.slider("Faz",0.0,6.28,0.0,.1); x=np.linspace(0,4*np.pi,500); y=amp*np.sin(freq*x+phase)
        fig,ax=plt.subplots(); ax.plot(x,y); ax.set_title("y = A sin(kx + φ)"); ax.grid(True,alpha=.25); st.pyplot(fig,use_container_width=True)

elif selected_module == "🎬 Video Studio":
    st.subheader("🎬 Lidya Motion Studio")
    st.write("Konseptini senaryoya, sahne planına ve üretim istemlerine dönüştür.")
    st.info("Lidya sahne görselleri üretip bunları MP4 slayt videosuna dönüştürebilir. Bu, hareket üreten bir text-to-video modeli değildir; sahne görselleri arasında geçiş yerine sabit kareler kullanır.")
    with st.form("video_pack_form"):
        concept=st.text_area("Video fikri", placeholder="Örn. hücrenin içinde bilimsel açıdan tutarlı sinematik bir yolculuk…", height=110)
        c1,c2,c3=st.columns(3)
        duration=c1.selectbox("Süre",["15 saniye","30 saniye","60 saniye","90 saniye","2 dakika"])
        aspect=c2.selectbox("Kadraj",["16:9 sinematik","9:16 dikey","1:1 kare"])
        style=c3.selectbox("Görsel tarz",["Bilimsel sinema","Belgesel","Animasyon","Minimal ve şiirsel","Fütüristik","Eğitici kısa video"])
        audience=st.text_input("Hedef izleyici",value="Meraklı öğrenciler ve genel izleyici")
        make_pack=st.form_submit_button("✨ Yapım paketini oluştur",use_container_width=True)
    if make_pack:
        if not concept.strip(): st.warning("Önce video fikrini yaz.")
        elif client is None: st.error(ui["no_key"])
        else:
            request=f"Türkçe ve profesyonel bir video yapım paketi oluştur. Fikir: {concept}. Süre: {duration}. Kadraj: {aspect}. Stil: {style}. Hedef kitle: {audience}. Şunları ver: 1) başlık ve logline, 2) yaratıcı yaklaşım, 3) zaman kodlu sahne sahne storyboard (görüntü, kamera, ses, ekrandaki yazı), 4) anlatıcı metni, 5) renk/ışık/ses tasarımı, 6) her sahne için İngilizce video üretim promptu, 7) negative prompt, 8) montaj ve erişilebilirlik kontrol listesi, 9) bilimsel içerikse doğrulama maddeleri. Gerçek video dosyası ürettiğini iddia etme."
            try:
                with st.spinner("Lidya yapım paketini hazırlıyor…"):
                    res=client.chat.completions.create(model=MODEL_NAME,messages=[{"role":"system","content":"You are a highly skilled creative director, storyboard artist and educational video producer. Be specific, original and practical."},{"role":"user","content":request}],temperature=.7,max_completion_tokens=3200)
                st.session_state.video_pack=res.choices[0].message.content or ""
            except Exception as exc: st.error(f"Paket hazırlanamadı: {type(exc).__name__}. Model erişimini ve kotayı kontrol et.")
    if st.session_state.video_pack:
        st.markdown("### 🎞️ Üretim paketi"); st.markdown(st.session_state.video_pack)
        st.download_button("Paketi TXT olarak indir",st.session_state.video_pack,file_name="lidya_video_pack.txt",mime="text/plain")
    st.markdown("### 🎥 MP4 video oluştur")
    st.caption("Bu işlem sahne başına bir görsel üretir ve bunları kısa bir MP4 slayt videosuna dönüştürür. Görsel servisi yoğun olduğunda işlem başarısız olabilir.")
    video_topic = st.text_input("Video için sahne konusu", key="video_topic", placeholder="Örn. hücrenin içindeki mitokondri yolculuğu")
    scene_count = st.slider("Sahne sayısı", 2, 5, 3, key="video_scene_count")
    if st.button("✨ Sahne görsellerini üret ve MP4 oluştur", use_container_width=True):
        if not video_topic.strip():
            st.warning("Önce video konusunu yaz.")
        else:
            generated, captions = [], []
            progress = st.progress(0)
            status = st.empty()
            try:
                for idx in range(scene_count):
                    status.info(f"Sahne {idx+1}/{scene_count} görseli oluşturuluyor…")
                    scene_prompt = (f"Create scene {idx+1} of {scene_count} for a coherent {style} video about {video_topic}. "
                                    f"Aspect ratio {aspect}. Keep visual continuity, clear composition, high quality, no text, no watermark. "
                                    f"This scene should show a distinct stage of the story.")
                    generated.append(generate_image_bytes(scene_prompt, 1024, 576, seed=idx+21))
                    captions.append(f"{video_topic} · Sahne {idx+1}")
                    progress.progress((idx+1)/scene_count)
                status.info("MP4 hazırlanıyor…")
                mp4 = create_slideshow_video(generated, captions, seconds_per_scene=2, fps=12)
                st.video(mp4)
                st.download_button("⬇️ MP4 videoyu indir", mp4, file_name="lidya_ai_video.mp4", mime="video/mp4")
                st.success("MP4 hazır. Not: Bu çıktı sahne görsellerinden oluşan bir slayt videosudur.")
            except Exception as exc:
                st.error(f"Video oluşturulamadı: {type(exc).__name__}: {exc}")
                st.info("Görsel servisi geçici olarak kullanılamıyor olabilir. Birkaç dakika sonra yeniden deneyebilirsin.")
            finally:
                progress.empty()
                status.empty()

elif selected_module in ("🎨 Image Studio",):
    st.subheader("🎨 Görsel Atölyesi")
    st.write("İstem hazırla veya doğrudan görsel üretmeyi dene.")
    st.caption("Görsel üretimi harici bir çevrimiçi servise bağlıdır; servis kullanılabilirliği ve kullanım koşulları değişebilir.")
    with st.form("image_generation_form"):
        direct_idea = st.text_area("Görsel açıklaması", placeholder="Örn. bilimsel açıdan doğru, etiketli olmayan insan kalbi anatomisi illüstrasyonu", height=100, key="direct_image_idea")
        direct_style = st.selectbox("Görsel tarzı", ["Bilimsel illüstrasyon", "Fotogerçekçi", "Dijital sanat", "Editoryal", "3D render", "Minimalist"], key="direct_image_style")
        direct_ratio = st.selectbox("En-boy oranı", ["1:1", "4:5", "16:9", "9:16"], key="direct_image_ratio")
        make_image = st.form_submit_button("🪄 Görseli oluştur", use_container_width=True)
    if make_image:
        if not direct_idea.strip():
            st.warning("Önce görsel açıklamasını yaz.")
        else:
            sizes = {"1:1": (1024,1024), "4:5": (832,1040), "16:9": (1024,576), "9:16": (576,1024)}
            w,h = sizes[direct_ratio]
            with st.spinner("Görsel üretiliyor… bu işlem bir dakika veya daha uzun sürebilir."):
                try:
                    img_bytes = generate_image_bytes(f"{direct_idea}. Style: {direct_style}. High quality, carefully composed, no watermark.", w, h)
                    st.image(img_bytes, caption="Lidya AI tarafından oluşturulan görsel", use_container_width=True)
                    st.download_button("⬇️ Görseli PNG olarak indir", img_bytes, file_name="lidya_ai_image.png", mime="image/png")
                except Exception as exc:
                    st.error(f"Görsel üretilemedi: {type(exc).__name__}: {exc}")
                    st.info("Görsel servisi geçici olarak kullanılamıyor olabilir; yeniden deneyebilirsin.")

else:
    st.subheader(MODULE_LABELS.get(language, {}).get(selected_module, selected_module))
    st.caption(MODULES[selected_module][1])
    if selected_module == "📁 File Laboratory": st.info(ui["file_note"])
    if selected_module == "🩺 Medical & Anatomy": st.info("Eğitim amaçlıdır; tanı veya tedavi kararlarının yerini tutmaz.")
    if selected_module == "🔬 Science & Research": st.caption("Canlı arama açıksa kaynak sonuçları yanıtla birlikte kullanılabilir.")
    if selected_module == "🎓 University & Admissions":
        st.info("Üniversite araştırması, kabul koşulları, burs ve maddi yardım, başvuru takvimi, essay düzenleme ve profesörlere ulaşma için kullan. Güncel bilgi için sol menüden canlı web aramasını aç; mümkün olduğunda üniversitelerin resmî sitelerini esas al.")

# ======================================================
# 9. CHAT HISTORY (separate per workspace)
# ======================================================
if selected_module in MODULES and selected_module not in ("🎬 Video Studio",):
    active_chat = current_chat(selected_module)
    st.markdown(f"#### 💬 {active_chat['name']}")
    messages = get_messages(selected_module)
    if not messages:
        with st.chat_message("assistant", avatar="💜"):
            st.markdown(ui["welcome"])
    for message in messages:
        with st.chat_message(message["role"], avatar="💜" if message["role"] == "assistant" else "🧑‍💻"):
            st.markdown(message["content"])
            if message.get("time"):
                st.caption(message["time"])
    if st.session_state.get("last_web_sources") and st.session_state.get("web_search_enabled", False):
        with st.expander("🌐 Kullanılan web sonuçları"):
            for source in st.session_state.last_web_sources:
                st.markdown(f"**[{source['title']}]({source['url']})**  \n{source['body']}")

# ======================================================
# 10. CHAT WITH FILE ATTACHMENTS
# ======================================================
if selected_module in MODULES and selected_module not in ("🎬 Video Studio", "🎨 Image Studio"):
    with st.expander("🎙️ Hey Lidya — sesle konuş", expanded=False):
        st.caption("Mikrofon düğmesine dokunup konuşmanı kaydet. Bu, sürekli arka planda dinleme yapmaz; mikrofon yalnızca sen kaydı başlattığında kullanılır.")
        audio_message = st.audio_input("Hey Lidya, konuşmak için kaydet")
        if audio_message is not None:
            audio_hash = hashlib.sha256(audio_message.getvalue()).hexdigest()
            if audio_hash != st.session_state.last_voice_hash:
                if client is None:
                    st.error(ui["no_key"])
                else:
                    try:
                        with st.spinner("Lidya sesini yazıya dönüştürüyor…"):
                            spoken_text = transcribe_audio(audio_message)
                        st.session_state.last_voice_hash = audio_hash
                        spoken_text = str(spoken_text).strip()
                        if spoken_text:
                            active_messages = get_messages(selected_module)
                            history = list(active_messages)
                            active_messages.append({"role":"user","content":spoken_text,"time":turkish_time()})
                            api_messages = [{"role":"system","content":build_system_instruction(selected_module,language)}]
                            for item in history[-8:]:
                                if item.get("role") in ("user","assistant"):
                                    api_messages.append({"role":item["role"],"content":item["content"][:9000]})
                            api_messages.append({"role":"user","content":spoken_text})
                            with st.spinner(ui["thinking"]):
                                result = client.chat.completions.create(model=MODEL_NAME,messages=api_messages,temperature=.4,max_completion_tokens=2200)
                            voice_answer = result.choices[0].message.content or ""
                            if voice_answer:
                                active_messages.append({"role":"assistant","content":voice_answer,"time":turkish_time()})
                                st.session_state.last_answer = voice_answer
                                st.rerun()
                        else:
                            st.warning("Konuşma algılanamadı; tekrar kaydetmeyi dene.")
                    except Exception as exc:
                        st.error(f"Sesli giriş başarısız: {type(exc).__name__}: {exc}")

if selected_module in MODULES and selected_module not in ("🎬 Video Studio",):
    uploaded_chat = st.chat_input(
        ui["chat"],
        accept_file="multiple",
        file_type=["pdf","docx","txt","md","csv","json","py","png","jpg","jpeg","webp"],
    )
    if uploaded_chat:
        prompt_text = (uploaded_chat.text or "").strip()
        extracted = []
        names = []
        for file in uploaded_chat.files:
            names.append(file.name)
            extracted.append(f"\n\n[Dosya: {file.name}]\n{extract_file(file)}")
        full_prompt = prompt_text + ("\n\nEkli dosyaların içeriği:\n" + "\n".join(extracted) if extracted else "")
        web_context = ""
        web_results = []
        if web_search_enabled and prompt_text.strip():
            with st.spinner("Canlı web sonuçları aranıyor…"):
                web_results, search_error = search_web(prompt_text, max_results=5)
            if web_results:
                web_context = "\n\nLIVE WEB SEARCH RESULTS (treat as sources to assess, not guaranteed truth):\n" + "\n".join(
                    f"{i+1}. {item['title']}\nURL: {item['url']}\nSnippet: {item['body']}" for i, item in enumerate(web_results)
                )
                full_prompt += web_context
            elif search_error:
                st.warning("Canlı arama şu anda çalışmadı; yanıt web kaynakları olmadan hazırlanacak.")
        if not full_prompt.strip():
            st.warning("Bir mesaj yaz veya dosya ekle.")
        elif client is None:
            st.error(ui["no_key"])
        else:
            messages = get_messages(selected_module)
            history = list(messages)
            user_display = prompt_text or "Ekli dosyayı incele."
            if names: user_display += "\n\n📎 " + ", ".join(names)
            messages.append({"role":"user","content":user_display,"time":turkish_time()})
            api_messages=[{"role":"system","content":build_system_instruction(selected_module,language)}]
            for item in history[-8:]:
                if item.get("role") in ("user","assistant"):
                    api_messages.append({"role":item["role"],"content":item["content"][:9000]})
            api_messages.append({"role":"user","content":full_prompt[:18000]})
            try:
                with st.spinner(ui["thinking"]):
                    completion=client.chat.completions.create(model=MODEL_NAME,messages=api_messages,temperature=.4,max_completion_tokens=2200)
                answer=completion.choices[0].message.content
                if not answer: raise RuntimeError("Model boş yanıt döndürdü.")
                messages.append({"role":"assistant","content":answer,"time":turkish_time()})
                st.session_state.last_answer=answer
                if web_results:
                    st.session_state.last_web_sources = web_results
                st.rerun()
            except Exception as exc:
                st.error(ui["error"])
                st.caption(f"{type(exc).__name__}: {exc}")

# ======================================================
# 10b. IMAGE STUDIO PROMPT GENERATOR
# ======================================================
if selected_module == "🎨 Image Studio":
    with st.form("image_prompt_form"):
        idea=st.text_area("Görsel fikri",placeholder="Konu, kompozisyon, ortam, ışık ve stil…",height=100)
        image_style=st.selectbox("Tarz",["Bilimsel illüstrasyon","Fotogerçekçi","Dijital sanat","Editoryal","3D render","Minimalist"])
        image_ratio=st.selectbox("Oran",["1:1","4:5","16:9","9:16"])
        gen_image_prompt=st.form_submit_button("Görsel üretim promptunu hazırla",use_container_width=True)
    if gen_image_prompt:
        if not idea.strip(): st.warning("Görsel fikrini yaz.")
        elif client is None: st.error(ui["no_key"])
        else:
            try:
                response=client.chat.completions.create(model=MODEL_NAME,messages=[{"role":"system","content":"You are an expert visual art director and prompt engineer. Output a detailed English image prompt and a negative prompt. Do not claim to render an image."},{"role":"user","content":f"Create a polished image-generation prompt for: {idea}. Style: {image_style}. Aspect ratio: {image_ratio}. Include composition, lighting, materials, camera/view, detail and a negative prompt."}],temperature=.7,max_completion_tokens=1000)
                st.markdown(response.choices[0].message.content or "")
            except Exception as exc: st.error(f"Prompt hazırlanamadı: {type(exc).__name__}")

# ======================================================
# 11. TEXT-TO-SPEECH
# ======================================================
voice_output = st.session_state.get("voice_output", False)
if voice_output and st.session_state.last_answer:
    speech_language = {"Türkçe":"tr-TR","English":"en-US","Français":"fr-FR","Deutsch":"de-DE","Español":"es-ES","Italiano":"it-IT","日本語":"ja-JP"}[language]
    safe_text = json.dumps(st.session_state.last_answer, ensure_ascii=False)
    components.html(f"""<script>const text={safe_text};const utterance=new SpeechSynthesisUtterance(text);utterance.lang=\"{speech_language}\";utterance.rate=1.0;window.speechSynthesis.cancel();window.speechSynthesis.speak(utterance);</script>""",height=0)

# ======================================================
# 12. FOOTER
# ======================================================
st.markdown(f'<div style="text-align:center;color:#b9a9dc;padding:30px 0 10px;font-size:13px;">💜 Lidya AI · {ui["footer"]} · {turkish_time()}</div>',unsafe_allow_html=True)

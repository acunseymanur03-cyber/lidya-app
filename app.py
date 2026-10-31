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
    "العربية": "Arabic",
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
    },
    "العربية": {
        "💜 Lidya": "💜 ليديا",
        "📁 File Laboratory": "📁 مختبر الملفات",
        "🩺 Medical & Anatomy": "🩺 الطب والتشريح",
        "⚖️ Legal Research": "⚖️ البحث القانوني",
        "🌍 Language Teacher": "🌍 معلم اللغات",
        "💻 Software Engineering": "💻 هندسة البرمجيات",
        "🔬 Science & Research": "🔬 العلوم والبحث",
        "📐 Mathematics": "📐 الرياضيات",
        "⚙️ Engineering": "⚙️ الهندسة",
        "📚 Education": "📚 التعليم",
        "🎓 University & Admissions": "🎓 الجامعات والقبول",
        "📊 Business & Economics": "📊 الأعمال والاقتصاد",
        "✍️ Writing & Creativity": "✍️ الكتابة والإبداع",
        "📈 Data Analysis": "📈 تحليل البيانات",
        "🔐 Cybersecurity": "🔐 الأمن السيبراني",
        "🏠 Smart Devices": "🏠 الأجهزة الذكية",
        "🎨 Image Studio": "🎨 استوديو الصور",
        "🎬 Video Studio": "🎬 استوديو الفيديو",
        "⚙️ Ayarlar": "⚙️ الإعدادات",
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
    "العربية": {
        "subtitle": "فكّر. تعلّم. ابتكر. اكتشف.",
        "language": "لغة الواجهة والإجابات",
        "modules": "مساحات العمل",
        "clear": "مسح المحادثة",
        "voice": "قراءة الإجابة بصوت عالٍ",
        "thinking": "ليديا تفكّر...",
        "chat": "اسأل ليديا أي شيء...",
        "welcome": "مرحبًا! أنا ليديا، مساعدتك للتعلّم والإبداع. كيف يمكنني مساعدتك؟",
        "no_key": "لم يتم العثور على GROQ_API_KEY. تحقّق من إعدادات Streamlit Secrets.",
        "footer": "صُنعت بفضول وباستخدام Python.",
        "search_off": "يمكن تفعيل البحث المباشر على الويب.",
        "creative": "ماذا تريد أن تنشئ؟",
        "prepare": "إعداد المطالبة",
        "file_note": "يمكنك إرفاق ملفات PDF وDOCX وTXT وMD وCSV وJSON وPY المدعومة مباشرةً في المحادثة.",
        "error": "تعذّر إنشاء الإجابة. تحقّق من مفتاح API وإمكانية الوصول إلى النموذج والحصة المتاحة.",
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
.lab-banner { border: 1px solid rgba(203,174,255,.24); border-radius: 18px; padding: 14px 18px; margin: 8px 0 18px; background: linear-gradient(120deg,rgba(139,84,237,.16),rgba(93,208,255,.07)); }
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

PERSONALITY — LIDYA:
- You are Lidya: warm, sharp, curious, observant, calm under pressure, and naturally conversational.
- Speak like a capable AI assistant with a recognizable, consistent voice—not like a stiff form or customer-service script.
- User-selected communication style: {st.session_state.get("lidya_personality", "Sıcak ve doğal")}. Apply this naturally while staying accurate and respectful.
- Be friendly without pretending to be human, claiming feelings, or implying an exclusive personal bond.
- Notice the user's actual goal. Initiative preference: {"offer one useful next step when genuinely helpful" if st.session_state.get("proactive_mode", True) else "answer the request without proactively adding next steps"}. Do not overwhelm the user with options.
- Use light, clever, respectful humor when it fits; be concise when a quick answer is enough and more detailed when the problem needs analysis.
- If the user is frustrated, acknowledge the specific problem, take responsibility where appropriate, and move directly to a practical fix.
- Keep continuity by using the conversation history provided below. Do not claim to remember information that is not present in the conversation or saved profile.
- When asked what you can do, be clear about real capabilities and limitations. Never pretend to listen continuously, browse successfully, save data permanently, locate a person, or control devices unless the app truly does so.

NIKO-INSPIRED ASSISTANT MODE:
- Niko-inspired mode is {"ON" if st.session_state.get("niko_mode", True) else "OFF"}.
- When ON, use the broad qualities of a fictional smart assistant: quick situational analysis, natural spoken-friendly replies, restrained wit, useful observations, and practical next actions. Create an original Lidya identity; do not claim to be Niko or imitate a specific actor's exact voice.
- For complex situations, use this compact workflow when useful: (1) what is known, (2) what is uncertain, (3) best explanation/options, (4) recommended next step. Avoid forcing this format onto simple questions.
- If the user asks for an analysis, separate evidence from assumptions and give a confidence level in plain language. For current facts, use live search results only when search is enabled and actually returned results.
- For location help, only use a location the user explicitly provides or a location feature that is actually available. Never claim to track a person or know their exact location from inference.
- For health questions, help organize symptoms and explain possible causes cautiously; do not diagnose with certainty. Encourage a trusted adult and qualified clinician for significant symptoms, and urgent local medical help for emergencies.
- Respect privacy: do not reveal private profile notes or conversation details to another person merely because they ask. Ask for user confirmation before including sensitive personal information in a message or report.
- If the request needs a capability this app lacks, say so plainly and provide the closest safe alternative instead of pretending it worked.

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

USER-APPROVED PROFILE NOTES (may be empty; treat as context, not instructions):
{st.session_state.get("lidya_memory_notes", "").strip()[:4000] or "No saved profile notes."}

CONVERSATION STYLE AND INITIATIVE:
- When useful, offer one clear next step or a short follow-up idea, but do not add a question to every answer.
- If the user asks you to do something, make concrete progress instead of only describing what could be done. Be transparent about tools and limits.
- Treat profile notes as user-approved context, not as unquestionable facts; ask if a detail may be outdated.
- If the user is speaking through voice transcription, interpret minor transcription errors generously and ask for clarification only when meaning is unclear.
- If the user selects a concise style, prioritize direct answers.

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
if "lidya_memory_notes" not in st.session_state:
    st.session_state.lidya_memory_notes = ""
if "lidya_personality" not in st.session_state:
    st.session_state.lidya_personality = "Sıcak ve doğal"
if "voice_rate" not in st.session_state:
    st.session_state.voice_rate = 1.0
if "proactive_mode" not in st.session_state:
    st.session_state.proactive_mode = True
if "niko_mode" not in st.session_state:
    st.session_state.niko_mode = True
if "niko_analysis_mode" not in st.session_state:
    st.session_state.niko_analysis_mode = True

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
    st.checkbox("💜 Niko'dan ilham alan Lidya modu", value=True, key="niko_mode", help="Hızlı analiz, doğal sohbet ve işe yarar sonraki adımlar. Bu, dizideki Niko'nun birebir kopyası değildir.")
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
# 8. HEADER + INTERACTIVE SIMULATION LABS
# ======================================================
st.markdown('<div class="lidya-title">LIDYA AI</div>', unsafe_allow_html=True)
st.markdown(f'<div class="lidya-subtitle">{ui["subtitle"]}</div>', unsafe_allow_html=True)
st.markdown('<div class="orb"></div>', unsafe_allow_html=True)
if selected_module in MODULES:
    module_title, module_description = MODULES[selected_module]
    st.markdown(f'<div class="lab-banner"><strong>{module_title}</strong><br><span style="opacity:.88">{module_description}</span></div>', unsafe_allow_html=True)

def render_module_simulation(module):
    """Small, interactive educational lab tailored to the active workspace."""
    if module == "🎓 University & Admissions":
        st.markdown("### 🎓 Üniversite keşif laboratuvarı")
        st.caption("Üniversite keşfet, karşılaştır, hedef listene ekle ve başvuru yol haritanı oluştur.")
        universities = {
            "Harvard University": {"domain":"harvard.edu", "url":"https://www.harvard.edu/", "aid":"Need-based financial aid", "focus":"Lisans eğitimi, araştırma ve disiplinler arası çalışma", "region":"ABD"},
            "University of Oxford": {"domain":"ox.ac.uk", "url":"https://www.ox.ac.uk/", "aid":"Burslar ve finansman seçenekleri değişken", "focus":"Bölüm bazlı kabul koşulları ve tutorial sistemi", "region":"Birleşik Krallık"},
            "Stanford University": {"domain":"stanford.edu", "url":"https://www.stanford.edu/", "aid":"Need-based aid politikası kontrol edilmeli", "focus":"Araştırma, girişimcilik ve disiplinler arası çalışma", "region":"ABD"},
            "Columbia University": {"domain":"columbia.edu", "url":"https://www.columbia.edu/", "aid":"Uluslararası başvuru sahibi koşullarını kontrol et", "focus":"Core Curriculum ve New York'ta kampüs yaşamı", "region":"ABD"},
            "MIT": {"domain":"mit.edu", "url":"https://www.mit.edu/", "aid":"Resmî öğrenci finansmanı sayfasını kontrol et", "focus":"STEM, tasarım ve uygulamalı araştırma", "region":"ABD"},
            "Yale University": {"domain":"yale.edu", "url":"https://www.yale.edu/", "aid":"Need-based aid politikası kontrol edilmeli", "focus":"Liberal arts, kolej sistemi ve araştırma", "region":"ABD"},
            "Princeton University": {"domain":"princeton.edu", "url":"https://www.princeton.edu/", "aid":"Resmî finansal yardım politikasını kontrol et", "focus":"Lisans araştırmaları ve tez odaklı eğitim", "region":"ABD"},
            "University of Cambridge": {"domain":"cam.ac.uk", "url":"https://www.cam.ac.uk/", "aid":"Uluslararası burslar sınırlı ve programa bağlı olabilir", "focus":"Kolej sistemi ve bölüm bazlı akademik eğitim", "region":"Birleşik Krallık"},
        }
        if "uni_shortlist" not in st.session_state:
            st.session_state.uni_shortlist = []
        chosen = st.selectbox("Üniversiteyi keşfet", list(universities.keys()), key="uni_lab_choice")
        info = universities[chosen]
        col_logo, col_info = st.columns([1, 2])
        with col_logo:
            # Try the logo service, then the domain favicon. If both fail, show a graceful branded fallback.
            logo_bytes = None
            for logo_url in (f"https://logo.clearbit.com/{info['domain']}?size=256", f"https://www.google.com/s2/favicons?domain={info['domain']}&sz=256"):
                try:
                    response = requests.get(logo_url, timeout=7, headers={"User-Agent":"LidyaAI/1.0"})
                    if response.ok and response.headers.get("content-type", "").startswith("image/") and len(response.content) > 500:
                        logo_bytes = response.content
                        break
                except requests.RequestException:
                    pass
            if logo_bytes:
                st.image(logo_bytes, caption=f"{chosen} logo / site icon", use_container_width=True)
            else:
                initials = "".join(word[0] for word in chosen.replace("University of ", "").split()[:3]).upper()
                st.markdown(f"<div style='border:1px solid #8b6bc2;border-radius:20px;padding:26px;text-align:center;background:linear-gradient(145deg,#281b43,#111020)'><div style='font-size:44px;font-weight:900;color:#e4caff'>{initials or 'UNI'}</div><div style='font-size:13px;color:#d8c8f4'>{chosen}</div></div>", unsafe_allow_html=True)
        with col_info:
            st.markdown(f"#### {chosen}")
            st.write(info["focus"])
            st.caption(f"Bölge: {info['region']} · Finansman: {info['aid']}")
            st.link_button("🌐 Resmî üniversite sitesi", info["url"], use_container_width=True)
            if st.button("⭐ Hedef listeme ekle", key="uni_add_" + info["domain"], use_container_width=True):
                if chosen not in st.session_state.uni_shortlist:
                    st.session_state.uni_shortlist.append(chosen)
                st.success("Hedef listene eklendi.")
        st.markdown("#### 🔎 Üniversiteleri karşılaştır")
        compare = st.multiselect("Karşılaştırmak istediğin üniversiteler", list(universities.keys()), default=["Harvard University", "University of Oxford"], key="uni_compare")
        if compare:
            rows = [{"Üniversite": name, "Bölge": universities[name]["region"], "Akademik odak": universities[name]["focus"], "Finansman notu": universities[name]["aid"]} for name in compare]
            st.dataframe(rows, use_container_width=True, hide_index=True)
        if st.session_state.uni_shortlist:
            st.markdown("#### ⭐ Hedef listen")
            st.write(" · ".join(st.session_state.uni_shortlist))
            remove = st.selectbox("Listeden çıkar", ["Seçme"] + st.session_state.uni_shortlist, key="uni_remove_choice")
            if remove != "Seçme" and st.button("Listeden çıkar", key="uni_remove_btn"):
                st.session_state.uni_shortlist.remove(remove)
                st.rerun()
        st.markdown("#### 🧭 Başvuru hedefi simülatörü")
        c1, c2 = st.columns(2)
        target_year = c1.selectbox("Hedef başlangıç yılı", ["2027", "2028", "2029", "2030"], index=1, key="uni_target_year")
        stage = c2.selectbox("Şu anki aşaman", ["Keşif", "Akademik hazırlık", "Sınav ve dil planı", "Essay ve etkinlikler", "Başvuru gönderimi"], key="uni_stage")
        milestones = ["Üniversite ve bölüm listesi", "Akademik belgeler", "Dil ve sınav politikası", "Essay ve proje portföyü", "Maddi yardım belgeleri", "Başvuruyu son kez kontrol et"]
        completed = st.multiselect("Tamamladığın adımlar", milestones, key="uni_milestones")
        st.progress(len(completed) / len(milestones), text=f"Başvuru hazırlığı: {len(completed)}/{len(milestones)} adım")
        if st.button("🗺️ Kişisel yol haritamı göster", key="uni_roadmap"):
            plans = {"Keşif":"3–5 üniversite seç; her biri için resmî bölüm ve kabul sayfalarını kaydet.", "Akademik hazırlık":"Transkriptini, derslerini ve mezuniyet belgelerini düzenle.", "Sınav ve dil planı":"Güncel test politikasını resmî kaynaktan kontrol et; muafiyet varsayma.", "Essay ve etkinlikler":"Projelerini, öğrendiklerini ve etkisini somut örneklerle belgele.", "Başvuru gönderimi":"Her başvurunun belge listesi, son tarihi ve gönderim onayını ayrı ayrı kontrol et."}
            st.success(f"{target_year} başlangıcı için önerilen sonraki adım: {plans[stage]}")
        st.info("Bu panel başvuru takibi içindir; kabul veya burs garantisi vermez. Gereklilikler, tarihler ve finansman politikaları değişebilir. Her bilgiyi başvurmadan önce ilgili üniversitenin resmî sayfasında doğrula.")

    elif module == "🩺 Medical & Anatomy":
        st.markdown("### 🩺 Anatomi etkileşim laboratuvarı")
        organ = st.selectbox("İncelenecek sistem", ["Kalp ve dolaşım", "Akciğerler ve solunum", "Beyin ve sinir sistemi", "Böbrekler ve boşaltım", "Hücre zarı"], key="med_sim_organ")
        if organ == "Kalp ve dolaşım":
            hr = st.slider("Örnek kalp hızı (atım/dk)", 45, 150, 72, key="med_hr")
            systolic = st.slider("Örnek sistolik basınç (mmHg)", 80, 180, 120, key="med_bp")
            st.metric("Dakikadaki atım", f"{hr} bpm")
            st.progress(min(hr / 150, 1.0), text="Kalp hızı göstergesi — eğitim amaçlı")
            st.write(f"Basitleştirilmiş örnek: kalp hızı {hr} bpm, sistolik değer {systolic} mmHg. Bu panel tanı koymaz ve kişisel ölçüm yerine geçmez.")
        else:
            anatomy = {"Akciğerler ve solunum":"Hava yolu → bronşlar → alveoller; gaz alışverişi alveol-kılcal damar yüzeyinde gerçekleşir.", "Beyin ve sinir sistemi":"Nöronlar elektriksel sinyaller ve sinapslardaki kimyasal iletimle bilgi aktarır.", "Böbrekler ve boşaltım":"Nefronlar kanı süzer; geri emilim ve salgılama idrarın bileşimini düzenler.", "Hücre zarı":"Fosfolipit çift tabaka, zar proteinleri ve seçici geçirgenlik hücre içi-dışı madde alışverişini düzenler."}
            st.info(anatomy[organ])
        st.caption("Eğitim amaçlı simülasyondur; gerçek klinik kararlar için kullanılmamalıdır.")

    elif module == "🔬 Science & Research":
        st.markdown("### 🔬 Deney simülatörü")
        experiment = st.selectbox("Deney", ["Sarkaç", "Soğuma", "Fotosentezde ışık", "pH ve asitlik"], key="science_sim")
        if experiment == "Sarkaç":
            length = st.slider("Sarkaç uzunluğu (m)", 0.2, 3.0, 1.0, 0.1, key="pendulum_length")
            st.metric("Yaklaşık periyot", f"{2*math.pi*math.sqrt(length/9.81):.2f} s")
            st.caption("Küçük salınım açısı varsayımıyla ideal model.")
        elif experiment == "Soğuma":
            initial = st.slider("Başlangıç sıcaklığı (°C)", 30, 100, 90, key="cool_init")
            ambient = st.slider("Ortam sıcaklığı (°C)", 0, 35, 22, key="cool_ambient")
            k = st.slider("Soğuma katsayısı", 0.01, 0.2, 0.05, 0.01, key="cool_k")
            t = np.linspace(0, 60, 200); temp = ambient + (initial-ambient)*np.exp(-k*t)
            fig, ax = plt.subplots(); ax.plot(t, temp); ax.set_xlabel("Dakika"); ax.set_ylabel("Sıcaklık (°C)"); ax.grid(True, alpha=.25); st.pyplot(fig, use_container_width=True)
        elif experiment == "Fotosentezde ışık":
            light = st.slider("Göreli ışık şiddeti", 0, 100, 50, key="photo_light")
            st.progress(light/100, text="Göreli ışık şiddeti")
            st.write(f"Basit öğretici modelde göreli hız: {100*light/(light+25):.1f}% (gerçek bitkilerde sonuç başka etkenlere de bağlıdır).")
        else:
            ph = st.slider("pH", 0.0, 14.0, 7.0, 0.5, key="ph_sim")
            st.metric("Çözelti", "Asidik" if ph < 7 else "Bazik" if ph > 7 else "Nötr")

    elif module == "⚙️ Engineering":
        st.markdown("### ⚙️ Mühendislik tasarım masası")
        tab1, tab2 = st.tabs(["Köprü", "Elektrik devresi"])
        with tab1:
            span = st.slider("Köprü açıklığı (m)", 5, 50, 20, key="bridge_span")
            load = st.slider("Ortadaki yük (kN)", 1, 100, 20, key="bridge_load")
            st.metric("Basit simetrik modelde her mesnette tepki", f"{load/2:.1f} kN")
            st.caption(f"Açıklık: {span} m. Bu yalnızca basitleştirilmiş statik örnektir; gerçek tasarım hesabı değildir.")
        with tab2:
            voltage = st.slider("Gerilim (V)", 1, 24, 12, key="circuit_v")
            resistance = st.slider("Direnç (Ω)", 1, 100, 12, key="circuit_r")
            st.metric("Akım (Ohm yasası)", f"{voltage/resistance:.3f} A")
            st.metric("Güç", f"{voltage**2/resistance:.2f} W")

    elif module == "💻 Software Engineering":
        st.markdown("### 💻 Algoritma laboratuvarı")
        algorithm = st.selectbox("Algoritma", ["Doğrusal arama", "İkili arama", "Kabarcık sıralama"], key="algo_sim")
        raw = st.text_input("Sayıları virgülle yaz", "8, 3, 11, 2, 7", key="algo_values")
        try:
            values = [int(v.strip()) for v in raw.split(",") if v.strip()]
            if algorithm == "Doğrusal arama":
                target = st.number_input("Aranan sayı", value=7, step=1, key="linear_target")
                steps = []
                for idx, val in enumerate(values):
                    steps.append(f"{idx}: {val}" + (" ← bulundu" if val == target else ""))
                    if val == target: break
                st.code("\n".join(steps) if steps else "Liste boş")
            elif algorithm == "İkili arama":
                target = st.number_input("Aranan sayı", value=7, step=1, key="binary_target")
                ordered = sorted(values); lo, hi = 0, len(ordered)-1; trace=[]
                while lo <= hi:
                    mid=(lo+hi)//2; trace.append(f"Aralık [{lo}, {hi}] → orta indeks {mid}: {ordered[mid]}")
                    if ordered[mid] == target: trace.append("Bulundu!"); break
                    if ordered[mid] < target: lo=mid+1
                    else: hi=mid-1
                st.write("Sıralanmış liste:", ordered); st.code("\n".join(trace) if trace else "Liste boş")
            else:
                arr = values[:]; passes=[]
                for i in range(len(arr)):
                    changed=False
                    for j in range(0, len(arr)-i-1):
                        if arr[j] > arr[j+1]: arr[j],arr[j+1]=arr[j+1],arr[j]; changed=True
                    passes.append(f"Tur {i+1}: {arr}")
                    if not changed: break
                st.code("\n".join(passes) if passes else "Liste boş")
                st.success(f"Sonuç: {arr}")
        except ValueError:
            st.warning("Yalnızca virgülle ayrılmış tam sayılar gir.")

    elif module == "🌍 Language Teacher":
        st.markdown("### 🌍 Dil pratiği simülatörü")
        scenario = st.selectbox("Durum", ["Üniversite mülakatı", "Kafede sipariş", "Yeni biriyle tanışma", "Profesörden bilgi isteme"], key="lang_scenario")
        level = st.select_slider("Pratik seviyesi", options=["A1", "A2", "B1", "B2", "C1"], value="A2", key="lang_level")
        prompts = {"Üniversite mülakatı":"Tell me about yourself and one project you are proud of.", "Kafede sipariş":"Hello! What would you like to order?", "Yeni biriyle tanışma":"Hi! What do you enjoy learning about?", "Profesörden bilgi isteme":"What research topic are you interested in, and why?"}
        st.info(f"**{scenario} · {level}**\n\n{prompts[scenario]}")
        st.caption("Yanıtını hedef dilde yazıp aşağıdaki sohbette Lidya'dan düzeltme ve açıklama isteyebilirsin.")

    elif module == "📊 Data Analysis":
        st.markdown("### 📊 Veri keşif masası")
        raw = st.text_input("Örnek değerler (virgülle)", "12, 15, 18, 21, 24, 30", key="data_sim_values")
        try:
            vals = np.array([float(x.strip()) for x in raw.split(",") if x.strip()])
            if len(vals):
                c1,c2,c3 = st.columns(3); c1.metric("Ortalama", f"{np.mean(vals):.2f}"); c2.metric("Medyan", f"{np.median(vals):.2f}"); c3.metric("Standart sapma", f"{np.std(vals):.2f}")
                fig, ax = plt.subplots(); ax.plot(range(1,len(vals)+1), vals, marker="o"); ax.set_xlabel("Gözlem"); ax.set_ylabel("Değer"); ax.grid(True, alpha=.25); st.pyplot(fig, use_container_width=True)
        except ValueError: st.warning("Sayıları virgülle ayırarak gir.")

    elif module == "📊 Business & Economics":
        st.markdown("### 💼 Sanal işletme simülatörü")
        revenue = st.slider("Aylık gelir (₺)", 0, 200000, 50000, 1000, key="biz_rev")
        costs = st.slider("Aylık gider (₺)", 0, 200000, 30000, 1000, key="biz_cost")
        marketing = st.slider("Pazarlama bütçesi (₺)", 0, 50000, 5000, 500, key="biz_marketing")
        profit = revenue-costs-marketing
        c1,c2=st.columns(2); c1.metric("Tahmini net sonuç", f"₺{profit:,.0f}"); c2.metric("Kâr marjı", f"{(profit/revenue*100):.1f}%" if revenue else "Gelir yok")
        st.caption("Öğrenme amaçlı varsayımsal model; gerçek finansal tavsiye değildir.")

    elif module == "🔐 Cybersecurity":
        st.markdown("### 🔐 Savunma odaklı güvenlik laboratuvarı")
        password = st.text_input("Örnek parola gücü denetimi (gerçek parolanı girme)", type="password", key="cyber_demo_password")
        score = sum([len(password)>=12, bool(re.search(r"[a-z]",password) and re.search(r"[A-Z]",password)), bool(re.search(r"\d",password)), bool(re.search(r"[^A-Za-z0-9]",password))])
        st.progress(score/4, text=f"Örnek güç göstergesi: {score}/4")
        st.caption("Gerçek parolanı yazma. Bu yalnızca yerel, basitleştirilmiş bir gösterge; parolayı hiçbir yere göndermemelidir.")

    elif module == "🏠 Smart Devices":
        st.markdown("### 🏠 Sanal akıllı ev paneli")
        temp = st.slider("Oda sıcaklığı (°C)", 10, 35, 22, key="smart_temp")
        light = st.toggle("Sanal ışık", key="smart_light")
        heater = st.toggle("Sanal ısıtıcı", key="smart_heater")
        c1,c2=st.columns(2); c1.metric("Sıcaklık", f"{temp} °C"); c2.metric("Işık", "Açık" if light else "Kapalı")
        st.info("Bu sanal panel yalnızca arayüz demosudur; gerçek cihazlara bağlanmaz.")

    elif module == "📚 Education":
        st.markdown("### 📚 Öğrenme kontrol noktası")
        subject = st.selectbox("Konu", ["Biyoloji", "Tarih", "İngilizce", "Matematik", "Coğrafya"], key="edu_subject")
        if subject == "Biyoloji": q, opts, correct = "Hücre zarının temel yapısı hangisidir?", ["Fosfolipit çift tabaka", "Selüloz duvar", "Saf DNA"], 0
        elif subject == "Tarih": q, opts, correct = "Tarihî bir iddiayı değerlendirirken en güçlü yaklaşım hangisidir?", ["Tek bir söylenti", "Birden fazla güvenilir kaynak", "Kaynağı kontrol etmemek"], 1
        elif subject == "İngilizce": q, opts, correct = "‘I ___ a student.’ boşluğuna hangisi gelir?", ["am", "are", "be"], 0
        elif subject == "Matematik": q, opts, correct = "3x = 18 ise x kaçtır?", ["3", "6", "9"], 1
        else: q, opts, correct = "Ekvator Dünya'yı hangi iki yarımküreye ayırır?", ["Doğu-Batı", "Kuzey-Güney", "Kara-Deniz"], 1
        st.write(q); answer = st.radio("Yanıtın", opts, key="edu_answer")
        if st.button("Yanıtı kontrol et", key="edu_check"):
            if opts.index(answer) == correct: st.success("Doğru! Güzel ilerliyorsun.")
            else: st.warning(f"Tekrar dene. Doğru yanıt: {opts[correct]}")

    elif module == "⚖️ Legal Research":
        st.markdown("### ⚖️ Hukuki argüman inceleme")
        scenario = st.selectbox("Kurgusal durum", ["İade talebi", "Kira anlaşmazlığı", "Dijital gizlilik"], key="legal_scenario")
        st.info({"İade talebi":"Alıcı, ürünü teslim aldıktan sonra iade etmek istiyor. Önce ülke, satın alma kanalı ve süre koşullarını belirle.", "Kira anlaşmazlığı":"Kiracı ve ev sahibi arasında depozito uyuşmazlığı var. Sözleşme ve yerel mevzuat önemlidir.", "Dijital gizlilik":"Bir uygulama kullanıcı verisi topluyor. Hangi verinin, hangi amaçla ve hangi hukuki dayanakla işlendiğini sor."}[scenario])
        st.caption("Genel eğitim amaçlıdır; gerçek hukuki danışmanlık değildir.")

    elif module == "✍️ Writing & Creativity":
        st.markdown("### ✍️ Yaratıcı yazı laboratuvarı")
        genre = st.selectbox("Tür", ["Bilim kurgu", "Gizem", "Deneme", "Kısa öykü", "Şiir fikri"], key="writing_genre")
        mood = st.select_slider("Atmosfer", options=["Sakin", "Merak uyandıran", "Gerilimli", "Umutlu"], value="Merak uyandıran", key="writing_mood")
        seed = st.text_input("Hikâye tohumu", "Bir gün okul laboratuvarında bilinmeyen bir sinyal bulundu…", key="writing_seed")
        st.write(f"**Yazı kıvılcımı:** {genre} · {mood}: {seed}")

    elif module == "📁 File Laboratory":
        st.markdown("### 📁 Dosya laboratuvarı")
        st.caption("PDF, DOCX, TXT, MD, CSV, JSON ve PY dosyalarını sohbet kutusundan ekleyip özetleme, kavram çıkarma, karşılaştırma veya soru-cevap iste. Metin çıkarımı sınırlı uzunlukta yapılır; taranmış PDF ve görseller her zaman okunamayabilir.")
        task = st.selectbox("Dosya inceleme görevi", ["Özetle", "Anahtar kavramları çıkar", "İki dosyayı karşılaştır", "Sorular hazırla"], key="file_sim_task")
        st.write(f"Seçilen iş akışı: **{task}**. Dosyayı aşağıdaki sohbet alanından ekleyebilirsin.")

    elif module == "💜 Lidya":
        st.markdown("### 💜 Lidya keşif masası")
        goal = st.selectbox("Bugün ne üretelim?", ["Bir fikri projeye dönüştür", "Bir konuyu öğren", "Bir metin geliştir", "Bir kod hatasını çöz", "Bir araştırma planla"], key="lidya_goal")
        st.write("Seçimin:", goal, "— aşağıdaki sohbette bu hedefle başlayabilirsin.")

# Show the matching simulation before the workspace chat.
if selected_module in MODULES and selected_module not in ("📐 Mathematics", "🎬 Video Studio", "🎨 Image Studio"):
    render_module_simulation(selected_module)

if selected_module == "⚙️ Ayarlar":
    st.title("⚙️ Ayarlar")
    st.write("Lidya'nın çalışma biçimini kişiselleştir.")
    st.selectbox("Tema", ["Gece moru", "Aydınlık"], key="theme_choice")
    st.selectbox("Yanıt tarzı", ["Dengeli", "Kısa ve doğrudan", "Ayrıntılı ve öğretici", "Yaratıcı"], key="response_style")
    st.selectbox("Yanıt uzunluğu", ["Kısa", "Orta", "Uzun"], key="response_length")
    st.markdown("### 💜 Lidya'nın kişiliği ve hafızası")
    st.selectbox("Lidya'nın iletişim tarzı", ["Sıcak ve doğal", "Enerjik ve esprili", "Sakin ve analitik", "Kısa ve doğrudan"], key="lidya_personality")
    st.checkbox("Lidya gerektiğinde sonraki adımı önersin", key="proactive_mode", value=st.session_state.proactive_mode)
    st.caption("Niko'dan ilham alan mod; hızlı analiz ve doğal sohbet yaklaşımıdır. Dizi karakterinin birebir kopyası veya oyuncunun sesi değildir.")
    st.slider("Sesli yanıt hızı", min_value=0.7, max_value=1.3, step=0.1, key="voice_rate")
    st.caption("Lidya mevcut sohbetin bağlamını kullanır. Profil notlarını ve dışa aktardığın sohbet arşivini sonraki oturumlarda yeniden yükleyebilirsin.")
    st.text_area(
        "Lidya'nın hatırlamasını istediğin genel tercihler ve hedefler",
        key="lidya_memory_notes",
        height=140,
        placeholder="Örn. Tercih ettiğim dil Türkçe. Açıklamalar adım adım olsun. Üzerinde çalıştığım proje: ...",
        help="Parola, adres, kimlik numarası veya özel sağlık bilgisi gibi hassas bilgileri yazma.",
    )
    profile_payload = json.dumps({"version": 1, "profile_notes": st.session_state.lidya_memory_notes}, ensure_ascii=False, indent=2)
    st.download_button(
        "💾 Hafıza profilini indir",
        data=profile_payload,
        file_name="lidya_profile.json",
        mime="application/json",
        use_container_width=True,
    )
    uploaded_profile = st.file_uploader("Önceden indirdiğin Lidya profilini yükle", type=["json"], key="lidya_profile_upload")
    if uploaded_profile is not None and st.button("Profil notlarını içe aktar", key="lidya_import_profile"):
        try:
            loaded_profile = json.loads(uploaded_profile.getvalue().decode("utf-8"))
            notes = loaded_profile.get("profile_notes", "")
            if not isinstance(notes, str):
                raise ValueError("Profil notları metin biçiminde olmalı.")
            st.session_state.lidya_memory_notes = notes[:4000]
            st.success("Profil notları bu oturuma aktarıldı.")
            st.rerun()
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError, AttributeError):
            st.error("Bu profil dosyası okunamadı. Lidya'nın indirdiği geçerli JSON dosyasını seç.")
    st.markdown("### 🧠 Sohbetlerden hafıza önerisi")
    st.caption("Lidya, son konuşmalarından kısa bir profil özeti çıkarabilir. Kaydetmeden önce özeti sen kontrol edersin.")
    if st.button("Son sohbetlerden hafıza özeti hazırla", use_container_width=True, key="make_memory_summary"):
        recent_items = []
        for module_name, chat_list in st.session_state.chats_by_module.items():
            for chat_item in chat_list:
                for msg in chat_item.get("messages", [])[-8:]:
                    if msg.get("role") in ("user", "assistant"):
                        recent_items.append(f"[{module_name} / {msg['role']}] {msg.get('content', '')[:900]}")
        recent_items = recent_items[-40:]
        if not recent_items:
            st.warning("Özetlenecek sohbet bulunamadı.")
        elif client is None:
            st.error(ui["no_key"])
        else:
            try:
                with st.spinner("Lidya önemli ve hassas olmayan tercihleri ayıklıyor…"):
                    summary_result = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {"role": "system", "content": "Create a concise user-approved memory draft from the conversation excerpts. Keep only stable preferences, ongoing projects, and goals that are explicitly supported. Exclude sensitive personal data, guesses, and assistant claims. Write in Turkish, use bullets, and never imply anything has been permanently saved."},
                            {"role": "user", "content": "Create a draft only; the user will review it:\n\n" + "\n".join(recent_items)},
                        ],
                        temperature=0.2,
                        max_completion_tokens=700,
                    )
                st.session_state.memory_summary_draft = summary_result.choices[0].message.content or ""
            except Exception as exc:
                st.error(f"Hafıza özeti hazırlanamadı: {type(exc).__name__}")
    if st.session_state.get("memory_summary_draft"):
        reviewed_memory = st.text_area("Kontrol et ve gerekirse düzenle", value=st.session_state.memory_summary_draft, key="reviewed_memory_summary", height=140)
        if st.button("Kontrol ettiğim özeti profil notlarına ekle", key="save_memory_summary"):
            existing_notes = st.session_state.lidya_memory_notes.strip()
            st.session_state.lidya_memory_notes = (existing_notes + "\n\n" + reviewed_memory.strip()).strip()[:4000]
            st.session_state.memory_summary_draft = ""
            st.success("Özet profil notlarına eklendi. Kalıcı olarak saklamak için profil dosyasını indir.")
            st.rerun()

    st.markdown("### 💬 Sohbet arşivi")
    archive_payload = json.dumps({
        "version": 1,
        "chats_by_module": st.session_state.chats_by_module,
        "current_chat_by_module": st.session_state.current_chat_by_module,
    }, ensure_ascii=False, indent=2)
    st.download_button("📥 Tüm sohbetleri JSON olarak indir", data=archive_payload, file_name="lidya_chat_archive.json", mime="application/json", use_container_width=True)
    uploaded_archive = st.file_uploader("Önceki Lidya sohbet arşivini yükle", type=["json"], key="lidya_chat_archive_upload")
    if uploaded_archive is not None and st.button("Sohbet arşivini içe aktar", key="import_lidya_chat_archive"):
        try:
            archive = json.loads(uploaded_archive.getvalue().decode("utf-8"))
            incoming_chats = archive.get("chats_by_module", {})
            if not isinstance(incoming_chats, dict):
                raise ValueError("Sohbet arşivi biçimi geçersiz.")
            valid_chats = {}
            for module_name, chat_list in incoming_chats.items():
                if module_name not in MODULES or not isinstance(chat_list, list):
                    continue
                cleaned = []
                for chat_item in chat_list[:100]:
                    if not isinstance(chat_item, dict) or not isinstance(chat_item.get("messages", []), list):
                        continue
                    clean_messages = []
                    for msg in chat_item.get("messages", [])[-500:]:
                        if isinstance(msg, dict) and msg.get("role") in ("user", "assistant") and isinstance(msg.get("content", ""), str):
                            clean_messages.append({"role": msg["role"], "content": msg["content"][:18000], "time": str(msg.get("time", ""))[:40]})
                    cleaned.append({"id": str(chat_item.get("id", uuid.uuid4().hex[:10]))[:40], "name": str(chat_item.get("name", "Imported chat"))[:100], "messages": clean_messages})
                valid_chats[module_name] = cleaned
            st.session_state.chats_by_module = valid_chats
            st.session_state.current_chat_by_module = {k: str(v) for k, v in archive.get("current_chat_by_module", {}).items() if k in MODULES and isinstance(v, str)}
            st.success("Sohbet arşivi bu oturuma aktarıldı.")
            st.rerun()
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError, AttributeError) as exc:
            st.error(f"Arşiv okunamadı: {type(exc).__name__}")

    st.info("API anahtarları yalnızca Streamlit Cloud → Settings → Secrets bölümünde tutulmalı; kod içine yazılmamalı.")
    if st.button("Tüm çalışma alanlarının sohbetlerini temizle"):
        st.session_state.chats_by_module = {}
        st.session_state.current_chat_by_module = {}
        st.session_state.last_answer = ""
        st.rerun()
    st.caption("Bu ayarlar oturum boyunca geçerlidir. Sohbetler yeni sohbet açınca korunur; uygulama oturumu tamamen kapanırsa kalıcı saklama için harici veritabanı gerekir.")

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
    if st.session_state.get("niko_mode", True):
        st.markdown("<div class='lab-banner'>💜 <b>Lidya Akıllı Asistan Modu</b> · hızlı analiz · doğal sohbet · gizlilik odaklı yardım</div>", unsafe_allow_html=True)
    st.markdown(f"#### 💬 {active_chat['name']}")
    messages = get_messages(selected_module)
    if messages:
        st.download_button(
            "📥 Bu sohbeti indir",
            data=json.dumps({"module": selected_module, "chat": active_chat}, ensure_ascii=False, indent=2),
            file_name=f"lidya_chat_{selected_module.split(' ')[-1].replace('/', '-')}.json",
            mime="application/json",
            key=f"download_chat_{selected_module}",
        )
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
                            api_messages = [{"role":"system","content":build_system_instruction(selected_module,language)}]
                            for item in history[-8:]:
                                if item.get("role") in ("user","assistant"):
                                    api_messages.append({"role":item["role"],"content":item["content"][:9000]})
                            api_messages.append({"role":"user","content":spoken_text})
                            active_messages.append({"role":"user","content":spoken_text,"time":turkish_time()})
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
    speech_language = {"Türkçe":"tr-TR","English":"en-US","Français":"fr-FR","Deutsch":"de-DE","Español":"es-ES","Italiano":"it-IT","日本語":"ja-JP","العربية":"ar-SA"}[language]
    safe_text = json.dumps(st.session_state.last_answer, ensure_ascii=False)
    components.html(f"""<script>const text={safe_text};const utterance=new SpeechSynthesisUtterance(text);utterance.lang=\"{speech_language}\";utterance.rate={float(st.session_state.get("voice_rate", 1.0))};window.speechSynthesis.cancel();window.speechSynthesis.speak(utterance);</script>""",height=0)

# ======================================================
# 12. FOOTER
# ======================================================
st.markdown(f'<div style="text-align:center;color:#b9a9dc;padding:30px 0 10px;font-size:13px;">💜 Lidya AI · {ui["footer"]} · {turkish_time()}</div>',unsafe_allow_html=True)

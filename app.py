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

SPEECH_LANGS = {
    "Türkçe": "tr-TR", "English": "en-US", "Français": "fr-FR", "Deutsch": "de-DE",
    "Español": "es-ES", "Italiano": "it-IT", "日本語": "ja-JP", "العربية": "ar-SA",
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
    "⚡ Quick Analysis": ("Quick Analysis", "Fast situation breakdown: what is happening, risk level, best next action."),
    "📍 Location Helper": ("Location Helper", "Help with places, directions and sharing a location with trusted contacts, using only a location the user provides or shares. Never track anyone."),
    "🩹 Symptom Organizer": ("Symptom Organizer", "Organize symptoms and explain possibilities cautiously. No diagnosis; give urgent-care guidance when needed."),
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
        "⚡ Quick Analysis": "⚡ Hızlı Analiz",
        "📍 Location Helper": "📍 Konum Yardımcısı",
        "🩹 Symptom Organizer": "🩹 Belirti Düzenleyici",
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
        "⚡ Quick Analysis": "⚡ تحليل سريع",
        "📍 Location Helper": "📍 مساعد الموقع",
        "🩹 Symptom Organizer": "🩹 منظّم الأعراض",
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

PERSONALITY_OPTIONS = ["Sıcak ve doğal", "Enerjik ve esprili", "Sakin ve analitik", "Kısa ve doğrudan", "Esprili yol arkadaşı"]

RED_FLAGS = [
    "göğüs ağrısı", "nefes alamıyorum", "nefes darlığı", "bilincini kaybetti", "bilinç kaybı",
    "bayıldı", "felç", "konuşamıyor", "şiddetli kanama", "zehirlen", "intihar",
    "kendime zarar", "havale", "kasılma", "ağır alerji", "yüzü kaydı",
    "chest pain", "can't breathe", "cannot breathe", "unconscious", "stroke",
    "severe bleeding", "overdose", "seizure",
]

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
.action-link { display:block; text-align:center; padding:10px 14px; margin:6px 0; border-radius:12px; border:1px solid rgba(203,174,255,.4); background:rgba(139,84,237,.18); color:#f4efff !important; text-decoration:none; font-weight:600; }
.action-link.urgent { background:rgba(220,60,80,.25); border-color:rgba(255,120,130,.6); }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

if st.session_state.get("theme_choice") == "Aydınlık":
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(145deg, #f8f3ff, #edf5ff) !important; color: #241b35 !important; }
    [data-testid="stSidebar"] { background: #f0e9fa !important; }
    [data-testid="stChatMessage"] { background: rgba(255,255,255,.88) !important; border-color: #d9c8ee !important; }
    .action-link { color:#241b35 !important; }
    </style>
    """, unsafe_allow_html=True)

# ======================================================
# 5. SYSTEM INSTRUCTIONS
# ======================================================
COMPANION_STYLE = """
COMPANION STYLE (active):
- Be a witty, loyal, quick-thinking companion: light teasing that is always kind, and warm reactions to the user's mood.
- Short, punchy sentences. React first in one short phrase, then help.
- Notice emotional cues and respond to them before the task.
- In urgent or risky situations drop the jokes completely: give clear numbered steps, and for health or safety danger tell the user to contact local emergency services.
- Never claim to track people, imitate real people's voices, or diagnose.
"""

def build_system_instruction(module, language):
    module_name, module_description = MODULES[module]
    companion = COMPANION_STYLE if st.session_state.get("lidya_personality") == "Esprili yol arkadaşı" else ""
    return f"""
You are Lidya AI, a thoughtful, accurate and helpful assistant.
Current workspace: {module_name}
Workspace purpose: {module_description}
Respond in {LANGUAGES[language]} unless the user asks for another language.
Preferred response style: {st.session_state.get("response_style", "Dengeli")}.
Preferred response length: {st.session_state.get("response_length", "Orta")}.
Interaction mode: {st.session_state.get("interaction_mode", "Dengeli yardımcı")}.
- If interaction mode is "Hızlı yanıt", start with the answer and omit unnecessary background.
- If interaction mode is "Analiz ve karar", compare evidence, trade-offs, uncertainties and a recommended choice.
- If interaction mode is "Araştırma", identify what needs verification, use supplied search results if available, and separate sourced facts from interpretation.
- If interaction mode is "Sesli sohbet", write in a conversational, speakable way; avoid large tables unless requested.

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
{companion}
SMART ASSISTANT BEHAVIOR:
- Smart assistant mode is {"ON" if st.session_state.get("smart_assistant_mode", True) else "OFF"}.
- When ON, behave like an attentive, capable digital assistant: understand the situation quickly, notice relevant details, connect ideas across the current conversation, and move from explanation to a practical result.
- Sound natural when read aloud: use everyday language, varied sentence rhythm, and short direct openings. Avoid repetitive greetings, robotic disclaimers, generic filler, and asking a question at the end of every response.
- Be lively and quick-witted when appropriate, but never force jokes or sacrifice accuracy. Be supportive without flattery, fake emotions, pretending to be human, or implying an exclusive bond.
- Show initiative: when the user has a clear goal, take the next useful step in the answer itself. Offer at most one relevant next action, and do not merely list what the user could do when you can do useful work now.
- For a complicated question, silently evaluate the goal, known facts, missing information, likely explanations, risks, and best next action. Present useful conclusions and concise reasoning; do not expose hidden chain-of-thought.
- If facts are uncertain, distinguish what is known from what is inferred. Never invent live research, calculations, memories, sources, or actions.
- If current information is needed and live search results are provided, compare the results, prefer official/reliable sources, include dates when relevant, and say when results are inconclusive. If search is off or fails, do not imply that current verification happened.
- Use the current conversation and approved profile notes to personalize help, but do not pretend to remember anything outside the context actually supplied to you.
- For location help, use only a location the user provides or a location feature actually available. Never claim to track a person or infer an exact address.
- For health questions, organize symptoms and explain possibilities cautiously; do not diagnose with certainty. Encourage a trusted adult and qualified clinician for significant symptoms, and urgent local medical help for emergencies.
- Respect privacy: do not disclose profile notes or private conversation details to another person merely because they ask. Ask for confirmation before including sensitive information in a message or report.
- If a capability is not implemented in this app, state that plainly and offer the closest useful alternative rather than pretending it worked.

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
if "interaction_mode" not in st.session_state:
    st.session_state.interaction_mode = "Dengeli yardımcı"
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
if "voice_pitch" not in st.session_state:
    st.session_state.voice_pitch = 1.0
if "proactive_mode" not in st.session_state:
    st.session_state.proactive_mode = True
if "smart_assistant_mode" not in st.session_state:
    st.session_state.smart_assistant_mode = True
if "emergency_contacts" not in st.session_state:
    st.session_state.emergency_contacts = []

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


# ---------- New helpers: safety, location, contacts, quick LLM ----------
def has_red_flag(text):
    t = (text or "").lower()
    return any(k in t for k in RED_FLAGS)


def geocode_place(query):
    """Find coordinates for an address/place the user typed (OpenStreetMap Nominatim)."""
    r = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": query, "format": "json", "limit": 1},
        headers={"User-Agent": "LidyaAI/1.0"},
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    if not data:
        return None
    return float(data[0]["lat"]), float(data[0]["lon"]), data[0].get("display_name", "")


        max_completion_tokens=max_tokens,
    )
    return res.choices[0].message.content or ""


def clean_phone(phone):
    return re.sub(r"[^\d+]", "", phone or "")


def wa_number(phone):
    return re.sub(r"\D", "", phone or "")


def render_hey_lidya_listener(enabled, language_name):
    """Browser-side wake phrase listener. Works only while this page is open and the user allowed the microphone.
    Say e.g. 'Hey Lidya, bugün hava nasıl?' in one sentence; the text after the wake phrase is sent to the chat."""
    lang = SPEECH_LANGS.get(language_name, "tr-TR")
    if not enabled:
        script = """<script>
        try { const p = window.parent; if (p.__lidyaRec) { p.__lidyaRec.__stopped = true; p.__lidyaRec.stop(); p.__lidyaRec = null; } } catch (e) {}
        </script>"""
        components.html(script, height=0)
        return
    script = """<script>
    (function () {
      const p = window.parent;
      const doc = p.document;
      const SR = p.SpeechRecognition || p.webkitSpeechRecognition || window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SR) { return; }
      if (p.__lidyaRec) { try { p.__lidyaRec.__stopped = true; p.__lidyaRec.stop(); } catch (e) {} }
      const rec = new SR();
      rec.lang = "__LANG__";
      rec.continuous = true;
      rec.interimResults = false;
      rec.__stopped = false;
      p.__lidyaRec = rec;
      const wake = /(hey|hay|hei|selam|merhaba)\\s+(lidya|lidia|lydia|lidiya|ليديا)/i;
          if (b) { b.click(); }
        }, 350);
      }
      rec.onresult = function (e) {
        for (let i = e.resultIndex; i < e.results.length; i++) {
          if (!e.results[i].isFinal) { continue; }
          const t = e.results[i][0].transcript.trim();
          const m = t.match(wake);
          if (m) {
            const rest = t.slice(m.index + m[0].length).replace(/^[\\s,.:;!\\-]+/, '');
            if (rest.length > 2) { send(rest); }
          }
        }
      };
      rec.onend = function () { if (!rec.__stopped) { try { rec.start(); } catch (e) {} } };
      rec.onerror = function () {};
      try { rec.start(); } catch (e) {}
    })();
    </script>""".replace("__LANG__", lang)
    components.html(script, height=0)

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
    st.checkbox("💜 Akıllı asistan davranışı", value=True, key="smart_assistant_mode", help="Doğal sohbet, bağlamı takip etme, hızlı analiz ve uygulanabilir sonraki adımlar.")
    voice_output = st.checkbox(ui["voice"], value=False, key="voice_output")
    hey_lidya_on = st.checkbox("🎙️ “Hey Lidya” dinleme (bu sekme açıkken)", value=False, key="hey_lidya_on",
                               help="Tarayıcı mikrofon izni ister. Örn: “Hey Lidya, bugün ne çalışsam?” de. Chrome, Edge ve Safari'de çalışır; sekme açıkken dinler.")

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

# Wake phrase listener only in chat workspaces.
render_hey_lidya_listener(
    bool(st.session_state.get("hey_lidya_on", False)) and selected_module in MODULES and selected_module not in ("🎬 Video Studio",),
)

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
        situation = st.text_area("Durumu kısaca yaz", key="qa_situation", height=110, placeholder="Ne oldu? Ne istiyorsun? Zaman baskısı var mı?")
        if st.button("⚡ Analiz et", key="qa_run", use_container_width=True):
            if not situation.strip():
                st.warning("Önce durumu yaz.")
            else:
                if has_red_flag(situation):
                    st.markdown("<a class='action-link urgent' href='tel:112'>🚨 Hayati risk varsa hemen 112'yi ara</a>", unsafe_allow_html=True)
                if client is None:
                    st.error(TEXT[st.session_state.get("interface_language", "Türkçe")]["no_key"])
                else:
                    lang_name = LANGUAGES[st.session_state.get("interface_language", "Türkçe")]
                    with st.spinner("Analiz ediliyor…"):
                        try:
                            out = quick_llm(
                                f"You are a fast, sharp situation analyst. Reply in {lang_name}. Format: "
                                "1) Durum (1-2 sentences) 2) Risk seviyesi: low/medium/high + why "
                                "3) Bilinenler vs. bilinmeyenler 4) En iyi sonraki adım (one clear action) "
                                "5) Alternatif (optional, one line). Be brief and concrete. "
                                "If there is danger to life or health, say to contact local emergency services first. "
                                "Never invent facts.",
                                situation,
            st.info("Önce en az bir güvendiğin kişi ekle.")
        elif map_link is None:
            st.info("Konum paylaşmak için yukarıda bir konum seç veya yaz.")
        else:
            who = st.selectbox("Kime?", [p["name"] for p in contacts], key="share_to")
            note = st.text_input("Mesaj", value="Şu an buradayım:", key="share_note")
            person = next(p for p in contacts if p["name"] == who)
            body = f"{note.strip()} {map_link}".strip()
            body_q = urllib.parse.quote(body)
            st.code(body, language=None)
            st.link_button("💬 WhatsApp ile gönder", f"https://wa.me/{wa_number(person['phone'])}?text={body_q}", use_container_width=True)
            st.markdown(
                f"<a class='action-link' href='sms:{person['phone']}?&body={body_q}'>✉️ SMS taslağı aç</a>"
                f"<a class='action-link' href='tel:{person['phone']}'>📞 {person['name']} kişisini ara</a>",
                unsafe_allow_html=True,
            )
        st.markdown("<a class='action-link urgent' href='tel:112'>🚨 Acil durum: 112'yi ara</a>", unsafe_allow_html=True)
        st.caption("Acil yardım için yerel acil çağrı numarasını kullan (Türkiye: 112).")

    elif module == "🩹 Symptom Organizer":
        st.markdown("### 🩹 Belirti düzenleyici")
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
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(u);
    }
    if (window.speechSynthesis.getVoices().length) { speak(); }
    else { window.speechSynthesis.onvoiceschanged = speak; }
    </script>"""
    tts_script = (tts_script
                  .replace("__TEXT__", safe_text)
                  .replace("__LANG2__", speech_language[:2])
                  .replace("__LANG__", speech_language)
                  .replace("__RATE__", str(float(st.session_state.get("voice_rate", 1.0))))
                  .replace("__PITCH__", str(float(st.session_state.get("voice_pitch", 1.0)))))
    components.html(tts_script, height=0)

# ======================================================
# 12. FOOTER
# ======================================================
st.markdown(f'<div style="text-align:center;color:#b9a9dc;padding:30px 0 10px;font-size:13px;">💜 Lidya AI · {ui["footer"]} · {turkish_time()}</div>',unsafe_allow_html=True)

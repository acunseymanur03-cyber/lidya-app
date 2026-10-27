import os
import io
import json
import base64
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st
import requests
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from groq import Groq

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None


# =========================================================
# 1. CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Lidya AI",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)

CHAT_MODEL = "openai/gpt-oss-20b"
IMAGE_MODEL = "@cf/black-forest-labs/flux-1-schnell"
MAX_FILE_SIZE = 10 * 1024 * 1024

def secret(name):
    try:
        value = st.secrets.get(name)
        if value:
            return value
    except Exception:
        pass
    return os.getenv(name)

GROQ_API_KEY = secret("GROQ_API_KEY")
CF_ACCOUNT_ID = secret("CLOUDFLARE_ACCOUNT_ID")
CF_API_TOKEN = secret("CLOUDFLARE_API_TOKEN")


# =========================================================
# 2. LANGUAGES
# =========================================================

LANGUAGES = {
    "Türkçe 🇹🇷": "tr",
    "English 🇬🇧": "en",
    "Français 🇫🇷": "fr",
    "Deutsch 🇩🇪": "de",
    "Español 🇪🇸": "es",
    "Italiano 🇮🇹": "it",
    "日本語 🇯🇵": "ja",
    "简体中文 🇨🇳": "zh",
    "العربية 🇸🇦": "ar",
}

# Arayüzün temel metinleri seçilen dile göre değişir.
UI = {
    "tr": {
        "workspace": "Çalışma alanı",
        "chat": "💜 Lidya ile Sohbet",
        "file": "📁 Dosya Laboratuvarı",
        "medical": "🫀 Tıp ve Anatomi",
        "legal": "⚖️ Hukuk Araştırmaları",
        "language": "🌍 Dil Öğretmeni",
        "coding": "💻 Yazılım Mühendisliği",
        "science": "🔬 Bilim ve Araştırma",
        "math": "📐 Matematik",
        "engineering": "⚙️ Mühendislik",
        "education": "🎓 Eğitim",
        "business": "📊 İşletme ve Ekonomi",
        "writing": "✍️ Yazma ve Yaratıcılık",
        "data": "📈 Veri Analizi",
        "cyber": "🛡️ Siber Güvenlik",
        "devices": "🔌 Akıllı Cihazlar",
        "image": "🎨 Görsel Atölyesi",
        "video": "🎬 Video Atölyesi",
        "sim": "🪐 Simülasyonlar",
        "history": "🏛️ Tarih Araştırmaları",
        "university": "🎓 Üniversite Araştırmaları",
        "karaoke": "🎤 Şarkı ve Ses Laboratuvarı",
        "tagline": "Düşün. Öğren. Üret. Keşfet.",
        "welcome": "Merhaba! Bugün ne öğrenmek veya üretmek istiyorsun?",
        "prompt": "Lidya'ya bir şey sor...",
        "thinking": "Lidya düşünüyor...",
        "new": "➕ Yeni sohbet",
        "clear": "🧹 Sohbeti temizle",
        "send": "Gönder",
        "upload": "Dosya yükle",
        "analyze": "Analiz et",
        "question": "Dosyayla ilgili ne yapmamı istiyorsun?",
        "image_prompt": "Nasıl bir görsel oluşturalım?",
        "make_image": "✨ Görsel oluştur",
        "video_prompt": "Video için bir sahne tarif et",
        "make_video": "🎬 Animasyonlu MP4 oluştur",
        "simulation": "Lidya Simülasyon Laboratuvarı",
        "simulation_desc": "Matematik ve bilim modellerini etkileşimli olarak keşfet.",
        "sim_type": "Simülasyon türü",
        "projectile": "🚀 Fırlatma hareketi",
        "orbit": "🪐 Yörünge modeli",
        "function": "📈 Fonksiyon grafiği",
        "wave": "〰️ Dalga simülasyonu",
        "angle": "Fırlatma açısı",
        "velocity": "Başlangıç hızı",
        "gravity": "Yerçekimi",
        "frequency": "Frekans",
        "amplitude": "Genlik",
        "result": "Sonuç",
        "remember": "🧠 Bu bilgiyi oturum hafızasına kaydet",
        "memory": "Oturum hafızası",
        "voice": "🎙️ Ses kaydı",
        "transcribe": "Sesi yazıya çevir",
        "read": "🔊 Son yanıtı sesli oku",
        "notice": "Tıp ve hukuk konularında uzman görüşünü doğrula.",
        "missing_key": "Sohbet için Streamlit Secrets bölümüne GROQ_API_KEY eklemelisin.",
        "missing_cf": "Görsel üretimi için Cloudflare hesap bilgileri gerekli.",
        "timestamp": "Yerel tarih ve saat",
        "official": "Resmî web sitesi",
        "research": "Araştırma sorusu",
        "research_button": "🔎 Araştırma isteği hazırla",
        "karaoke_help": "Kendi ses kaydını veya kullanma hakkına sahip olduğun bir ses dosyasını yükle. Bu alan henüz otomatik perde ve ritim değerlendirmesi yapmaz.",
        "not_live": "Bu alan tek başına canlı internet araştırması yapmaz. Sonuçları resmî kaynaklardan doğrula.",
    },
    "en": {
        "workspace": "Workspace",
        "chat": "💜 Chat with Lidya",
        "file": "📁 File Laboratory",
        "medical": "🫀 Medicine & Anatomy",
        "legal": "⚖️ Legal Research",
        "language": "🌍 Language Teacher",
        "coding": "💻 Software Engineering",
        "science": "🔬 Science & Research",
        "math": "📐 Mathematics",
        "engineering": "⚙️ Engineering",
        "education": "🎓 Education",
        "business": "📊 Business & Economics",
        "writing": "✍️ Writing & Creativity",
        "data": "📈 Data Analysis",
        "cyber": "🛡️ Cybersecurity",
        "devices": "🔌 Smart Devices",
        "image": "🎨 Image Studio",
        "video": "🎬 Video Studio",
        "sim": "🪐 Simulations",
        "history": "🏛️ History Research",
        "university": "🎓 University Research",
        "karaoke": "🎤 Song & Audio Lab",
        "tagline": "Think. Learn. Create. Explore.",
        "welcome": "Hello! What would you like to learn or create today?",
        "prompt": "Ask Lidya something...",
        "thinking": "Lidya is thinking...",
        "new": "➕ New chat",
        "clear": "🧹 Clear chat",
        "send": "Send",
        "upload": "Upload file",
        "analyze": "Analyze",
        "question": "What should I do with this file?",
        "image_prompt": "Describe the image you want to create",
        "make_image": "✨ Generate image",
        "video_prompt": "Describe a scene for your video",
        "make_video": "🎬 Create animated MP4",
        "simulation": "Lidya Simulation Laboratory",
        "simulation_desc": "Explore mathematical and scientific models interactively.",
        "sim_type": "Simulation type",
        "projectile": "🚀 Projectile motion",
        "orbit": "🪐 Orbital model",
        "function": "📈 Function graph",
        "wave": "〰️ Wave simulation",
        "angle": "Launch angle",
        "velocity": "Initial velocity",
        "gravity": "Gravity",
        "frequency": "Frequency",
        "amplitude": "Amplitude",
        "result": "Result",
        "remember": "🧠 Save this to session memory",
        "memory": "Session memory",
        "voice": "🎙️ Audio recording",
        "transcribe": "Transcribe audio",
        "read": "🔊 Read last answer aloud",
        "notice": "Verify medical and legal information with qualified professionals.",
        "missing_key": "Add GROQ_API_KEY in Streamlit Secrets to enable chat.",
        "missing_cf": "Cloudflare credentials are required for image generation.",
        "timestamp": "Local date and time",
        "official": "Official website",
        "research": "Research question",
        "research_button": "🔎 Prepare research request",
        "karaoke_help": "Upload your own recording or audio you have permission to use. Automatic pitch and rhythm evaluation is not implemented yet.",
        "not_live": "This area does not independently perform live web research. Verify results using official sources.",
    },
    "fr": {
        "workspace": "Espace de travail",
        "chat": "💜 Discuter avec Lidya",
        "file": "📁 Laboratoire de fichiers",
        "medical": "🫀 Médecine et anatomie",
        "legal": "⚖️ Recherche juridique",
        "language": "🌍 Professeur de langues",
        "coding": "💻 Ingénierie logicielle",
        "science": "🔬 Sciences et recherche",
        "math": "📐 Mathématiques",
        "engineering": "⚙️ Ingénierie",
        "education": "🎓 Éducation",
        "business": "📊 Économie et gestion",
        "writing": "✍️ Écriture et créativité",
        "data": "📈 Analyse de données",
        "cyber": "🛡️ Cybersécurité",
        "devices": "🔌 Appareils intelligents",
        "image": "🎨 Atelier d’images",
        "video": "🎬 Atelier vidéo",
        "sim": "🪐 Simulations",
        "history": "🏛️ Recherche historique",
        "university": "🎓 Recherche universitaire",
        "karaoke": "🎤 Laboratoire audio",
        "tagline": "Réfléchir. Apprendre. Créer. Explorer.",
        "welcome": "Bonjour ! Que souhaitez-vous apprendre ou créer aujourd’hui ?",
        "prompt": "Posez une question à Lidya...",
        "thinking": "Lidya réfléchit...",
        "new": "➕ Nouvelle discussion",
        "clear": "🧹 Effacer la discussion",
        "send": "Envoyer",
        "upload": "Téléverser un fichier",
        "analyze": "Analyser",
        "question": "Que dois-je faire avec ce fichier ?",
        "image_prompt": "Décrivez l’image à créer",
        "make_image": "✨ Créer une image",
        "video_prompt": "Décrivez une scène vidéo",
        "make_video": "🎬 Créer une animation MP4",
        "simulation": "Laboratoire de simulation Lidya",
        "simulation_desc": "Explorez des modèles mathématiques et scientifiques.",
        "sim_type": "Type de simulation",
        "projectile": "🚀 Mouvement d’un projectile",
        "orbit": "🪐 Modèle orbital",
        "function": "📈 Graphe de fonction",
        "wave": "〰️ Simulation d’onde",
        "angle": "Angle de lancement",
        "velocity": "Vitesse initiale",
        "gravity": "Gravité",
        "frequency": "Fréquence",
        "amplitude": "Amplitude",
        "result": "Résultat",
        "remember": "🧠 Enregistrer dans la mémoire de session",
        "memory": "Mémoire de session",
        "voice": "🎙️ Enregistrement audio",
        "transcribe": "Transcrire l’audio",
        "read": "🔊 Lire la dernière réponse",
        "notice": "Vérifiez les informations médicales et juridiques auprès de professionnels.",
        "missing_key": "Ajoutez GROQ_API_KEY dans Streamlit Secrets.",
        "missing_cf": "Les identifiants Cloudflare sont requis pour créer des images.",
        "timestamp": "Date et heure locales",
        "official": "Site officiel",
        "research": "Question de recherche",
        "research_button": "🔎 Préparer la recherche",
        "karaoke_help": "Téléversez votre propre enregistrement ou un fichier audio autorisé. L’évaluation automatique de la justesse n’est pas disponible.",
        "not_live": "Cette section ne réalise pas elle-même de recherche Web en direct. Vérifiez les sources officielles.",
    },
}

# D'autres langues ont leurs propres étiquettes principales.
# Les textes non traduits sont fournis en anglais plutôt qu'en turc.
OTHER_LANGS = {
    "de": {
        "workspace": "Arbeitsbereich", "chat": "💜 Mit Lidya chatten",
        "file": "📁 Datei-Labor", "medical": "🫀 Medizin und Anatomie",
        "legal": "⚖️ Rechtsrecherche", "language": "🌍 Sprachlehrer",
        "coding": "💻 Softwareentwicklung", "science": "🔬 Wissenschaft",
        "math": "📐 Mathematik", "engineering": "⚙️ Ingenieurwesen",
        "education": "🎓 Bildung", "business": "📊 Wirtschaft",
        "writing": "✍️ Schreiben", "data": "📈 Datenanalyse",
        "cyber": "🛡️ Cybersicherheit", "devices": "🔌 Smarte Geräte",
        "image": "🎨 Bildstudio", "video": "🎬 Videostudio",
        "sim": "🪐 Simulationen", "history": "🏛️ Geschichte",
        "university": "🎓 Universitätsrecherche",
        "karaoke": "🎤 Audio-Labor",
        "tagline": "Denken. Lernen. Erstellen. Entdecken.",
        "welcome": "Hallo! Was möchtest du heute lernen oder erstellen?",
        "prompt": "Frag Lidya etwas...", "thinking": "Lidya denkt nach...",
        "new": "➕ Neuer Chat", "clear": "🧹 Chat löschen",
        "send": "Senden", "simulation": "Lidya Simulationslabor",
        "simulation_desc": "Erkunde mathematische und wissenschaftliche Modelle.",
        "run_sim": "Simulation starten",
    },
    "es": {
        "workspace": "Espacio de trabajo", "chat": "💜 Chatear con Lidya",
        "file": "📁 Laboratorio de archivos", "medical": "🫀 Medicina y anatomía",
        "legal": "⚖️ Investigación jurídica", "language": "🌍 Profesor de idiomas",
        "coding": "💻 Ingeniería de software", "science": "🔬 Ciencia e investigación",
        "math": "📐 Matemáticas", "engineering": "⚙️ Ingeniería",
        "education": "🎓 Educación", "business": "📊 Economía",
        "writing": "✍️ Escritura", "data": "📈 Análisis de datos",
        "cyber": "🛡️ Ciberseguridad", "devices": "🔌 Dispositivos inteligentes",
        "image": "🎨 Estudio de imágenes", "video": "🎬 Estudio de vídeo",
        "sim": "🪐 Simulaciones", "history": "🏛️ Historia",
        "university": "🎓 Investigación universitaria",
        "karaoke": "🎤 Laboratorio de audio",
        "tagline": "Piensa. Aprende. Crea. Explora.",
        "welcome": "¡Hola! ¿Qué te gustaría aprender o crear hoy?",
        "prompt": "Pregúntale algo a Lidya...", "thinking": "Lidya está pensando...",
        "new": "➕ Nuevo chat", "clear": "🧹 Borrar chat",
        "send": "Enviar", "simulation": "Laboratorio de simulación Lidya",
        "simulation_desc": "Explora modelos matemáticos y científicos.",
    },
    "it": {
        "workspace": "Area di lavoro", "chat": "💜 Chatta con Lidya",
        "file": "📁 Laboratorio file", "medical": "🫀 Medicina e anatomia",
        "legal": "⚖️ Ricerca legale", "language": "🌍 Insegnante di lingue",
        "coding": "💻 Ingegneria del software", "science": "🔬 Scienza e ricerca",
        "math": "📐 Matematica", "engineering": "⚙️ Ingegneria",
        "education": "🎓 Istruzione", "business": "📊 Economia",
        "writing": "✍️ Scrittura", "data": "📈 Analisi dei dati",
        "cyber": "🛡️ Sicurezza informatica", "devices": "🔌 Dispositivi intelligenti",
        "image": "🎨 Studio immagini", "video": "🎬 Studio video",
        "sim": "🪐 Simulazioni", "history": "🏛️ Storia",
        "university": "🎓 Ricerca universitaria",
        "karaoke": "🎤 Laboratorio audio",
        "tagline": "Pensa. Impara. Crea. Esplora.",
        "welcome": "Ciao! Che cosa vorresti imparare o creare oggi?",
        "prompt": "Chiedi qualcosa a Lidya...", "thinking": "Lidya sta pensando...",
        "new": "➕ Nuova chat", "clear": "🧹 Cancella chat",
        "send": "Invia", "simulation": "Laboratorio di simulazione Lidya",
        "simulation_desc": "Esplora modelli matematici e scientifici.",
    },
    "ja": {
        "workspace": "ワークスペース", "chat": "💜 Lidyaとチャット",
        "file": "📁 ファイルラボ", "medical": "🫀 医学と解剖学",
        "legal": "⚖️ 法律リサーチ", "language": "🌍 言語教師",
        "coding": "💻 ソフトウェア工学", "science": "🔬 科学と研究",
        "math": "📐 数学", "engineering": "⚙️ 工学",
        "education": "🎓 教育", "business": "📊 ビジネス",
        "writing": "✍️ 執筆", "data": "📈 データ分析",
        "cyber": "🛡️ サイバーセキュリティ", "devices": "🔌 スマートデバイス",
        "image": "🎨 画像スタジオ", "video": "🎬 動画スタジオ",
        "sim": "🪐 シミュレーション", "history": "🏛️ 歴史研究",
        "university": "🎓 大学調査", "karaoke": "🎤 オーディオラボ",
        "tagline": "考える。学ぶ。創る。探求する。",
        "welcome": "こんにちは！今日は何を学び、何を作りたいですか？",
        "prompt": "Lidyaに質問する...", "thinking": "Lidyaが考えています...",
        "new": "➕ 新しいチャット", "clear": "🧹 チャットを消去",
        "send": "送信", "simulation": "Lidyaシミュレーションラボ",
        "simulation_desc": "数学と科学のモデルを体験しましょう。",
    },
    "zh": {
        "workspace": "工作区", "chat": "💜 与 Lidya 聊天",
        "file": "📁 文件实验室", "medical": "🫀 医学与解剖学",
        "legal": "⚖️ 法律研究", "language": "🌍 语言教师",
        "coding": "💻 软件工程", "science": "🔬 科学与研究",
        "math": "📐 数学", "engineering": "⚙️ 工程学",
        "education": "🎓 教育", "business": "📊 商业与经济",
        "writing": "✍️ 写作", "data": "📈 数据分析",
        "cyber": "🛡️ 网络安全", "devices": "🔌 智能设备",
        "image": "🎨 图像工作室", "video": "🎬 视频工作室",
        "sim": "🪐 模拟实验", "history": "🏛️ 历史研究",
        "university": "🎓 大学研究", "karaoke": "🎤 音频实验室",
        "tagline": "思考。学习。创造。探索。",
        "welcome": "你好！今天你想学习或创作什么？",
        "prompt": "向 Lidya 提问...", "thinking": "Lidya 正在思考...",
        "new": "➕ 新建聊天", "clear": "🧹 清空聊天",
        "send": "发送", "simulation": "Lidya 模拟实验室",
        "simulation_desc": "互动探索数学和科学模型。",
    },
    "ar": {
        "workspace": "مساحة العمل", "chat": "💜 الدردشة مع ليديا",
        "file": "📁 مختبر الملفات", "medical": "🫀 الطب والتشريح",
        "legal": "⚖️ البحث القانوني", "language": "🌍 معلّم اللغات",
        "coding": "💻 هندسة البرمجيات", "science": "🔬 العلوم والبحث",
        "math": "📐 الرياضيات", "engineering": "⚙️ الهندسة",
        "education": "🎓 التعليم", "business": "📊 الأعمال والاقتصاد",
        "writing": "✍️ الكتابة", "data": "📈 تحليل البيانات",
        "cyber": "🛡️ الأمن السيبراني", "devices": "🔌 الأجهزة الذكية",
        "image": "🎨 استوديو الصور", "video": "🎬 استوديو الفيديو",
        "sim": "🪐 المحاكاة", "history": "🏛️ التاريخ",
        "university": "🎓 البحث الجامعي", "karaoke": "🎤 مختبر الصوت",
        "tagline": "فكّر. تعلّم. ابتكر. اكتشف.",
        "welcome": "مرحبًا! ماذا تريد أن تتعلم أو تنشئ اليوم؟",
        "prompt": "اسأل ليديا...", "thinking": "ليديا تفكّر...",
        "new": "➕ محادثة جديدة", "clear": "🧹 مسح المحادثة",
        "send": "إرسال", "simulation": "مختبر محاكاة ليديا",
        "simulation_desc": "استكشف النماذج الرياضية والعلمية بشكل تفاعلي.",
    },
}

for lang, values in OTHER_LANGS.items():
    UI[lang] = {**UI["en"], **values}

for lang in LANGUAGES.values():
    if lang not in UI:
        UI[lang] = dict(UI["en"])

# Eksik anahtarlar İngilizce karşılıklarıyla tamamlanır.
for lang in LANGUAGES.values():
    for key, value in UI["en"].items():
        UI[lang].setdefault(key, value)


# =========================================================
# 3. WORKSPACES AND INSTRUCTIONS
# =========================================================

WORKSPACES = [
    "chat", "file", "medical", "legal", "language", "coding",
    "science", "math", "engineering", "education", "business",
    "writing", "data", "cyber", "devices", "history",
    "university", "karaoke", "image", "video", "sim",
]

INSTRUCTIONS = {
    "chat": "Be a helpful, thoughtful, accurate AI assistant.",
    "file": "Analyze documents carefully. Separate facts from assumptions.",
    "medical": "Explain anatomy and medicine educationally. Do not diagnose users.",
    "legal": "Explain general legal concepts. Laws depend on jurisdiction.",
    "language": "Teach languages interactively. Correct mistakes kindly.",
    "coding": "Help with programming, debugging, testing, and software design.",
    "science": "Explain scientific concepts and distinguish evidence from hypotheses.",
    "math": "Explain mathematical reasoning step by step and check calculations.",
    "engineering": "Explain engineering principles, units, assumptions, and limitations.",
    "education": "Teach step by step and adapt explanations to the learner.",
    "business": "Explain business and economics with clear assumptions.",
    "writing": "Help with writing, editing, creativity, and constructive feedback.",
    "data": "Analyze data carefully. Do not invent results.",
    "cyber": "Focus on defensive cybersecurity and authorized testing.",
    "devices": "Explain electronics and smart devices with attention to safety.",
    "history": "Explain history using dates, context, and competing interpretations. Do not invent citations.",
    "university": "Help research universities, admissions requirements, programs, deadlines, and official sources. Do not promise admission or invent current deadlines.",
    "karaoke": "Help with vocal practice, breathing, pronunciation, and musical concepts. Do not reproduce copyrighted song lyrics.",
    "image": "Help with visual design and image prompts.",
    "video": "Help plan video scenes and motion. Be clear about what tools can actually generate.",
    "sim": "Explain simulations, assumptions, units, and limitations.",
}


# =========================================================
# 4. VISUAL DESIGN
# =========================================================

st.markdown("""
<style>
.stApp {
    background:
      radial-gradient(circle at 85% 4%, rgba(151,91,235,.18), transparent 32%),
      linear-gradient(135deg,#100d1c,#191329 55%,#100d1c);
    color:#f5f0ff;
}
[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#211432,#110d1c);
    border-right:1px solid rgba(191,151,255,.2);
}
h1,h2,h3 {color:#e0c5ff !important;}
.lidya-header {
    padding:25px 20px;
    border:1px solid rgba(196,160,255,.3);
    border-radius:22px;
    background:linear-gradient(120deg,rgba(109,61,171,.32),rgba(39,24,64,.65));
    margin-bottom:18px;
    text-align:center;
}
.lidya-title {
    font-size:clamp(30px,5vw,44px);
    font-weight:850;
    letter-spacing:2px;
    color:#e8d4ff;
}
.lidya-subtitle {color:#d7c6ed;font-size:16px;}
.lidya-orb {
    width:64px;height:64px;margin:0 auto 12px;border-radius:50%;
    background:radial-gradient(circle at 30% 25%,#fff 0%,#e5c8ff 9%,#b27bff 28%,#6338a5 58%,#28133e 80%);
    box-shadow:0 0 20px rgba(190,126,255,.5);
}
.lidya-card {
    border:1px solid rgba(196,160,255,.25);
    border-radius:18px;padding:22px;
    background:rgba(48,32,68,.42);
}
.stButton>button {
    border-radius:11px;border:1px solid rgba(199,165,255,.35);
}
[data-testid="stChatMessage"] {
    border:1px solid rgba(195,161,255,.12);
    border-radius:14px;
}
.lidya-footer {
    margin-top:28px;padding:18px;text-align:center;
    color:#bfa9dc;border-top:1px solid rgba(195,161,255,.16);
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# 5. SESSION STATE
# =========================================================

DEFAULTS = {
    "messages": [],
    "last_answer": "",
    "generated_image": None,
    "generated_video": None,
    "memory_items": [],
    "transcript": "",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def timestamp():
    try:
        return datetime.now(
            ZoneInfo("Europe/Istanbul")
        ).strftime("%d.%m.%Y %H:%M:%S")
    except Exception:
        return datetime.now().strftime("%d.%m.%Y %H:%M:%S")


# =========================================================
# 6. FILE READING
# =========================================================

def read_file(uploaded):
    if uploaded is None:
        raise ValueError("No file selected.")

    raw = uploaded.getvalue()
    if len(raw) > MAX_FILE_SIZE:
        raise ValueError("File size exceeds 10 MB.")

    name = uploaded.name.lower()

    if name.endswith(".pdf"):
        if PdfReader is None:
            raise RuntimeError("Install pypdf.")
        pdf = PdfReader(io.BytesIO(raw))
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

    if name.endswith(".docx"):
        if Document is None:
            raise RuntimeError("Install python-docx.")
        doc = Document(io.BytesIO(raw))
        parts = [p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                parts.append(" | ".join(c.text for c in row.cells))
        return "\n".join(parts)

    supported = (
        ".txt", ".md", ".csv", ".json", ".py", ".js",
        ".html", ".css", ".xml", ".yaml", ".yml",
        ".toml", ".sql",
    )
    if name.endswith(supported):
        return raw.decode("utf-8", errors="replace")

    raise ValueError(
        "Unsupported file. Supported types: PDF, DOCX, TXT, MD, CSV, JSON, and code files."
    )


# =========================================================
# 7. GROQ CHAT
# =========================================================

def ask_lidya(prompt, workspace="chat", context="", history=None, lang="en"):
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured in Streamlit Secrets.")

    client = Groq(api_key=GROQ_API_KEY)

    system = f"""
You are Lidya AI, a project developed by Şeymanur Acun.
Do not claim the underlying foundation models were all created by her.

Reply in the user's selected language ({lang}), unless they ask for another.
Understand mixed-language messages.
Be clear, thoughtful, accurate, and respectful.
Do not invent citations, web searches, or actions.
Do not pretend that you accessed live information when you did not.
For medical topics, provide educational information, not diagnosis.
For legal topics, explain that laws vary by jurisdiction.

Workspace instructions:
{INSTRUCTIONS.get(workspace, INSTRUCTIONS['chat'])}
"""

    messages = [{"role": "system", "content": system}]

    if history:
        for item in history[-12:]:
            if item.get("role") in ("user", "assistant"):
                content = str(item.get("content", ""))[:9000]
                if content:
                    messages.append({
                        "role": item["role"],
                        "content": content,
                    })

    if context:
        prompt += "\n\nUploaded document content:\n" + context[:25000]

    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.4,
        max_tokens=2200,
    )

    return response.choices[0].message.content or ""


# =========================================================
# 8. IMAGE GENERATION
# =========================================================

def generate_image(prompt):
    if not CF_ACCOUNT_ID or not CF_API_TOKEN:
        raise RuntimeError("Configure CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN.")

    url = (
        "https://api.cloudflare.com/client/v4/accounts/"
        f"{CF_ACCOUNT_ID}/ai/run/{IMAGE_MODEL}"
    )

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {CF_API_TOKEN}",
            "Content-Type": "application/json",
        },
        json={"prompt": prompt[:2000]},
        timeout=120,
    )

    if not response.ok:
        raise RuntimeError(
            f"Cloudflare HTTP {response.status_code}: {response.text[:300]}"
        )

    result = response.json()
    image_data = result.get("result", {}).get("image")

    if not result.get("success") or not image_data:
        raise RuntimeError("The image service returned no image.")

    raw = base64.b64decode(image_data)
    return Image.open(io.BytesIO(raw)).convert("RGB")


# =========================================================
# 9. ANIMATED VIDEO FROM IMAGE
# =========================================================

def animate_image(image, duration=4, fps=12):
    # This creates a zoom animation, NOT AI text-to-video.
    image = image.convert("RGB").resize((512, 512))
    frames = []

    for i in range(duration * fps):
        progress = i / max(duration * fps - 1, 1)
        scale = 1.0 + 0.10 * progress
        crop_w = int(512 / scale)
        crop_h = int(512 / scale)
        left = (512 - crop_w) // 2
        top = (512 - crop_h) // 2
        frame = image.crop(
            (left, top, left + crop_w, top + crop_h)
        ).resize((512, 512))
        frames.append(np.asarray(frame))

    try:
        import imageio.v2 as imageio
    except ImportError:
        raise RuntimeError("Install imageio to create MP4.")

    path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            path = f.name
        imageio.mimsave(
            path, frames, fps=fps, codec="libx264",
            quality=7, macro_block_size=16,
        )
        with open(path, "rb") as f:
            return f.read()
    finally:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass


# =========================================================
# 10. VOICE TRANSCRIPTION
# =========================================================

def transcribe_audio(audio):
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    client = Groq(api_key=GROQ_API_KEY)
    result = client.audio.transcriptions.create(
        file=(audio.name or "recording.wav", audio.getvalue()),
        model="whisper-large-v3-turbo",
        response_format="text",
    )
    return result if isinstance(result, str) else getattr(result, "text", str(result))


# =========================================================
# 11. SIMULATION LAB
# =========================================================

def simulation_lab(t):
    st.title(t["simulation"])
    st.write(t["simulation_desc"])

    kinds = [
        t["projectile"],
        t["orbit"],
        t["function"],
        t["wave"],
    ]

    kind = st.selectbox(t["sim_type"], kinds)

    if kind == t["projectile"]:
        a, b, c = st.columns(3)
        angle = a.slider(t["angle"], 5, 85, 45)
        velocity = b.slider(t["velocity"], 5, 100, 30)
        gravity = c.slider(t["gravity"], 1.0, 20.0, 9.81, 0.1)

        theta = np.radians(angle)
        vx = velocity * np.cos(theta)
        vy = velocity * np.sin(theta)
        flight = 2 * vy / gravity
        time = np.linspace(0, flight, 250)
        x = vx * time
        y = np.maximum(vy * time - 0.5 * gravity * time**2, 0)

        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_xlabel("Distance (m)")
        ax.set_ylabel("Height (m)")
        ax.set_title("Ideal projectile trajectory")
        ax.grid(True)
        st.pyplot(fig)
        plt.close(fig)

        st.subheader(t["result"])
        st.write(f"Maximum height: **{vy**2 / (2 * gravity):.2f} m**")
        st.write(f"Horizontal range: **{vx * flight:.2f} m**")
        st.write(f"Flight time: **{flight:.2f} s**")
        st.caption("Ideal model; air resistance is not included.")

    elif kind == t["orbit"]:
        radius = st.slider("Orbital radius", 2, 20, 8)
        period = st.slider("Orbital period", 2, 30, 12)
        time_value = st.slider(
            "Simulation time", 0.0, float(period), 3.0, 0.25
        )

        theta = np.linspace(0, 2 * np.pi, 400)
        angle = 2 * np.pi * time_value / period

        fig, ax = plt.subplots()
        ax.plot(radius * np.cos(theta), radius * np.sin(theta), "--")
        ax.scatter([0], [0], s=200, label="Central body")
        ax.scatter(
            [radius * np.cos(angle)],
            [radius * np.sin(angle)],
            s=90, label="Orbiting body",
        )
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True)
        ax.legend()
        ax.set_title("Simplified circular orbit")
        st.pyplot(fig)
        plt.close(fig)

        st.caption("Illustrative model, not an astronomical prediction.")

    elif kind == t["function"]:
        func = st.selectbox(
            "Function",
            ["y = x²", "y = x³", "y = sin(x)", "y = cos(x)",
             "y = 2x + 1", "y = |x|"],
        )
        x = np.linspace(-10, 10, 500)
        funcs = {
            "y = x²": x**2,
            "y = x³": x**3,
            "y = sin(x)": np.sin(x),
            "y = cos(x)": np.cos(x),
            "y = 2x + 1": 2*x + 1,
            "y = |x|": np.abs(x),
        }

        fig, ax = plt.subplots()
        ax.plot(x, funcs[func])
        ax.axhline(0, linewidth=0.8)
        ax.axvline(0, linewidth=0.8)
        ax.grid(True)
        ax.set_title(func)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        st.pyplot(fig)
        plt.close(fig)

    else:
        a, b = st.columns(2)
        amplitude = a.slider(t["amplitude"], 0.1, 5.0, 1.0, 0.1)
        frequency = b.slider(t["frequency"], 0.1, 5.0, 1.0, 0.1)
        phase = st.slider("Phase", 0.0, 6.28, 0.0, 0.1)
        x = np.linspace(0, 4*np.pi, 600)
        y = amplitude * np.sin(frequency*x + phase)

        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.grid(True)
        ax.set_xlabel("Position")
        ax.set_ylabel("Amplitude")
        ax.set_title("Sine wave")
        st.pyplot(fig)
        plt.close(fig)


# =========================================================
# 12. UNIVERSITY RESEARCH LINKS
# =========================================================

UNIVERSITIES = {
    "Harvard University": "https://college.harvard.edu/",
    "University of Oxford": "https://www.ox.ac.uk/admissions/undergraduate",
    "University of Cambridge": "https://www.undergraduate.study.cam.ac.uk/",
    "Massachusetts Institute of Technology": "https://mitadmissions.org/",
    "Yale University": "https://admissions.yale.edu/",
    "Columbia University": "https://undergrad.admissions.columbia.edu/",
    "Princeton University": "https://admission.princeton.edu/",
    "Stanford University": "https://admission.stanford.edu/",
}


# =========================================================
# 13. LANGUAGE AND SIDEBAR
# =========================================================

language_options = list(LANGUAGES.keys())

if "language_name" not in st.session_state:
    st.session_state.language_name = language_options[0]

selected_language = st.sidebar.selectbox(
    "🌐 Dil / Language / Langue",
    language_options,
    index=language_options.index(st.session_state.language_name),
    key="language_selector",
)

st.session_state.language_name = selected_language
lang = LANGUAGES[selected_language]
t = UI[lang]

if lang == "ar":
    st.markdown(
        "<style>.stApp,[data-testid='stSidebar']{direction:rtl;text-align:right}</style>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        "<style>.stApp,[data-testid='stSidebar']{direction:ltr;text-align:left}</style>",
        unsafe_allow_html=True,
    )

st.sidebar.markdown("---")
st.sidebar.subheader(t["workspace"])

selected = st.sidebar.radio(
    t["workspace"],
    WORKSPACES,
    format_func=lambda key: t.get(key, UI["en"].get(key, key)),
    label_visibility="collapsed",
    key="workspace_selector",
)

if st.sidebar.button(t["new"], use_container_width=True):
    st.session_state.messages = []
    st.session_state.last_answer = ""
    st.rerun()

if st.sidebar.button(t["clear"], use_container_width=True):
    st.session_state.messages = []
    st.session_state.last_answer = ""
    st.rerun()

st.sidebar.markdown("---")

if not GROQ_API_KEY:
    st.sidebar.warning(t["missing_key"])

if not CF_ACCOUNT_ID or not CF_API_TOKEN:
    st.sidebar.info(t["missing_cf"])

st.sidebar.caption(t["notice"])


# =========================================================
# 14. CLEAN LANDING SCREEN
# =========================================================

st.markdown(
    f"""
    <div class="lidya-header">
        <div class="lidya-orb"></div>
        <div class="lidya-title">💜 LIDYA AI</div>
        <div class="lidya-subtitle">{t["tagline"]}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(f"🕒 {t['timestamp']}: {timestamp()}")

if not st.session_state.messages and selected == "chat":
    st.markdown(
        f"""
        <div class="lidya-card" style="text-align:center;">
            <h3>{t["welcome"]}</h3>
            <p>Lidya AI · Built with curiosity and Python.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # Workspace cards intentionally omitted:
    # the sidebar already contains the workspace list.


# =========================================================
# 15. CHAT WORKSPACE
# =========================================================

if selected not in ("file", "image", "video", "sim", "university", "karaoke"):

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("timestamp"):
                st.caption("🕒 " + message["timestamp"])

    prompt = st.chat_input(t["prompt"])

    if prompt:
        now = timestamp()
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": now,
        })

        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption("🕒 " + now)

        with st.chat_message("assistant"):
            with st.spinner(t["thinking"]):
                try:
                    answer = ask_lidya(
                        prompt,
                        workspace=selected,
                        history=st.session_state.messages[:-1],
                        lang=lang,
                    )
                    st.markdown(answer)
                    answer_time = timestamp()
                    st.caption("🕒 " + answer_time)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "timestamp": answer_time,
                    })
                    st.session_state.last_answer = answer
                except Exception as exc:
                    st.error(f"{type(exc).__name__}: {exc}")


# =========================================================
# 16. FILE LABORATORY
# =========================================================

elif selected == "file":
    st.title(t["file"])

    uploaded = st.file_uploader(
        t["upload"],
        type=[
            "pdf", "docx", "txt", "md", "csv", "json",
            "py", "js", "html", "css", "xml", "yaml",
            "yml", "toml", "sql",
        ],
    )

    question = st.text_area(
        t["question"],
        value=(
            "Bu dosyayı özetle, önemli noktaları açıkla ve varsa hataları belirt."
            if lang == "tr"
            else "Summarize this file, explain key points, and identify possible issues."
        ),
    )

    if st.button(t["analyze"], use_container_width=True):
        if not uploaded:
            st.warning("Please upload a file first.")
        elif not GROQ_API_KEY:
            st.error(t["missing_key"])
        else:
            try:
                content = read_file(uploaded)
                if not content.strip():
                    st.warning("No readable text was found.")
                else:
                    with st.spinner(t["thinking"]):
                        answer = ask_lidya(
                            question, "file", context=content, lang=lang
                        )
                    st.markdown(answer)
                    st.session_state.last_answer = answer
            except Exception as exc:
                st.error(f"File analysis failed: {exc}")


# =========================================================
# 17. IMAGE STUDIO
# =========================================================

elif selected == "image":
    st.title(t["image"])
    prompt = st.text_area(t["image_prompt"], height=130)

    if st.button(t["make_image"], use_container_width=True):
        if not prompt.strip():
            st.warning(t["image_prompt"])
        else:
            try:
                with st.spinner(t["thinking"]):
                    image = generate_image(prompt)
                st.session_state.generated_image = image
            except Exception as exc:
                st.error(f"Image generation failed: {exc}")

    if st.session_state.generated_image is not None:
        image = st.session_state.generated_image
        st.image(image, use_container_width=True)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        st.download_button(
            "⬇️ PNG",
            buffer.getvalue(),
            "lidya_image.png",
            "image/png",
        )


# =========================================================
# 18. VIDEO STUDIO
# =========================================================

elif selected == "video":
    st.title(t["video"])
    st.info(
        "This tool creates a short zoom animation from an AI-generated image. "
        "It is not true text-to-video generation."
    )
    prompt = st.text_area(t["video_prompt"], height=120)

    if st.button(t["make_video"], use_container_width=True):
        if not prompt.strip():
            st.warning(t["video_prompt"])
        else:
            try:
                with st.spinner(t["thinking"]):
                    image = generate_image(prompt)
                    st.session_state.generated_image = image
                    st.session_state.generated_video = animate_image(image)
            except Exception as exc:
                st.error(f"Video creation failed: {exc}")

    if st.session_state.generated_video:
        st.video(st.session_state.generated_video)
        st.download_button(
            "⬇️ Download MP4",
            st.session_state.generated_video,
            "lidya_video.mp4",
            "video/mp4",
        )


# =========================================================
# 19. SIMULATION LAB
# =========================================================

elif selected == "sim":
    simulation_lab(t)


# =========================================================
# 20. UNIVERSITY RESEARCH
# =========================================================

elif selected == "university":
    st.title(t["university"])
    st.write(
        "Üniversitelerin kabul koşullarını ve programlarını resmî "
        "kaynaklardan kontrol etmek için aşağıdaki bağlantıları kullan."
        if lang == "tr"
        else "Use the official university websites below to verify admissions requirements and programs."
    )

    for name, url in UNIVERSITIES.items():
        st.markdown(f"**[{name}]({url})**")

    st.caption(t["not_live"])

    research_question = st.text_area(
        t["research"],
        placeholder=(
            "Örnek: Uluslararası öğrenciler için lisans başvuru koşulları ve maddi yardım."
            if lang == "tr"
            else "Example: Undergraduate requirements and financial aid for international applicants."
        ),
    )

    if st.button(t["research_button"], use_container_width=True):
        if not research_question.strip():
            st.warning(t["research"])
        elif not GROQ_API_KEY:
            st.error(t["missing_key"])
        else:
            with st.spinner(t["thinking"]):
                try:
                    answer = ask_lidya(
                        "Help me plan research on this question: "
                        + research_question
                        + "\nProvide a checklist of facts to verify and relevant official websites. "
                          "Do not pretend to have checked current pages.",
                        workspace="university",
                        lang=lang,
                    )
                    st.markdown(answer)
                    st.session_state.last_answer = answer
                except Exception as exc:
                    st.error(str(exc))


# =========================================================
# 21. SONG AND AUDIO LAB
# =========================================================

elif selected == "karaoke":
    st.title(t["karaoke"])
    st.info(t["karaoke_help"])

    audio = st.file_uploader(
        t["upload"],
        type=["wav", "mp3", "m4a", "ogg"],
    )

    if audio:
        st.audio(audio)
        st.download_button(
            "⬇️ Download audio",
            audio.getvalue(),
            audio.name,
            audio.type or "audio/mpeg",
        )

    st.subheader("Vocal practice")
    practice_text = st.text_area(
        "Practice notes",
        placeholder="Record the song title, pronunciation goals, breathing notes, or your practice plan.",
    )

    if st.button("Save practice notes"):
        if practice_text.strip():
            st.session_state.memory_items.append({
                "type": "practice",
                "text": practice_text.strip(),
                "time": timestamp(),
            })
            st.success("Practice notes saved for this session.")


# =========================================================
# 22. SESSION MEMORY
# =========================================================

st.markdown("---")
st.subheader(t["memory"])

with st.expander(t["remember"], expanded=False):
    memory_text = st.text_area(
        "Memory note",
        placeholder=(
            "Örneğin: Bu projede şu hedefe odaklanıyorum."
            if lang == "tr"
            else "For example: This is the goal I am working toward."
        ),
        key="memory_input",
    )

    if st.button("Save memory note"):
        if memory_text.strip():
            st.session_state.memory_items.append({
                "type": "note",
                "text": memory_text.strip(),
                "time": timestamp(),
            })
            st.success("Saved for the current session.")

if st.session_state.memory_items:
    for i, item in enumerate(st.session_state.memory_items):
        st.write(f"**{i + 1}.** {item['text']}")
        st.caption(item["time"])

    if st.button("Clear session memory"):
        st.session_state.memory_items = []
        st.rerun()

st.caption(
    "Session memory is temporary. It is not a permanent, account-linked database."
)


# =========================================================
# 23. VOICE RECORDING AND TRANSCRIPTION
# =========================================================

st.markdown("---")
st.subheader(t["voice"])

audio_input = st.audio_input(t["voice"])

if audio_input is not None:
    st.audio(audio_input)

    if st.button(t["transcribe"]):
        if not GROQ_API_KEY:
            st.error(t["missing_key"])
        else:
            try:
                with st.spinner(t["thinking"]):
                    st.session_state.transcript = transcribe_audio(audio_input)
            except Exception as exc:
                st.error(f"Transcription failed: {exc}")

if st.session_state.transcript:
    transcript = st.text_area(
        "Transcript",
        value=st.session_state.transcript,
        key="transcript_edit",
    )

    if st.button(t["send"], key="send_transcript"):
        if transcript.strip() and GROQ_API_KEY:
            try:
                answer = ask_lidya(
                    transcript,
                    workspace=selected,
                    history=st.session_state.messages[-12:],
                    lang=lang,
                )
                st.session_state.messages.extend([
                    {
                        "role": "user",
                        "content": transcript,
                        "timestamp": timestamp(),
                    },
                    {
                        "role": "assistant",
                        "content": answer,
                        "timestamp": timestamp(),
                    },
                ])
                st.session_state.last_answer = answer
                st.markdown(answer)
            except Exception as exc:
                st.error(str(exc))


# =========================================================
# 24. READ ANSWER ALOUD
# =========================================================

if st.session_state.last_answer:
    if st.button(t["read"]):
        voice_languages = {
            "tr": "tr-TR", "en": "en-US", "fr": "fr-FR",
            "de": "de-DE", "es": "es-ES", "it": "it-IT",
            "ja": "ja-JP", "zh": "zh-CN", "ar": "ar-SA",
        }

        speech_text = json.dumps(st.session_state.last_answer)
        speech_lang = json.dumps(voice_languages.get(lang, "en-US"))

        component_html = f"""
        <button onclick="speakLidya()" style="
          padding:12px 18px;border-radius:12px;
          border:1px solid #b99ae8;background:#302044;color:white;">
          {t["read"]}
        </button>
        <script>
          function speakLidya() {{
            if (!window.speechSynthesis) {{
              alert("Speech synthesis is unavailable in this browser.");
              return;
            }}
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance({speech_text});
            utterance.lang = {speech_lang};
            utterance.rate = 0.95;
            window.speechSynthesis.speak(utterance);
          }}
        </script>
        """

        st.components.v1.html(component_html, height=70)


# =========================================================
# 25. FOOTER
# =========================================================

st.markdown(
    f"""
    <div class="lidya-footer">
      💜 Lidya AI · {t["tagline"]}
      <br>Built with curiosity and Python.
    </div>
    """,
    unsafe_allow_html=True,
)

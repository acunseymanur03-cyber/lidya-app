import os
import io
import base64
import tempfile
import html
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st
import requests
import numpy as np
import imageio.v2 as imageio
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
# 1. PAGE CONFIGURATION
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


# =========================================================
# 2. API CONFIGURATION
# =========================================================

def get_secret(key):
    try:
        value = st.secrets.get(key)
        if value:
            return value
    except Exception:
        pass
    return os.getenv(key)


GROQ_API_KEY = get_secret("GROQ_API_KEY")
CLOUDFLARE_ACCOUNT_ID = get_secret("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = get_secret("CLOUDFLARE_API_TOKEN")


# =========================================================
# 3. LANGUAGES AND TRANSLATIONS
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

TRANSLATIONS = {
    "tr": {
        "tagline": "Düşün. Öğren. Üret. Keşfet.",
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
        "new_chat": "➕ Yeni sohbet",
        "clear": "🧹 Sohbeti temizle",
        "prompt": "Lidya'ya bir şey sor...",
        "upload": "Dosya yükle",
        "analyze": "Dosyayı analiz et",
        "file_question": "Dosyayla ilgili ne yapmamı istiyorsun?",
        "image_prompt": "Nasıl bir görsel oluşturalım?",
        "generate_image": "✨ Görsel oluştur",
        "video_prompt": "Nasıl bir video oluşturalım?",
        "generate_video": "🎬 Video oluştur",
        "need_groq": "Sohbet için GROQ_API_KEY yapılandırılmalı.",
        "need_cloudflare": "Görsel üretimi için Cloudflare ayarları gerekli.",
        "thinking": "Lidya düşünüyor...",
        "welcome": "Merhaba! Ben Lidya. Bugün ne öğrenmek veya üretmek istiyorsun?",
        "read_aloud": "🔊 Son yanıtı sesli oku",
        "voice": "🎙️ Sesli mesaj",
        "transcribe": "Sesi yazıya çevir",
        "notice": "Lidya yapay zekâ destekli bir yardımcıdır. Tıp ve hukuk kararlarını uzmanlarla doğrula.",
        "file_help": "PDF, DOCX, TXT, MD, CSV, JSON veya kod dosyası yükleyebilirsin.",
        "choose_file": "Önce bir dosya yükle.",
        "file_empty": "Dosyadan okunabilir metin çıkarılamadı.",
        "file_error": "Dosya analizi başarısız oldu.",
        "image_success": "Görsel başarıyla oluşturuldu.",
        "image_error": "Görsel üretimi başarısız oldu.",
        "video_success": "Hareketli MP4 video hazır!",
        "video_error": "Video oluşturma başarısız oldu.",
        "download_image": "⬇️ Görseli indir",
        "download_video": "⬇️ MP4 videoyu indir",
        "transcript_label": "Ses kaydının metni",
        "creating_image": "Lidya görsel oluşturuyor...",
        "creating_video": "Görsel oluşturuluyor ve ardından MP4 hazırlanıyor...",
        "voice_error": "Ses işlenemedi.",
        "send": "Gönder",
        "simulation_title": "Lidya Simülasyon Laboratuvarı",
        "simulation_desc": "Matematiksel ve bilimsel modelleri etkileşimli olarak keşfet.",
        "simulation_type": "Simülasyon türü",
        "projectile": "🚀 Fırlatma hareketi",
        "orbit": "🪐 Yörünge modeli",
        "function": "📈 Fonksiyon grafiği",
        "wave": "〰️ Dalga simülasyonu",
        "angle": "Fırlatma açısı",
        "velocity": "Başlangıç hızı",
        "gravity": "Yerçekimi",
        "frequency": "Frekans",
        "amplitude": "Genlik",
        "run_sim": "▶️ Simülasyonu çalıştır",
        "result": "Simülasyon sonucu",
        "math_topic": "Matematik konusu",
        "solve": "Çözümünü açıkla",
        "timestamp": "Yerel tarih ve saat",
    },
    "en": {
        "tagline": "Think. Learn. Create. Explore.",
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
        "new_chat": "➕ New chat",
        "clear": "🧹 Clear chat",
        "prompt": "Ask Lidya something...",
        "upload": "Upload file",
        "analyze": "Analyze file",
        "file_question": "What should I do with this file?",
        "image_prompt": "Describe the image you want to create",
        "generate_image": "✨ Generate image",
        "video_prompt": "Describe the image for your video",
        "generate_video": "🎬 Create video",
        "need_groq": "Configure GROQ_API_KEY to enable chat.",
        "need_cloudflare": "Configure Cloudflare to enable image generation.",
        "thinking": "Lidya is thinking...",
        "welcome": "Hello! I'm Lidya. What would you like to learn or create today?",
        "read_aloud": "🔊 Read last answer aloud",
        "voice": "🎙️ Voice message",
        "transcribe": "Transcribe audio",
        "notice": "Lidya is an AI assistant. Verify important medical and legal decisions with qualified professionals.",
        "file_help": "Upload a PDF, DOCX, TXT, MD, CSV, JSON, or code file.",
        "choose_file": "Please upload a file first.",
        "file_empty": "No readable text could be extracted.",
        "file_error": "File analysis failed.",
        "image_success": "Image created successfully.",
        "image_error": "Image generation failed.",
        "video_success": "Animated MP4 video is ready!",
        "video_error": "Video creation failed.",
        "download_image": "⬇️ Download image",
        "download_video": "⬇️ Download MP4 video",
        "transcript_label": "Audio transcript",
        "creating_image": "Lidya is creating an image...",
        "creating_video": "Creating an image, then preparing the MP4...",
        "voice_error": "Audio could not be processed.",
        "send": "Send",
        "simulation_title": "Lidya Simulation Laboratory",
        "simulation_desc": "Explore mathematical and scientific models interactively.",
        "simulation_type": "Simulation type",
        "projectile": "🚀 Projectile motion",
        "orbit": "🪐 Orbital model",
        "function": "📈 Function graph",
        "wave": "〰️ Wave simulation",
        "angle": "Launch angle",
        "velocity": "Initial velocity",
        "gravity": "Gravity",
        "frequency": "Frequency",
        "amplitude": "Amplitude",
        "run_sim": "▶️ Run simulation",
        "result": "Simulation result",
        "math_topic": "Mathematics topic",
        "solve": "Explain the solution",
        "timestamp": "Local date and time",
    },
    "fr": {
        "tagline": "Réfléchir. Apprendre. Créer. Explorer.",
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
        "new_chat": "➕ Nouvelle discussion",
        "clear": "🧹 Effacer la discussion",
        "prompt": "Posez une question à Lidya...",
        "upload": "Téléverser un fichier",
        "analyze": "Analyser le fichier",
        "file_question": "Que dois-je faire avec ce fichier ?",
        "image_prompt": "Décrivez l’image à créer",
        "generate_image": "✨ Créer une image",
        "video_prompt": "Décrivez l’image de votre vidéo",
        "generate_video": "🎬 Créer une vidéo",
        "need_groq": "Configurez GROQ_API_KEY pour activer le chat.",
        "need_cloudflare": "Configurez Cloudflare pour créer des images.",
        "thinking": "Lidya réfléchit...",
        "welcome": "Bonjour ! Je suis Lidya. Que souhaitez-vous apprendre ou créer ?",
        "read_aloud": "🔊 Lire la dernière réponse",
        "voice": "🎙️ Message vocal",
        "transcribe": "Transcrire l’audio",
        "notice": "Lidya est une assistante IA. Vérifiez les décisions importantes auprès de professionnels.",
        "file_help": "Téléversez un fichier PDF, DOCX, TXT, MD, CSV, JSON ou un fichier de code.",
        "choose_file": "Veuillez d’abord téléverser un fichier.",
        "file_empty": "Aucun texte lisible n’a été extrait.",
        "file_error": "L’analyse du fichier a échoué.",
        "image_success": "Image créée avec succès.",
        "image_error": "La création de l’image a échoué.",
        "video_success": "La vidéo MP4 animée est prête !",
        "video_error": "La création vidéo a échoué.",
        "download_image": "⬇️ Télécharger l’image",
        "download_video": "⬇️ Télécharger la vidéo MP4",
        "transcript_label": "Transcription audio",
        "creating_image": "Lidya crée une image...",
        "creating_video": "Création de l’image, puis préparation du MP4...",
        "voice_error": "Impossible de traiter l’audio.",
        "send": "Envoyer",
        "simulation_title": "Laboratoire de simulation Lidya",
        "simulation_desc": "Explorez des modèles mathématiques et scientifiques.",
        "simulation_type": "Type de simulation",
        "projectile": "🚀 Mouvement d’un projectile",
        "orbit": "🪐 Modèle orbital",
        "function": "📈 Graphe de fonction",
        "wave": "〰️ Simulation d’onde",
        "angle": "Angle de lancement",
        "velocity": "Vitesse initiale",
        "gravity": "Gravité",
        "frequency": "Fréquence",
        "amplitude": "Amplitude",
        "run_sim": "▶️ Lancer la simulation",
        "result": "Résultat de la simulation",
        "math_topic": "Sujet mathématique",
        "solve": "Expliquer la solution",
        "timestamp": "Date et heure locales",
    },
}

# Eksik çevirilerde İngilizce yedek kullanılır.
for code in LANGUAGES.values():
    if code not in TRANSLATIONS:
        TRANSLATIONS[code] = {}
    for key, value in TRANSLATIONS["en"].items():
        TRANSLATIONS[code].setdefault(key, value)

# Almanca, İspanyolca, İtalyanca, Japonca, Çince ve Arapça için
# temel arayüz etiketlerini yerelleştir.
EXTRA_TRANSLATIONS = {
    "de": {
        "tagline": "Denken. Lernen. Erstellen. Entdecken.",
        "workspace": "Arbeitsbereich",
        "chat": "💜 Mit Lidya chatten",
        "file": "📁 Datei-Labor",
        "medical": "🫀 Medizin und Anatomie",
        "legal": "⚖️ Rechtsrecherche",
        "language": "🌍 Sprachlehrer",
        "coding": "💻 Softwareentwicklung",
        "science": "🔬 Wissenschaft und Forschung",
        "math": "📐 Mathematik",
        "engineering": "⚙️ Ingenieurwesen",
        "education": "🎓 Bildung",
        "business": "📊 Wirtschaft und Finanzen",
        "writing": "✍️ Schreiben und Kreativität",
        "data": "📈 Datenanalyse",
        "cyber": "🛡️ Cybersicherheit",
        "devices": "🔌 Smarte Geräte",
        "image": "🎨 Bildstudio",
        "video": "🎬 Videostudio",
        "sim": "🪐 Simulationen",
        "new_chat": "➕ Neuer Chat",
        "clear": "🧹 Chat löschen",
        "prompt": "Frag Lidya etwas...",
        "welcome": "Hallo! Ich bin Lidya. Was möchtest du heute lernen oder erstellen?",
        "thinking": "Lidya denkt nach...",
        "run_sim": "▶️ Simulation starten",
        "simulation_title": "Lidya Simulationslabor",
        "simulation_desc": "Erkunde mathematische und wissenschaftliche Modelle.",
    },
    "es": {
        "tagline": "Piensa. Aprende. Crea. Explora.",
        "workspace": "Espacio de trabajo",
        "chat": "💜 Chatear con Lidya",
        "file": "📁 Laboratorio de archivos",
        "medical": "🫀 Medicina y anatomía",
        "legal": "⚖️ Investigación jurídica",
        "language": "🌍 Profesor de idiomas",
        "coding": "💻 Ingeniería de software",
        "science": "🔬 Ciencia e investigación",
        "math": "📐 Matemáticas",
        "engineering": "⚙️ Ingeniería",
        "education": "🎓 Educación",
        "business": "📊 Negocios y economía",
        "writing": "✍️ Escritura y creatividad",
        "data": "📈 Análisis de datos",
        "cyber": "🛡️ Ciberseguridad",
        "devices": "🔌 Dispositivos inteligentes",
        "image": "🎨 Estudio de imágenes",
        "video": "🎬 Estudio de vídeo",
        "sim": "🪐 Simulaciones",
        "new_chat": "➕ Nuevo chat",
        "clear": "🧹 Borrar chat",
        "prompt": "Pregúntale algo a Lidya...",
        "welcome": "¡Hola! Soy Lidya. ¿Qué te gustaría aprender o crear hoy?",
        "thinking": "Lidya está pensando...",
        "run_sim": "▶️ Ejecutar simulación",
        "simulation_title": "Laboratorio de simulación Lidya",
        "simulation_desc": "Explora modelos matemáticos y científicos.",
    },
    "it": {
        "tagline": "Pensa. Impara. Crea. Esplora.",
        "workspace": "Area di lavoro",
        "chat": "💜 Chatta con Lidya",
        "file": "📁 Laboratorio file",
        "medical": "🫀 Medicina e anatomia",
        "legal": "⚖️ Ricerca legale",
        "language": "🌍 Insegnante di lingue",
        "coding": "💻 Ingegneria del software",
        "science": "🔬 Scienza e ricerca",
        "math": "📐 Matematica",
        "engineering": "⚙️ Ingegneria",
        "education": "🎓 Istruzione",
        "business": "📊 Economia e impresa",
        "writing": "✍️ Scrittura e creatività",
        "data": "📈 Analisi dei dati",
        "cyber": "🛡️ Sicurezza informatica",
        "devices": "🔌 Dispositivi intelligenti",
        "image": "🎨 Studio immagini",
        "video": "🎬 Studio video",
        "sim": "🪐 Simulazioni",
        "new_chat": "➕ Nuova chat",
        "clear": "🧹 Cancella chat",
        "prompt": "Chiedi qualcosa a Lidya...",
        "welcome": "Ciao! Sono Lidya. Che cosa vorresti imparare o creare oggi?",
        "thinking": "Lidya sta pensando...",
        "run_sim": "▶️ Avvia simulazione",
        "simulation_title": "Laboratorio di simulazione Lidya",
        "simulation_desc": "Esplora modelli matematici e scientifici.",
    },
    "ja": {
        "tagline": "考える。学ぶ。創る。探求する。",
        "workspace": "ワークスペース",
        "chat": "💜 Lidyaとチャット",
        "file": "📁 ファイルラボ",
        "medical": "🫀 医学と解剖学",
        "legal": "⚖️ 法律リサーチ",
        "language": "🌍 言語教師",
        "coding": "💻 ソフトウェア工学",
        "science": "🔬 科学と研究",
        "math": "📐 数学",
        "engineering": "⚙️ 工学",
        "education": "🎓 教育",
        "business": "📊 ビジネスと経済",
        "writing": "✍️ 執筆と創作",
        "data": "📈 データ分析",
        "cyber": "🛡️ サイバーセキュリティ",
        "devices": "🔌 スマートデバイス",
        "image": "🎨 画像スタジオ",
        "video": "🎬 動画スタジオ",
        "sim": "🪐 シミュレーション",
        "new_chat": "➕ 新しいチャット",
        "clear": "🧹 チャットを消去",
        "prompt": "Lidyaに質問する...",
        "welcome": "こんにちは、Lidyaです。今日は何を学び、何を作りたいですか？",
        "thinking": "Lidyaが考えています...",
        "run_sim": "▶️ シミュレーション開始",
        "simulation_title": "Lidyaシミュレーションラボ",
        "simulation_desc": "数学と科学のモデルを体験しましょう。",
    },
    "zh": {
        "tagline": "思考。学习。创造。探索。",
        "workspace": "工作区",
        "chat": "💜 与 Lidya 聊天",
        "file": "📁 文件实验室",
        "medical": "🫀 医学与解剖学",
        "legal": "⚖️ 法律研究",
        "language": "🌍 语言教师",
        "coding": "💻 软件工程",
        "science": "🔬 科学与研究",
        "math": "📐 数学",
        "engineering": "⚙️ 工程学",
        "education": "🎓 教育",
        "business": "📊 商业与经济",
        "writing": "✍️ 写作与创意",
        "data": "📈 数据分析",
        "cyber": "🛡️ 网络安全",
        "devices": "🔌 智能设备",
        "image": "🎨 图像工作室",
        "video": "🎬 视频工作室",
        "sim": "🪐 模拟实验",
        "new_chat": "➕ 新建聊天",
        "clear": "🧹 清空聊天",
        "prompt": "向 Lidya 提问...",
        "welcome": "你好！我是 Lidya。今天你想学习或创作什么？",
        "thinking": "Lidya 正在思考...",
        "run_sim": "▶️ 运行模拟",
        "simulation_title": "Lidya 模拟实验室",
        "simulation_desc": "互动探索数学和科学模型。",
    },
    "ar": {
        "tagline": "فكّر. تعلّم. ابتكر. اكتشف.",
        "workspace": "مساحة العمل",
        "chat": "💜 الدردشة مع ليديا",
        "file": "📁 مختبر الملفات",
        "medical": "🫀 الطب والتشريح",
        "legal": "⚖️ البحث القانوني",
        "language": "🌍 معلّم اللغات",
        "coding": "💻 هندسة البرمجيات",
        "science": "🔬 العلوم والبحث",
        "math": "📐 الرياضيات",
        "engineering": "⚙️ الهندسة",
        "education": "🎓 التعليم",
        "business": "📊 الأعمال والاقتصاد",
        "writing": "✍️ الكتابة والإبداع",
        "data": "📈 تحليل البيانات",
        "cyber": "🛡️ الأمن السيبراني",
        "devices": "🔌 الأجهزة الذكية",
        "image": "🎨 استوديو الصور",
        "video": "🎬 استوديو الفيديو",
        "sim": "🪐 المحاكاة",
        "new_chat": "➕ محادثة جديدة",
        "clear": "🧹 مسح المحادثة",
        "prompt": "اسأل ليديا...",
        "welcome": "مرحبًا! أنا ليديا. ماذا تريد أن تتعلم أو تنشئ اليوم؟",
        "thinking": "ليديا تفكّر...",
        "run_sim": "▶️ تشغيل المحاكاة",
        "simulation_title": "مختبر محاكاة ليديا",
        "simulation_desc": "استكشف النماذج الرياضية والعلمية بشكل تفاعلي.",
    },
}

for code, values in EXTRA_TRANSLATIONS.items():
    TRANSLATIONS[code].update(values)


# =========================================================
# 4. WORKSPACES
# =========================================================

WORKSPACES = [
    "chat", "file", "medical", "legal", "language", "coding",
    "science", "math", "engineering", "education", "business",
    "writing", "data", "cyber", "devices", "image", "video", "sim",
]

WORKSPACE_INSTRUCTIONS = {
    "chat": "Be a helpful, thoughtful, clear AI assistant.",
    "file": "Analyze documents carefully. Separate facts, inferences, and uncertainties.",
    "medical": (
        "Explain medicine and anatomy educationally and accurately. "
        "Do not diagnose a person. Encourage professional care for personal concerns."
    ),
    "legal": (
        "Explain legal concepts generally. Laws differ by jurisdiction; "
        "do not claim to be the user's lawyer."
    ),
    "language": "Teach languages interactively at the learner's level.",
    "coding": "Help with software development. Explain code and likely bugs clearly.",
    "science": "Explain scientific ideas using evidence and clear examples.",
    "math": "Solve mathematics step by step and check the reasoning.",
    "engineering": "Explain engineering principles, assumptions, units, and limitations.",
    "education": "Teach step by step, adapting explanations to the learner.",
    "business": "Explain business and economics with clear assumptions.",
    "writing": "Help with writing, editing, brainstorming, and creativity.",
    "data": "Analyze data carefully and avoid unsupported conclusions.",
    "cyber": "Focus on defensive cybersecurity and authorized testing.",
    "devices": "Explain electronics and smart devices with attention to safety.",
    "image": "Help create detailed visual concepts and image prompts.",
    "video": "Help plan scenes, motion, composition, and video concepts.",
    "sim": "Explain scientific simulations, assumptions, units, and results.",
}


# =========================================================
# 5. DESIGN — ENHANCED LIDYA LANDING SCREEN
# =========================================================

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(
                circle at 82% 5%,
                rgba(151, 91, 235, 0.23),
                transparent 34%
            ),
            radial-gradient(
                circle at 5% 90%,
                rgba(104, 62, 163, 0.15),
                transparent 35%
            ),
            linear-gradient(135deg, #100d1c, #191329 55%, #100d1c);
        color: #f5f0ff;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #211432, #110d1c);
        border-right: 1px solid rgba(191, 151, 255, 0.20);
    }

    h1, h2, h3 {
        color: #e0c5ff !important;
    }

    .lidya-header {
        padding: 30px 26px;
        border: 1px solid rgba(196, 160, 255, 0.32);
        border-radius: 24px;
        background:
            radial-gradient(
                circle at 85% 50%,
                rgba(183, 120, 255, 0.22),
                transparent 35%
            ),
            linear-gradient(
                120deg,
                rgba(109, 61, 171, 0.35),
                rgba(39, 24, 64, 0.65)
            );
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.16);
        margin-bottom: 22px;
    }

    .lidya-title {
        font-size: clamp(30px, 5vw, 46px);
        font-weight: 850;
        letter-spacing: 2px;
        color: #e8d4ff;
        margin-bottom: 7px;
    }

    .lidya-subtitle {
        color: #d7c6ed;
        font-size: 16px;
    }

    .lidya-orb {
        width: 82px;
        height: 82px;
        margin: 4px auto 14px auto;
        border-radius: 50%;
        background:
            radial-gradient(
                circle at 32% 28%,
                #ffffff 0%,
                #e5c8ff 8%,
                #b27bff 25%,
                #6338a5 52%,
                #28133e 78%
            );
        box-shadow:
            0 0 18px rgba(190, 126, 255, 0.65),
            0 0 42px rgba(145, 84, 230, 0.35),
            inset -8px -8px 20px rgba(0, 0, 0, 0.32);
        animation: lidya-float 3.4s ease-in-out infinite;
    }

    @keyframes lidya-float {
        0%, 100% {
            transform: translateY(0) scale(1);
        }
        50% {
            transform: translateY(-7px) scale(1.035);
        }
    }

    .lidya-card {
        border: 1px solid rgba(196, 160, 255, 0.25);
        border-radius: 18px;
        padding: 18px;
        background: rgba(48, 32, 68, 0.48);
        min-height: 100px;
        margin-bottom: 10px;
    }

    .lidya-card-title {
        color: #e2c9ff;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .lidya-card-text {
        color: #cbb9e2;
        font-size: 13px;
    }

    .stButton > button {
        border-radius: 12px;
        border: 1px solid rgba(199, 165, 255, 0.35);
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: #c7a5ff;
        box-shadow: 0 0 14px rgba(173, 118, 255, 0.20);
    }

    [data-testid="stChatMessage"] {
        border: 1px solid rgba(195, 161, 255, 0.12);
        border-radius: 14px;
    }

    .lidya-footer {
        margin-top: 35px;
        padding: 18px;
        text-align: center;
        color: #bfa9dc;
        border-top: 1px solid rgba(195, 161, 255, 0.16);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 6. SESSION STATE
# =========================================================

DEFAULTS = {
    "messages": [],
    "last_answer": "",
    "generated_image": None,
    "generated_video_bytes": None,
    "transcribed_text": "",
    "show_welcome": True,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def local_timestamp():
    try:
        return datetime.now(
            ZoneInfo("Europe/Istanbul")
        ).strftime("%d.%m.%Y %H:%M:%S")
    except Exception:
        return datetime.now().strftime("%d.%m.%Y %H:%M:%S")


# =========================================================
# 7. FILE READER
# =========================================================

def read_uploaded_file(uploaded_file):
    if uploaded_file is None:
        raise ValueError("No file uploaded.")

    data = uploaded_file.getvalue()

    if len(data) > MAX_FILE_SIZE:
        raise ValueError("The file exceeds the 10 MB limit.")

    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        if PdfReader is None:
            raise RuntimeError("Install pypdf to read PDF files.")

        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if name.endswith(".docx"):
        if Document is None:
            raise RuntimeError("Install python-docx to read DOCX files.")

        document = Document(io.BytesIO(data))
        parts = [p.text for p in document.paragraphs]

        for table in document.tables:
            for row in table.rows:
                parts.append(" | ".join(cell.text for cell in row.cells))

        return "\n".join(parts)

    supported = (
        ".txt", ".md", ".csv", ".json", ".py", ".js",
        ".html", ".css", ".xml", ".yaml", ".yml",
        ".toml", ".sql",
    )

    if name.endswith(supported):
        return data.decode("utf-8", errors="replace")

    raise ValueError("Unsupported file type.")


# =========================================================
# 8. LIDYA CHAT
# =========================================================

def ask_lidya(
    user_prompt,
    workspace="chat",
    file_context="",
    language_name="Türkçe",
    history=None,
):
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it in Streamlit Secrets."
        )

    client = Groq(api_key=GROQ_API_KEY)

    instructions = WORKSPACE_INSTRUCTIONS.get(
        workspace,
        WORKSPACE_INSTRUCTIONS["chat"],
    )

    system_prompt = f"""
You are Lidya AI, an AI project developed by Şeymanur Acun.
Do not claim that the underlying models were all created by her.

The user's selected interface language is: {language_name}.
Reply in that language unless the user explicitly requests another language.
Understand mixed-language messages and preserve technical terms when useful.

Be accurate, clear, thoughtful, and respectful.
Explain complex concepts step by step when useful.
Do not invent sources, credentials, or actions you did not perform.
Do not claim to have browsed the internet unless browsing was actually performed.
Do not present medical or legal explanations as professional advice.

Workspace instructions:
{instructions}
"""

    messages = [{"role": "system", "content": system_prompt}]

    if history:
        for item in history[-12:]:
            role = item.get("role")
            if role not in ("user", "assistant"):
                continue

            content = str(item.get("content", ""))[:10000]
            if content:
                messages.append({
                    "role": role,
                    "content": content,
                })

    prompt = user_prompt.strip()

    if file_context:
        prompt += "\n\nDOCUMENT CONTENT:\n" + file_context[:25000]

    messages.append({
        "role": "user",
        "content": prompt,
    })

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.5,
        max_tokens=2000,
    )

    return response.choices[0].message.content or ""


# =========================================================
# 9. CLOUDFLARE IMAGE GENERATION
# =========================================================

def generate_image(prompt):
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        raise RuntimeError("Cloudflare credentials are missing.")

    endpoint = (
        "https://api.cloudflare.com/client/v4/accounts/"
        f"{CLOUDFLARE_ACCOUNT_ID}/ai/run/{IMAGE_MODEL}"
    )

    response = requests.post(
        endpoint,
        headers={
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "prompt": prompt[:2000],
            "steps": 4,
        },
        timeout=120,
    )

    if not response.ok:
        raise RuntimeError(
            f"Cloudflare returned HTTP {response.status_code}: "
            f"{response.text[:400]}"
        )

    result = response.json()

    if not result.get("success"):
        raise RuntimeError("Cloudflare could not generate the image.")

    image_data = result.get("result", {}).get("image")

    if not image_data:
        raise RuntimeError("The image response did not contain image data.")

    raw = base64.b64decode(image_data)
    return Image.open(io.BytesIO(raw)).convert("RGB")


# =========================================================
# 10. CREATE AN ANIMATED MP4 FROM AN IMAGE
# =========================================================

def create_video_from_image(image, duration=4, fps=12):
    """Create a zoom animation from a still image, not text-to-video AI."""
    image = image.convert("RGB")
    width, height = 512, 512
    image = image.resize((width, height))

    frames = []
    total_frames = duration * fps

    for i in range(total_frames):
        progress = i / max(total_frames - 1, 1)
        scale = 1.0 + (0.10 * progress)

        crop_w = int(width / scale)
        crop_h = int(height / scale)

        left = (width - crop_w) // 2
        top = (height - crop_h) // 2

        frame = image.crop((
            left,
            top,
            left + crop_w,
            top + crop_h,
        )).resize((width, height))

        frames.append(np.array(frame))

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".mp4",
            delete=False,
        ) as temp_file:
            temp_path = temp_file.name

        imageio.mimsave(
            temp_path,
            frames,
            fps=fps,
            codec="libx264",
            quality=7,
            macro_block_size=16,
        )

        with open(temp_path, "rb") as video_file:
            return video_file.read()

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


# =========================================================
# 11. VOICE TRANSCRIPTION
# =========================================================

def transcribe_audio(audio_file):
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is missing.")

    client = Groq(api_key=GROQ_API_KEY)

    transcription = client.audio.transcriptions.create(
        file=(
            audio_file.name or "recording.wav",
            audio_file.getvalue(),
        ),
        model="whisper-large-v3-turbo",
        response_format="text",
    )

    if isinstance(transcription, str):
        return transcription

    return getattr(transcription, "text", str(transcription))


# =========================================================
# 12. SCIENTIFIC SIMULATIONS
# =========================================================

def simulation_workspace(t):
    st.title(t["simulation_title"])
    st.write(t["simulation_desc"])

    simulation_type = st.selectbox(
        t["simulation_type"],
        [
            t["projectile"],
            t["orbit"],
            t["function"],
            t["wave"],
        ],
        key="simulation_type_select",
    )

    # -----------------------------------------------------
    # PROJECTILE MOTION
    # -----------------------------------------------------

    if simulation_type == t["projectile"]:
        st.subheader(t["projectile"])

        col1, col2, col3 = st.columns(3)

        with col1:
            angle = st.slider(
                t["angle"],
                min_value=5,
                max_value=85,
                value=45,
            )

        with col2:
            velocity = st.slider(
                t["velocity"],
                min_value=5,
                max_value=100,
                value=30,
            )

        with col3:
            gravity = st.slider(
                t["gravity"],
                min_value=1.0,
                max_value=20.0,
                value=9.81,
                step=0.1,
            )

        if st.button(t["run_sim"], key="run_projectile"):
            theta = np.radians(angle)
            vx = velocity * np.cos(theta)
            vy = velocity * np.sin(theta)

            flight_time = (2 * vy) / gravity
            time_values = np.linspace(0, flight_time, 200)

            x = vx * time_values
            y = (
                vy * time_values
                - 0.5 * gravity * time_values**2
            )

            y = np.maximum(y, 0)

            fig, ax = plt.subplots()
            ax.plot(x, y)
            ax.set_xlabel("Distance (m)")
            ax.set_ylabel("Height (m)")
            ax.set_title("Projectile trajectory")
            ax.grid(True)

            st.pyplot(fig)
            plt.close(fig)

            max_height = vy**2 / (2 * gravity)
            range_distance = vx * flight_time

            st.markdown(f"### {t['result']}")
            st.write(f"**Maximum height:** {max_height:.2f} m")
            st.write(f"**Horizontal range:** {range_distance:.2f} m")
            st.write(f"**Flight time:** {flight_time:.2f} s")

            st.caption(
                "Model assumes ideal projectile motion without air resistance."
            )

    # -----------------------------------------------------
    # ORBITAL MODEL
    # -----------------------------------------------------

    elif simulation_type == t["orbit"]:
        st.subheader(t["orbit"])

        radius = st.slider(
            "Orbital radius (arbitrary units)",
            min_value=2,
            max_value=20,
            value=8,
        )

        orbital_period = st.slider(
            "Orbital period (arbitrary time units)",
            min_value=2,
            max_value=30,
            value=12,
        )

        time_value = st.slider(
            "Simulation time",
            min_value=0.0,
            max_value=float(orbital_period),
            value=3.0,
            step=0.25,
        )

        theta = np.linspace(0, 2 * np.pi, 400)
        x_orbit = radius * np.cos(theta)
        y_orbit = radius * np.sin(theta)

        angle_now = 2 * np.pi * time_value / orbital_period
        planet_x = radius * np.cos(angle_now)
        planet_y = radius * np.sin(angle_now)

        fig, ax = plt.subplots()
        ax.plot(x_orbit, y_orbit, linestyle="--")
        ax.scatter([0], [0], s=250, label="Central body")
        ax.scatter([planet_x], [planet_y], s=80, label="Orbiting body")
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title("Simplified circular orbit")
        ax.grid(True)
        ax.legend()

        st.pyplot(fig)
        plt.close(fig)

        st.write(
            f"**Orbital position:** "
            f"x = {planet_x:.2f}, y = {planet_y:.2f}"
        )

        st.caption(
            "This is a simplified circular-orbit visualization, "
            "not a precise astronomical prediction."
        )

    # -----------------------------------------------------
    # FUNCTION GRAPH
    # -----------------------------------------------------

    elif simulation_type == t["function"]:
        st.subheader(t["function"])

        function_type = st.selectbox(
            "Function",
            [
                "y = x²",
                "y = x³",
                "y = sin(x)",
                "y = cos(x)",
                "y = 2x + 1",
                "y = |x|",
            ],
        )

        x = np.linspace(-10, 10, 500)

        functions = {
            "y = x²": x**2,
            "y = x³": x**3,
            "y = sin(x)": np.sin(x),
            "y = cos(x)": np.cos(x),
            "y = 2x + 1": 2 * x + 1,
            "y = |x|": np.abs(x),
        }

        fig, ax = plt.subplots()
        ax.plot(x, functions[function_type])
        ax.axhline(0, linewidth=0.8)
        ax.axvline(0, linewidth=0.8)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title(function_type)
        ax.grid(True)

        st.pyplot(fig)
        plt.close(fig)

    # -----------------------------------------------------
    # WAVE SIMULATION
    # -----------------------------------------------------

    elif simulation_type == t["wave"]:
        st.subheader(t["wave"])

        col1, col2 = st.columns(2)

        with col1:
            amplitude = st.slider(
                t["amplitude"],
                min_value=0.1,
                max_value=5.0,
                value=1.0,
                step=0.1,
            )

        with col2:
            frequency = st.slider(
                t["frequency"],
                min_value=0.1,
                max_value=5.0,
                value=1.0,
                step=0.1,
            )

        phase = st.slider(
            "Phase",
            min_value=0.0,
            max_value=6.28,
            value=0.0,
            step=0.1,
        )

        x = np.linspace(0, 4 * np.pi, 600)
        y = amplitude * np.sin(frequency * x + phase)

        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_xlabel("Position")
        ax.set_ylabel("Amplitude")
        ax.set_title("Sine wave")
        ax.grid(True)

        st.pyplot(fig)
        plt.close(fig)

        st.write(f"**Amplitude:** {amplitude}")
        st.write(f"**Frequency parameter:** {frequency}")
        st.write(f"**Phase:** {phase}")


# =========================================================
# 13. LANGUAGE SETTINGS AND SIDEBAR
# =========================================================

# Store the selected language so Streamlit reruns consistently.
if "language_name" not in st.session_state:
    st.session_state.language_name = "Türkçe 🇹🇷"

language_name = st.sidebar.selectbox(
    "🌐 Dil / Language / Langue",
    list(LANGUAGES.keys()),
    index=list(LANGUAGES.keys()).index(
        st.session_state.language_name
    ),
    key="language_selector",
)

st.session_state.language_name = language_name
language_code = LANGUAGES[language_name]
t = TRANSLATIONS[language_code]

if language_code == "ar":
    st.markdown(
        """
        <style>
        .stApp, [data-testid="stSidebar"] {
            direction: rtl;
            text-align: right;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        .stApp, [data-testid="stSidebar"] {
            direction: ltr;
            text-align: left;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.sidebar.markdown("---")
st.sidebar.subheader(t["workspace"])

selected_workspace = st.sidebar.radio(
    t["workspace"],
    WORKSPACES,
    format_func=lambda key: t.get(key, key),
    label_visibility="collapsed",
    key="workspace_selector",
)

if st.sidebar.button(t["new_chat"], use_container_width=True):
    st.session_state.messages = []
    st.session_state.last_answer = ""
    st.rerun()

if st.sidebar.button(t["clear"], use_container_width=True):
    st.session_state.messages = []
    st.session_state.last_answer = ""
    st.rerun()

st.sidebar.markdown("---")

if not GROQ_API_KEY:
    st.sidebar.warning(t["need_groq"])

if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
    st.sidebar.info(t["need_cloudflare"])

st.sidebar.caption(t["notice"])


# =========================================================
# 14. HEADER AND WELCOME SCREEN
# =========================================================

st.markdown(
    f"""
    <div class="lidya-header">
        <div class="lidya-orb"></div>
        <div class="lidya-title">💜 LIDYA AI</div>
        <div class="lidya-subtitle">
            {html.escape(t["tagline"])}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(f"🕒 {t['timestamp']}: {local_timestamp()}")

if not st.session_state.messages and selected_workspace == "chat":
    st.markdown(
        f"""
        <div class="lidya-card">
            <div class="lidya-card-title">
                {html.escape(t["welcome"])}
            </div>
            <div class="lidya-card-text">
                Lidya AI · Built with curiosity and Python.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### " + t["workspace"])

    card_columns = st.columns(3)

    quick_cards = [
        ("📐", t["math"]),
        ("🔬", t["science"]),
        ("🪐", t["sim"]),
        ("📁", t["file"]),
        ("🎨", t["image"]),
        ("🎬", t["video"]),
    ]

    for index, (icon, label) in enumerate(quick_cards):
        with card_columns[index % 3]:
            st.markdown(
                f"""
                <div class="lidya-card">
                    <div class="lidya-card-title">
                        {icon} {html.escape(label)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# 15. SIMULATION WORKSPACE
# =========================================================

if selected_workspace == "sim":
    simulation_workspace(t)


# =========================================================
# 16. CHAT WORKSPACE
# =========================================================

elif selected_workspace not in ("file", "image", "video", "sim"):

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("timestamp"):
                st.caption("🕒 " + message["timestamp"])

    user_prompt = st.chat_input(t["prompt"])

    if user_prompt:
        timestamp = local_timestamp()

        st.session_state.messages.append({
            "role": "user",
            "content": user_prompt,
            "timestamp": timestamp,
        })

        with st.chat_message("user"):
            st.markdown(user_prompt)
            st.caption("🕒 " + timestamp)

        with st.chat_message("assistant"):
            with st.spinner(t["thinking"]):
                try:
                    answer = ask_lidya(
                        user_prompt=user_prompt,
                        workspace=selected_workspace,
                        language_name=language_name,
                        history=st.session_state.messages[:-1],
                    )

                    st.markdown(answer)

                    answer_timestamp = local_timestamp()
                    st.caption("🕒 " + answer_timestamp)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "timestamp": answer_timestamp,
                    })

                    st.session_state.last_answer = answer

                except Exception as error:
                    st.error(f"{type(error).__name__}: {error}")


# =========================================================
# 17. FILE LABORATORY
# =========================================================

elif selected_workspace == "file":

    st.subheader(t["file"])
    st.caption(t["file_help"])

    uploaded_file = st.file_uploader(
        t["upload"],
        type=[
            "pdf", "docx", "txt", "md", "csv",
            "json", "py", "js", "html", "css",
            "xml", "yaml", "yml", "toml", "sql",
        ],
        key="file_upload",
    )

    file_question = st.text_area(
        t["file_question"],
        value=(
            "Bu dosyayı özetle ve önemli noktaları açıkla."
            if language_code == "tr"
            else "Summarize this file and explain its key points."
        ),
    )

    if st.button(t["analyze"], use_container_width=True):

        if not uploaded_file:
            st.warning(t["choose_file"])

        elif not GROQ_API_KEY:
            st.error(t["need_groq"])

        else:
            try:
                with st.spinner(t["thinking"]):
                    file_text = read_uploaded_file(uploaded_file)

                    if not file_text.strip():
                        st.warning(t["file_empty"])
                    else:
                        answer = ask_lidya(
                            user_prompt=file_question,
                            workspace="file",
                            file_context=file_text,
                            language_name=language_name,
                        )

                        st.markdown(answer)
                        st.session_state.last_answer = answer

            except Exception as error:
                st.error(f"{t['file_error']} {error}")


# =========================================================
# 18. IMAGE STUDIO
# =========================================================

elif selected_workspace == "image":

    st.subheader(t["image"])

    st.info(
        "Image generation uses Cloudflare Workers AI."
        if language_code == "en"
        else "Görsel üretimi Cloudflare Workers AI kullanır."
    )

    image_prompt = st.text_area(
        t["image_prompt"],
        placeholder=(
            "Mor ve lavanta renklerinde, bilim ve yapay zekâyı "
            "temsil eden zarif bir dijital illüstrasyon."
            if language_code == "tr"
            else "An elegant digital illustration about science and AI."
        ),
        height=120,
    )

    if st.button(t["generate_image"], use_container_width=True):

        if not image_prompt.strip():
            st.warning(t["image_prompt"])

        elif not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
            st.error(t["need_cloudflare"])

        else:
            try:
                with st.spinner(t["creating_image"]):
                    image_result = generate_image(image_prompt)

                st.session_state.generated_image = image_result
                st.success(t["image_success"])
                st.image(image_result, use_container_width=True)

            except Exception as error:
                st.error(f"{t['image_error']} {error}")

    if st.session_state.generated_image is not None:
        image_buffer = io.BytesIO()
        st.session_state.generated_image.save(
            image_buffer,
            format="PNG",
        )

        st.download_button(
            label=t["download_image"],
            data=image_buffer.getvalue(),
            file_name="lidya_image.png",
            mime="image/png",
            use_container_width=True,
        )


# =========================================================
# 19. VIDEO STUDIO
# =========================================================

elif selected_workspace == "video":

    st.subheader(t["video"])

    st.info(
        "Video Studio animates a still image and exports MP4; "
        "it is not true text-to-video generation."
    )

    video_prompt = st.text_area(
        t["video_prompt"],
        placeholder=(
            "Yıldızlarla dolu mor bir galakside yavaşça yakınlaşan kamera."
            if language_code == "tr"
            else "A slow zoom into a purple galaxy full of stars."
        ),
        height=120,
    )

    if st.button(t["generate_video"], use_container_width=True):

        if not video_prompt.strip():
            st.warning(t["video_prompt"])

        elif not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
            st.error(t["need_cloudflare"])

        else:
            try:
                with st.spinner(t["creating_video"]):
                    image_result = generate_image(video_prompt)
                    st.session_state.generated_image = image_result

                    video_bytes = create_video_from_image(image_result)
                    st.session_state.generated_video_bytes = video_bytes

                st.success(t["video_success"])

            except Exception as error:
                st.error(f"{t['video_error']} {error}")

    if st.session_state.generated_video_bytes:
        st.video(st.session_state.generated_video_bytes)

        st.download_button(
            label=t["download_video"],
            data=st.session_state.generated_video_bytes,
            file_name="lidya_video.mp4",
            mime="video/mp4",
            use_container_width=True,
        )


# =========================================================
# 20. VOICE INPUT
# =========================================================

st.markdown("---")
st.subheader(t["voice"])

audio_file = st.audio_input(t["voice"])

if audio_file is not None:

    st.audio(audio_file)

    if st.button(t["transcribe"]):

        if not GROQ_API_KEY:
            st.error(t["need_groq"])

        else:
            try:
                with st.spinner(t["thinking"]):
                    st.session_state.transcribed_text = transcribe_audio(
                        audio_file
                    )
            except Exception as error:
                st.error(f"{t['voice_error']} {error}")

if st.session_state.transcribed_text:

    transcript = st.text_area(
        t["transcript_label"],
        value=st.session_state.transcribed_text,
        height=120,
        key="transcript_editor",
    )

    if st.button(t["send"], key="send_transcript"):

        if transcript.strip():

            timestamp = local_timestamp()

            st.session_state.messages.append({
                "role": "user",
                "content": transcript,
                "timestamp": timestamp,
            })

            if GROQ_API_KEY:
                try:
                    with st.spinner(t["thinking"]):
                        answer = ask_lidya(
                            user_prompt=transcript,
                            workspace=selected_workspace,
                            language_name=language_name,
                            history=st.session_state.messages[:-1],
                        )

                    answer_timestamp = local_timestamp()

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "timestamp": answer_timestamp,
                    })

                    st.session_state.last_answer = answer
                    st.markdown(answer)

                except Exception as error:
                    st.error(str(error))


# =========================================================
# 21. READ ANSWER ALOUD
# =========================================================

if st.session_state.last_answer:

    if st.button(t["read_aloud"]):

        voice_languages = {
            "tr": "tr-TR",
            "en": "en-US",
            "fr": "fr-FR",
            "de": "de-DE",
            "es": "es-ES",
            "it": "it-IT",
            "ja": "ja-JP",
            "zh": "zh-CN",
            "ar": "ar-SA",
        }

        voice_language = voice_languages.get(
            language_code,
            "en-US",
        )

        speech_payload = json.dumps(
            st.session_state.last_answer
        )

        speech_html = f"""
        <div style="padding: 10px;">
            <button
                onclick="speakText()"
                style="
                    padding: 12px 18px;
                    border-radius: 12px;
                    border: 1px solid #b99ae8;
                    background: #302044;
                    color: white;
                    cursor: pointer;
                "
            >
                {html.escape(t["read_aloud"])}
            </button>

            <script>
                const textToSpeak = {speech_payload};
                const selectedVoiceLanguage = {json.dumps(voice_language)};

                function speakText() {{
                    if (!('speechSynthesis' in window)) {{
                        alert("Speech synthesis is not supported.");
                        return;
                    }}

                    window.speechSynthesis.cancel();

                    const utterance = new SpeechSynthesisUtterance(
                        textToSpeak
                    );

                    utterance.lang = selectedVoiceLanguage;
                    utterance.rate = 0.95;

                    window.speechSynthesis.speak(utterance);
                }}
            </script>
        </div>
        """

        st.components.v1.html(
            speech_html,
            height=80,
        )


# =========================================================
# 22. FOOTER
# =========================================================

st.markdown(
    f"""
    <div class="lidya-footer">
        💜 Lidya AI | {html.escape(t["tagline"])}
        <br>
        Built with curiosity and Python.
    </div>
    """,
    unsafe_allow_html=True,
)

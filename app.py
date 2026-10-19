import os
import tempfile
import streamlit as st
import streamlit.components.v1 as components

from google import genai
from google.genai import types


# ======================================================
# 1. PAGE CONFIGURATION
# ======================================================

st.set_page_config(
    page_title="Lidya AI",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ======================================================
# 2. CONFIGURATION
# ======================================================

MODEL_NAME = "gemini-3.8-flash"

MAX_FILE_SIZE_MB = 20

LANGUAGES = {
    "Türkçe": "Turkish",
    "English": "English",
    "Français": "French",
    "Deutsch": "German",
    "Español": "Spanish",
    "Italiano": "Italian",
    "日本語": "Japanese",
}


# ======================================================
# 3. TRANSLATIONS
# ======================================================

TRANSLATIONS = {
    "Türkçe": {
        "subtitle": "Düşün. Öğren. Üret. Keşfet.",
        "language": "Arayüz ve yanıt dili",
        "modules": "ÇALIŞMA ALANLARI",
        "clear": "Sohbeti temizle",
        "voice": "Yanıtı sesli oku",
        "thinking": "Lidya düşünüyor...",
        "chat": "Lidya'ya bir şey sor...",
        "upload": "İncelemek için dosya yükle",
        "welcome": "Merhaba! Ben Lidya. Sana nasıl yardımcı olabilirim?",
        "sources": "Araştırma kaynakları",
        "no_key": "API anahtarı bulunamadı. Streamlit Secrets ayarını kontrol et.",
        "file_limit": "Dosya boyutu sınırı",
        "file_error": "Dosya incelenirken hata oluştu",
        "chat_error": "Yanıt oluşturulamadı",
        "footer": "Merakla ve Python ile geliştirildi.",
        "search_info": "Güncel sorularda Google Search kullanılabilir.",
        "medical_notice": "Eğitim amaçlıdır; tanı veya tedavi kararlarının yerini tutmaz.",
        "legal_notice": "Genel hukuki bilgidir; ilgili ülkenin hukukunu doğrula.",
        "smart_notice": "Bu sürüm akıllı cihazları doğrudan kontrol etmez.",
        "image_notice": "Bu alan görsel üretimi için istem hazırlamaya ayrılmıştır.",
        "video_notice": "Bu alan video üretimi için istem hazırlamaya ayrılmıştır.",
        "prompt_label": "Ne oluşturmak istiyorsun?",
        "prepare": "İstemi hazırla",
        "file_selected": "Seçilen dosya",
        "search_toggle": "İnternet araştırmasını etkinleştir",
        "search_on": "İnternet araştırması etkin",
        "search_off": "Yalnızca model bilgisi kullanılıyor",
    },
    "English": {
        "subtitle": "Think. Learn. Create. Discover.",
        "language": "Interface and response language",
        "modules": "WORKSPACES",
        "clear": "Clear conversation",
        "voice": "Read the answer aloud",
        "thinking": "Lidya is thinking...",
        "chat": "Ask Lidya anything...",
        "upload": "Upload a file to analyze",
        "welcome": "Hello! I'm Lidya. How can I help you?",
        "sources": "Research sources",
        "no_key": "API key not found. Check your Streamlit Secrets.",
        "file_limit": "File size limit",
        "file_error": "An error occurred while analyzing the file",
        "chat_error": "Could not generate a response",
        "footer": "Built with curiosity and Python.",
        "search_info": "Google Search can be used for current questions.",
        "medical_notice": "For education only; not a substitute for diagnosis or treatment.",
        "legal_notice": "General legal information; verify the applicable jurisdiction.",
        "smart_notice": "This version does not directly control smart devices.",
        "image_notice": "This workspace prepares prompts for image generation.",
        "video_notice": "This workspace prepares prompts for video generation.",
        "prompt_label": "What would you like to create?",
        "prepare": "Prepare prompt",
        "file_selected": "Selected file",
        "search_toggle": "Enable internet research",
        "search_on": "Internet research is enabled",
        "search_off": "Using model knowledge only",
    },
    "Français": {
        "subtitle": "Réfléchir. Apprendre. Créer. Découvrir.",
        "language": "Langue de l'interface et des réponses",
        "modules": "ESPACES DE TRAVAIL",
        "clear": "Effacer la conversation",
        "voice": "Lire la réponse à voix haute",
        "thinking": "Lidya réfléchit...",
        "chat": "Posez une question à Lidya...",
        "upload": "Importer un fichier à analyser",
        "welcome": "Bonjour ! Je suis Lidya. Comment puis-je vous aider ?",
        "sources": "Sources de recherche",
        "no_key": "Clé API introuvable. Vérifiez les paramètres Secrets.",
        "file_limit": "Limite de taille du fichier",
        "file_error": "Erreur lors de l'analyse du fichier",
        "chat_error": "Impossible de générer une réponse",
        "footer": "Créé avec curiosité et Python.",
        "search_info": "Google Search peut être utilisé pour les questions actuelles.",
        "medical_notice": "À des fins éducatives uniquement, sans remplacer un avis médical.",
        "legal_notice": "Informations juridiques générales ; vérifiez la juridiction applicable.",
        "smart_notice": "Cette version ne contrôle pas directement les appareils connectés.",
        "image_notice": "Cet espace prépare des descriptions pour générer des images.",
        "video_notice": "Cet espace prépare des descriptions pour générer des vidéos.",
        "prompt_label": "Que souhaitez-vous créer ?",
        "prepare": "Préparer la description",
        "file_selected": "Fichier sélectionné",
        "search_toggle": "Activer la recherche Internet",
        "search_on": "Recherche Internet activée",
        "search_off": "Utilisation des connaissances du modèle uniquement",
    },
    "Deutsch": {
        "subtitle": "Denken. Lernen. Gestalten. Entdecken.",
        "language": "Sprache der Oberfläche und Antworten",
        "modules": "ARBEITSBEREICHE",
        "clear": "Unterhaltung löschen",
        "voice": "Antwort vorlesen",
        "thinking": "Lidya denkt nach...",
        "chat": "Frage Lidya etwas...",
        "upload": "Datei zur Analyse hochladen",
        "welcome": "Hallo! Ich bin Lidya. Wie kann ich dir helfen?",
        "sources": "Recherchequellen",
        "no_key": "API-Schlüssel fehlt. Überprüfe die Streamlit-Secrets.",
        "file_limit": "Dateigrößenlimit",
        "file_error": "Fehler bei der Dateianalyse",
        "chat_error": "Antwort konnte nicht erstellt werden",
        "footer": "Mit Neugier und Python entwickelt.",
        "search_info": "Google Search kann für aktuelle Fragen verwendet werden.",
        "medical_notice": "Nur zu Bildungszwecken; kein Ersatz für Diagnose oder Behandlung.",
        "legal_notice": "Allgemeine Rechtsinformationen; die geltende Rechtsordnung prüfen.",
        "smart_notice": "Diese Version steuert keine Smart-Geräte direkt.",
        "image_notice": "Dieser Bereich erstellt Eingaben für die Bildgenerierung.",
        "video_notice": "Dieser Bereich erstellt Eingaben für die Videogenerierung.",
        "prompt_label": "Was möchtest du erstellen?",
        "prepare": "Eingabe vorbereiten",
        "file_selected": "Ausgewählte Datei",
        "search_toggle": "Internetsuche aktivieren",
        "search_on": "Internetsuche aktiviert",
        "search_off": "Nur Modellwissen wird verwendet",
    },
    "Español": {
        "subtitle": "Piensa. Aprende. Crea. Descubre.",
        "language": "Idioma de la interfaz y las respuestas",
        "modules": "ESPACIOS DE TRABAJO",
        "clear": "Borrar conversación",
        "voice": "Leer la respuesta en voz alta",
        "thinking": "Lidya está pensando...",
        "chat": "Pregúntale algo a Lidya...",
        "upload": "Subir un archivo para analizar",
        "welcome": "¡Hola! Soy Lidya. ¿Cómo puedo ayudarte?",
        "sources": "Fuentes de investigación",
        "no_key": "No se encontró la clave API. Revisa los Secrets.",
        "file_limit": "Límite de tamaño del archivo",
        "file_error": "Error al analizar el archivo",
        "chat_error": "No se pudo generar una respuesta",
        "footer": "Creado con curiosidad y Python.",
        "search_info": "Google Search puede utilizarse para preguntas actuales.",
        "medical_notice": "Solo para educación; no sustituye un diagnóstico o tratamiento.",
        "legal_notice": "Información jurídica general; verifica la jurisdicción aplicable.",
        "smart_notice": "Esta versión no controla directamente dispositivos inteligentes.",
        "image_notice": "Este espacio prepara instrucciones para generar imágenes.",
        "video_notice": "Este espacio prepara instrucciones para generar vídeos.",
        "prompt_label": "¿Qué quieres crear?",
        "prepare": "Preparar instrucciones",
        "file_selected": "Archivo seleccionado",
        "search_toggle": "Activar búsqueda en Internet",
        "search_on": "Búsqueda en Internet activada",
        "search_off": "Solo se usa el conocimiento del modelo",
    },
    "Italiano": {
        "subtitle": "Pensa. Impara. Crea. Scopri.",
        "language": "Lingua dell'interfaccia e delle risposte",
        "modules": "SPAZI DI LAVORO",
        "clear": "Cancella conversazione",
        "voice": "Leggi la risposta ad alta voce",
        "thinking": "Lidya sta pensando...",
        "chat": "Chiedi qualcosa a Lidya...",
        "upload": "Carica un file da analizzare",
        "welcome": "Ciao! Sono Lidya. Come posso aiutarti?",
        "sources": "Fonti della ricerca",
        "no_key": "Chiave API mancante. Controlla i Secrets.",
        "file_limit": "Limite dimensione file",
        "file_error": "Errore durante l'analisi del file",
        "chat_error": "Impossibile generare una risposta",
        "footer": "Creato con curiosità e Python.",
        "search_info": "Google Search può essere usato per domande attuali.",
        "medical_notice": "Solo per scopi educativi; non sostituisce diagnosi o cure.",
        "legal_notice": "Informazioni legali generali; verifica la giurisdizione pertinente.",
        "smart_notice": "Questa versione non controlla direttamente i dispositivi intelligenti.",
        "image_notice": "Questo spazio prepara descrizioni per generare immagini.",
        "video_notice": "Questo spazio prepara descrizioni per generare video.",
        "prompt_label": "Che cosa vuoi creare?",
        "prepare": "Prepara la descrizione",
        "file_selected": "File selezionato",
        "search_toggle": "Attiva la ricerca su Internet",
        "search_on": "Ricerca Internet attivata",
        "search_off": "Si utilizza solo la conoscenza del modello",
    },
    "日本語": {
        "subtitle": "考える。学ぶ。創造する。発見する。",
        "language": "画面と言語",
        "modules": "ワークスペース",
        "clear": "会話を消去",
        "voice": "回答を読み上げる",
        "thinking": "Lidyaが考えています...",
        "chat": "Lidyaに質問する...",
        "upload": "分析するファイルをアップロード",
        "welcome": "こんにちは！Lidyaです。どのようにお手伝いできますか？",
        "sources": "調査ソース",
        "no_key": "APIキーが見つかりません。Secretsを確認してください。",
        "file_limit": "ファイルサイズ制限",
        "file_error": "ファイル分析中にエラーが発生しました",
        "chat_error": "回答を生成できませんでした",
        "footer": "好奇心とPythonで開発。",
        "search_info": "最新の質問にはGoogle Searchを使用できます。",
        "medical_notice": "教育目的のみです。診断や治療の代わりにはなりません。",
        "legal_notice": "一般的な法律情報です。適用される法域を確認してください。",
        "smart_notice": "このバージョンはスマートデバイスを直接操作しません。",
        "image_notice": "この領域では画像生成用の指示を準備します。",
        "video_notice": "この領域では動画生成用の指示を準備します。",
        "prompt_label": "何を作成しますか？",
        "prepare": "指示を準備",
        "file_selected": "選択したファイル",
        "search_toggle": "インターネット検索を有効にする",
        "search_on": "インターネット検索が有効です",
        "search_off": "モデルの知識のみを使用しています",
    },
}


# ======================================================
# 4. MODULES
# ======================================================

MODULES = {
    "💜 Lidya": {
        "en": "General Assistant",
        "description": (
            "Help with everyday questions, learning, "
            "research, writing and programming."
        ),
    },
    "📁 File Laboratory": {
        "en": "File Laboratory",
        "description": (
            "Analyze supported images, PDFs, audio and videos."
        ),
    },
    "🩺 Medical & Anatomy": {
        "en": "Medical & Anatomy",
        "description": (
            "Explain anatomy and medical illustrations "
            "for educational purposes."
        ),
    },
    "⚖️ Legal Research": {
        "en": "Legal Research",
        "description": (
            "Explain legal concepts and summarize documents."
        ),
    },
    "🌍 Language Teacher": {
        "en": "Language Teacher",
        "description": (
            "Practice languages, grammar, vocabulary and translation."
        ),
    },
    "💻 Software Engineering": {
        "en": "Software Engineering",
        "description": (
            "Programming, debugging and software design."
        ),
    },
    "🔬 Science & Research": {
        "en": "Science & Research",
        "description": "Scientific concepts and research.",
    },
    "📐 Mathematics": {
        "en": "Mathematics",
        "description": "Mathematical explanations and problem-solving.",
    },
    "⚙️ Engineering": {
        "en": "Engineering",
        "description": "Engineering principles and calculations.",
    },
    "📚 Education": {
        "en": "Education",
        "description": "Learning materials and explanations.",
    },
    "📊 Business & Economics": {
        "en": "Business & Economics",
        "description": "Business, economics and data concepts.",
    },
    "✍️ Writing & Creativity": {
        "en": "Writing & Creativity",
        "description": "Writing, editing and brainstorming.",
    },
    "📈 Data Analysis": {
        "en": "Data Analysis",
        "description": "Data interpretation and analysis.",
    },
    "🔐 Cybersecurity": {
        "en": "Cybersecurity",
        "description": "Defensive security and secure coding.",
    },
    "🏠 Smart Devices": {
        "en": "Smart Devices",
        "description": "Plan safe smart-home integrations.",
    },
    "🎨 Image Studio": {
        "en": "Image Studio",
        "description": "Prepare image-generation prompts.",
    },
    "🎬 Video Studio": {
        "en": "Video Studio",
        "description": "Prepare video-generation prompts.",
    },
}


MODULE_TRANSLATIONS = {
    "Türkçe": {
        "💜 Lidya": "💜 Lidya",
        "📁 File Laboratory": "📁 Dosya Laboratuvarı",
        "🩺 Medical & Anatomy": "🩺 Tıp ve Anatomi",
        "⚖️ Legal Research": "⚖️ Hukuk Araştırmaları",
        "🌍 Language Teacher": "🌍 Dil Öğretmeni",
        "💻 Software Engineering": "💻 Yazılım Mühendisliği",
        "🔬 Science & Research": "🔬 Bilim ve Araştırma",
        "📐 Mathematics": "📐 Matematik",
        "⚙️ Engineering": "⚙️ Mühendislik",
        "📚 Education": "📚 Eğitim",
        "📊 Business & Economics": "📊 İşletme ve Ekonomi",
        "✍️ Writing & Creativity": "✍️ Yazma ve Yaratıcılık",
        "📈 Data Analysis": "📈 Veri Analizi",
        "🔐 Cybersecurity": "🔐 Siber Güvenlik",
        "🏠 Smart Devices": "🏠 Akıllı Cihazlar",
        "🎨 Image Studio": "🎨 Görsel Atölyesi",
        "🎬 Video Studio": "🎬 Video Atölyesi",
    },
    "English": {},
    "Français": {
        "💜 Lidya": "💜 Lidya",
        "📁 File Laboratory": "📁 Laboratoire de fichiers",
        "🩺 Medical & Anatomy": "🩺 Médecine et anatomie",
        "⚖️ Legal Research": "⚖️ Recherche juridique",
        "🌍 Language Teacher": "🌍 Professeur de langues",
        "💻 Software Engineering": "💻 Développement logiciel",
        "🔬 Science & Research": "🔬 Sciences et recherche",
        "📐 Mathematics": "📐 Mathématiques",
        "⚙️ Engineering": "⚙️ Ingénierie",
        "📚 Education": "📚 Éducation",
        "📊 Business & Economics": "📊 Économie et entreprise",
        "✍️ Writing & Creativity": "✍️ Écriture et créativité",
        "📈 Data Analysis": "📈 Analyse de données",
        "🔐 Cybersecurity": "🔐 Cybersécurité",
        "🏠 Smart Devices": "🏠 Appareils connectés",
        "🎨 Image Studio": "🎨 Studio d'images",
        "🎬 Video Studio": "🎬 Studio vidéo",
    },
    "Deutsch": {
        "💜 Lidya": "💜 Lidya",
        "📁 File Laboratory": "📁 Dateilabor",
        "🩺 Medical & Anatomy": "🩺 Medizin und Anatomie",
        "⚖️ Legal Research": "⚖️ Rechtsrecherche",
        "🌍 Language Teacher": "🌍 Sprachlehrer",
        "💻 Software Engineering": "💻 Softwareentwicklung",
        "🔬 Science & Research": "🔬 Wissenschaft und Forschung",
        "📐 Mathematics": "📐 Mathematik",
        "⚙️ Engineering": "⚙️ Ingenieurwesen",
        "📚 Education": "📚 Bildung",
        "📊 Business & Economics": "📊 Wirtschaft",
        "✍️ Writing & Creativity": "✍️ Schreiben und Kreativität",
        "📈 Data Analysis": "📈 Datenanalyse",
        "🔐 Cybersecurity": "🔐 Cybersicherheit",
        "🏠 Smart Devices": "🏠 Smart-Geräte",
        "🎨 Image Studio": "🎨 Bildstudio",
        "🎬 Video Studio": "🎬 Videostudio",
    },
    "Español": {
        "💜 Lidya": "💜 Lidya",
        "📁 File Laboratory": "📁 Laboratorio de archivos",
        "🩺 Medical & Anatomy": "🩺 Medicina y anatomía",
        "⚖️ Legal Research": "⚖️ Investigación jurídica",
        "🌍 Language Teacher": "🌍 Profesor de idiomas",
        "💻 Software Engineering": "💻 Ingeniería de software",
        "🔬 Science & Research": "🔬 Ciencia e investigación",
        "📐 Mathematics": "📐 Matemáticas",
        "⚙️ Engineering": "⚙️ Ingeniería",
        "📚 Education": "📚 Educación",
        "📊 Business & Economics": "📊 Negocios y economía",
        "✍️ Writing & Creativity": "✍️ Escritura y creatividad",
        "📈 Data Analysis": "📈 Análisis de datos",
        "🔐 Cybersecurity": "🔐 Ciberseguridad",
        "🏠 Smart Devices": "🏠 Dispositivos inteligentes",
        "🎨 Image Studio": "🎨 Estudio de imágenes",
        "🎬 Video Studio": "🎬 Estudio de vídeo",
    },
    "Italiano": {
        "💜 Lidya": "💜 Lidya",
        "📁 File Laboratory": "📁 Laboratorio file",
        "🩺 Medical & Anatomy": "🩺 Medicina e anatomia",
        "⚖️ Legal Research": "⚖️ Ricerca legale",
        "🌍 Language Teacher": "🌍 Insegnante di lingue",
        "💻 Software Engineering": "💻 Ingegneria del software",
        "🔬 Science & Research": "🔬 Scienza e ricerca",
        "📐 Mathematics": "📐 Matematica",
        "⚙️ Engineering": "⚙️ Ingegneria",
        "📚 Education": "📚 Istruzione",
        "📊 Business & Economics": "📊 Economia e impresa",
        "✍️ Writing & Creativity": "✍️ Scrittura e creatività",
        "📈 Data Analysis": "📈 Analisi dei dati",
        "🔐 Cybersecurity": "🔐 Sicurezza informatica",
        "🏠 Smart Devices": "🏠 Dispositivi intelligenti",
        "🎨 Image Studio": "🎨 Studio immagini",
        "🎬 Video Studio": "🎬 Studio video",
    },
    "日本語": {
        "💜 Lidya": "💜 Lidya",
        "📁 File Laboratory": "📁 ファイル分析",
        "🩺 Medical & Anatomy": "🩺 医学・解剖学",
        "⚖️ Legal Research": "⚖️ 法律調査",
        "🌍 Language Teacher": "🌍 語学学習",
        "💻 Software Engineering": "💻 ソフトウェア開発",
        "🔬 Science & Research": "🔬 科学・研究",
        "📐 Mathematics": "📐 数学",
        "⚙️ Engineering": "⚙️ 工学",
        "📚 Education": "📚 教育",
        "📊 Business & Economics": "📊 ビジネス・経済",
        "✍️ Writing & Creativity": "✍️ 文章・創作",
        "📈 Data Analysis": "📈 データ分析",
        "🔐 Cybersecurity": "🔐 サイバーセキュリティ",
        "🏠 Smart Devices": "🏠 スマートデバイス",
        "🎨 Image Studio": "🎨 画像スタジオ",
        "🎬 Video Studio": "🎬 動画スタジオ",
    },
}


# ======================================================
# 5. API CLIENT
# ======================================================

def get_api_key():
    try:
        return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        return os.environ.get("GEMINI_API_KEY", "")


@st.cache_resource
def get_client(api_key):
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=60000,
        ),
    )


API_KEY = get_api_key()
client = get_client(API_KEY) if API_KEY else None


# ======================================================
# 6. VISUAL DESIGN
# ======================================================

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(
                circle at top,
                #30204f 0%,
                #141326 48%,
                #090914 100%
            );
        color: #f4efff;
    }

    [data-testid="stSidebar"] {
        background: #111020;
        border-right: 1px solid #3b2b59;
    }

    .lidya-title {
        font-size: 48px;
        font-weight: 900;
        letter-spacing: 4px;
        text-align: center;
        background: linear-gradient(
            90deg,
            #f6d7ff,
            #bb9aff,
            #83e8ff
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .lidya-subtitle {
        text-align: center;
        color: #d3c8f5;
        font-size: 16px;
    }

    .orb {
        width: 110px;
        height: 110px;
        margin: 20px auto;
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
            0 0 60px #8255ff;
        animation: float 3s ease-in-out infinite;
    }

    @keyframes float {
        0%, 100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-10px);
        }
    }

    [data-testid="stChatMessage"] {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(200,170,255,0.17);
        border-radius: 15px;
    }

    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ======================================================
# 7. SYSTEM INSTRUCTIONS
# ======================================================

def build_system_instruction(module, language):

    module_info = MODULES[module]

    return f"""
You are Lidya AI, a helpful, careful and accurate AI assistant.

Current workspace: {module_info["en"]}
Workspace purpose: {module_info["description"]}

Respond in {LANGUAGES[language]} unless the user asks
for a different language.

RESEARCH:
When internet research is enabled and the question requires
current or externally verifiable information, use Google Search.
Explain the evidence, distinguish facts from uncertainty, and
use the actual sources returned by the search tool.
Never invent citations, URLs, quotations or search results.
If reliable evidence is insufficient, say so.

MEDICAL:
Provide educational information, not definitive personal
diagnoses or treatment decisions. For medical illustrations,
describe visible structures and flag uncertain identifications.
Important clinical decisions must be checked by qualified
healthcare professionals.

LEGAL:
Provide general legal information. Ask which jurisdiction
applies when relevant. Do not claim to be the user's lawyer.

PRIVACY:
Do not request passwords, API keys or unnecessary sensitive
information. Avoid uploading identifiable patient information.

SMART DEVICES:
This app cannot directly control physical devices.
Never claim to have activated or changed a device.

Be transparent about limitations and uncertainty.
"""


# ======================================================
# 8. FILE HANDLING
# ======================================================

def prepare_file(uploaded_file):

    if uploaded_file is None:
        return None

    file_bytes = uploaded_file.getvalue()

    if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValueError(
            f"File is larger than {MAX_FILE_SIZE_MB} MB."
        )

    mime_type = (
        uploaded_file.type
        or "application/octet-stream"
    )

    # Images: send directly as image parts.
    if mime_type.startswith("image/"):
        return types.Part.from_bytes(
            data=file_bytes,
            mime_type=mime_type,
        )

    # Documents, audio and video: upload to the Files API.
    supported = (
        mime_type == "application/pdf"
        or mime_type.startswith("audio/")
        or mime_type.startswith("video/")
    )

    if not supported:
        raise ValueError(
            "Unsupported file type. Use an image, PDF, "
            "audio file or video file."
        )

    suffix = os.path.splitext(
        uploaded_file.name
    )[1]

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name

        remote_file = client.files.upload(
            file=temp_path
        )

        # Wait briefly for processing when required.
        for _ in range(15):
            state = getattr(
                remote_file,
                "state",
                None,
            )

            state_name = getattr(
                state,
                "name",
                str(state or ""),
            )

            if state_name in ("ACTIVE", "None", ""):
                break

            if state_name == "FAILED":
                raise RuntimeError(
                    "The uploaded file could not be processed."
                )

            time.sleep(2)

            remote_file = client.files.get(
                name=remote_file.name
            )

        return remote_file

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# ======================================================
# 9. GOOGLE SEARCH + CHAT
# ======================================================

def ask_lidya(
    prompt,
    module,
    language,
    history,
    uploaded_file=None,
    internet_search=True,
):

    if client is None:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it in "
            "Streamlit Cloud → Settings → Secrets."
        )

    instruction = build_system_instruction(
        module,
        language,
    )

    # Keep the latest messages to limit response time.
    recent_history = history[-8:]

    history_text = "\n\n".join(
        (
            "User: "
            if item["role"] == "user"
            else "Lidya: "
        )
        + item["content"]
        for item in recent_history
    )

    parts = [
        types.Part.from_text(
            text=(
                f"Recent conversation:\n{history_text}\n\n"
                f"Current message:\n{prompt}"
            )
        )
    ]

    if uploaded_file is not None:
        file_part = prepare_file(uploaded_file)

        if isinstance(file_part, types.Part):
            parts.append(file_part)

        elif file_part is not None:
            parts.append(
                types.Part.from_uri(
                    file_uri=file_part.uri,
                    mime_type=file_part.mime_type,
                )
            )

    tools = []

    if internet_search:
        tools.append(
            types.Tool(
                google_search=types.GoogleSearch()
            )
        )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            types.Content(
                role="user",
                parts=parts,
            )
        ],
        config=types.GenerateContentConfig(
            system_instruction=instruction,
            tools=tools if tools else None,
            temperature=0.4,
            max_output_tokens=1800,
        ),
    )

    answer = getattr(response, "text", None)

    if not answer:
        raise RuntimeError(
            "The model returned no text. Check model access "
            "and the API response."
        )

    sources = []

    # Collect actual URLs from Google Search grounding metadata.
    try:
        candidates = getattr(
            response,
            "candidates",
            [],
        )

        if candidates:
            metadata = getattr(
                candidates[0],
                "grounding_metadata",
                None,
            )

            chunks = getattr(
                metadata,
                "grounding_chunks",
                [],
            ) if metadata else []

            for chunk in chunks:
                web_info = getattr(
                    chunk,
                    "web",
                    None,
                )

                if not web_info:
                    continue

                uri = getattr(
                    web_info,
                    "uri",
                    None,
                )

                title = getattr(
                    web_info,
                    "title",
                    None,
                )

                if uri and uri.startswith("https://"):
                    item = (title or uri, uri)

                    if item not in sources:
                        sources.append(item)

    except Exception:
        # Do not break the answer if source metadata is absent.
        sources = []

    return answer, sources


# ======================================================
# 10. SESSION STATE
# ======================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""

if "last_sources" not in st.session_state:
    st.session_state.last_sources = []


# ======================================================
# 11. SIDEBAR AND LANGUAGE
# ======================================================

with st.sidebar:

    st.markdown("## 💜 Lidya AI")

    language = st.selectbox(
        "🌍 Language / Dil",
        list(LANGUAGES.keys()),
        key="interface_language",
    )

    ui = TRANSLATIONS[language]

    st.markdown(f"### {ui['modules']}")

    module_keys = list(MODULES.keys())

    module_labels = [
        MODULE_TRANSLATIONS.get(language, {}).get(
            key,
            key,
        )
        for key in module_keys
    ]

    selected_label = st.radio(
        ui["modules"],
        module_labels,
        label_visibility="collapsed",
    )

    selected_module = module_keys[
        module_labels.index(selected_label)
    ]

    internet_search = st.toggle(
        ui["search_toggle"],
        value=True,
    )

    if internet_search:
        st.caption("🌐 " + ui["search_on"])
    else:
        st.caption("📚 " + ui["search_off"])

    voice_output = st.checkbox(
        ui["voice"],
        value=False,
    )

    if st.button(
        ui["clear"],
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.session_state.last_answer = ""
        st.session_state.last_sources = []
        st.rerun()

    st.divider()

    st.caption(
        "💜 Lidya AI"
    )


# ======================================================
# 12. MAIN HEADER
# ======================================================

st.markdown(
    '<div class="lidya-title">LIDYA AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="lidya-subtitle">{ui["subtitle"]}</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="orb"></div>',
    unsafe_allow_html=True,
)

st.subheader(
    MODULE_TRANSLATIONS.get(language, {}).get(
        selected_module,
        selected_module,
    )
)

st.caption(
    MODULES[selected_module]["description"]
)


# ======================================================
# 13. SPECIAL MODULE MESSAGES
# ======================================================

if selected_module == "🩺 Medical & Anatomy":
    st.info(ui["medical_notice"])

if selected_module == "⚖️ Legal Research":
    st.info(ui["legal_notice"])

if selected_module == "🏠 Smart Devices":
    st.info(ui["smart_notice"])


# ======================================================
# 14. IMAGE AND VIDEO PROMPT WORKSPACES
# ======================================================

if selected_module in (
    "🎨 Image Studio",
    "🎬 Video Studio",
):

    if selected_module == "🎨 Image Studio":
        st.info(ui["image_notice"])
    else:
        st.info(ui["video_notice"])

    creative_prompt = st.text_area(
        ui["prompt_label"],
        height=150,
    )

    if st.button(ui["prepare"]):
        if creative_prompt.strip():
            st.code(
                creative_prompt.strip(),
                language=None,
            )
        else:
            st.warning(
                ui["prompt_label"]
            )


# ======================================================
# 15. FILE UPLOAD
# ======================================================

uploaded_file = None

if selected_module in (
    "📁 File Laboratory",
    "🩺 Medical & Anatomy",
):

    uploaded_file = st.file_uploader(
        ui["upload"],
        type=[
            "png",
            "jpg",
            "jpeg",
            "webp",
            "gif",
            "pdf",
            "mp4",
            "mov",
            "mp3",
            "wav",
            "m4a",
        ],
    )

    if uploaded_file:

        st.caption(
            f"{ui['file_selected']}: {uploaded_file.name}"
        )

        mime = uploaded_file.type or ""

        if mime.startswith("image/"):
            st.image(
                uploaded_file,
                use_container_width=True,
            )

        elif mime.startswith("video/"):
            st.video(uploaded_file)


# ======================================================
# 16. CHAT HISTORY
# ======================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"],
        avatar=(
            "💜"
            if message["role"] == "assistant"
            else "🧑‍💻"
        ),
    ):
        st.markdown(message["content"])


# ======================================================
# 17. CHAT INPUT
# ======================================================

if selected_module not in (
    "🎨 Image Studio",
    "🎬 Video Studio",
):

    prompt = st.chat_input(
        ui["chat"]
    )

    if prompt:

        previous_history = list(
            st.session_state.messages
        )

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        with st.chat_message(
            "user",
            avatar="🧑‍💻",
        ):
            st.markdown(prompt)

        with st.chat_message(
            "assistant",
            avatar="💜",
        ):

            status = st.empty()

            try:

                status.info(
                    "💜 " + ui["thinking"]
                )

                with st.spinner(
                    ui["thinking"]
                ):

                    answer, sources = ask_lidya(
                        prompt=prompt,
                        module=selected_module,
                        language=language,
                        history=previous_history,
                        uploaded_file=uploaded_file,
                        internet_search=internet_search,
                    )

                status.empty()

                st.markdown(answer)

                if sources:
                    with st.expander(ui["sources"]):
                        for title, url in sources:
                            st.markdown(
                                f"- [{title}]({url})"
                            )

                st.session_state.last_answer = answer
                st.session_state.last_sources = sources

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

            except Exception as error:

                status.error(
                    ui["chat_error"]
                )

                st.error(
                    f"{type(error).__name__}: {error}"
                )

                st.info(
                    "Check your API key, model access, "
                    "internet connection and file format."
                )


# ======================================================
# 18. TEXT-TO-SPEECH
# ======================================================

if (
    voice_output
    and st.session_state.last_answer
):

    speech_text = st.session_state.last_answer

    speech_language = {
        "Türkçe": "tr-TR",
        "English": "en-US",
        "Français": "fr-FR",
        "Deutsch": "de-DE",
        "Español": "es-ES",
        "Italiano": "it-IT",
        "日本語": "ja-JP",
    }[language]

    import json

    safe_text = json.dumps(
        speech_text,
        ensure_ascii=False,
    )

    components.html(
        f"""
        <script>
        const text = {safe_text};
        const utterance =
            new SpeechSynthesisUtterance(text);

        utterance.lang = "{speech_language}";
        utterance.rate = 1.0;

        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
        </script>
        """,
        height=0,
    )


# ======================================================
# 19. FOOTER
# ======================================================

st.markdown(
    f"""
    <div style="
        text-align:center;
        color:#b9a9dc;
        padding:30px 0 10px 0;
        font-size:13px;
    ">
        💜 Lidya AI · {ui["footer"]}
    </div>
    """,
    unsafe_allow_html=True,
)

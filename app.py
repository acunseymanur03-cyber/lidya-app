import os
import json
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
    "📁 File Laboratory": ("File Laboratory", "Help the user understand text they paste from documents. This version does not directly process uploaded files."),
    "🩺 Medical & Anatomy": ("Medical & Anatomy", "Explain anatomy and medical concepts for education, not personal diagnosis or treatment."),
    "⚖️ Legal Research": ("Legal Research", "Explain general legal concepts; ask which jurisdiction applies when relevant."),
    "🌍 Language Teacher": ("Language Teacher", "Practice languages, grammar, vocabulary, writing and translation."),
    "💻 Software Engineering": ("Software Engineering", "Programming, debugging, code review and software design."),
    "🔬 Science & Research": ("Science & Research", "Explain scientific concepts, methods and uncertainty."),
    "📐 Mathematics": ("Mathematics", "Solve math problems carefully and explain steps."),
    "⚙️ Engineering": ("Engineering", "Explain engineering principles and calculations."),
    "📚 Education": ("Education", "Create learning plans, explanations and study activities."),
    "📊 Business & Economics": ("Business & Economics", "Explain business, economics and data concepts."),
    "✍️ Writing & Creativity": ("Writing & Creativity", "Help brainstorm, write, revise and edit original text."),
    "📈 Data Analysis": ("Data Analysis", "Help interpret data and explain analysis methods."),
    "🔐 Cybersecurity": ("Cybersecurity", "Focus on defensive security, privacy and secure coding."),
    "🏠 Smart Devices": ("Smart Devices", "Plan safe smart-home integrations; do not claim to control devices."),
    "🎨 Image Studio": ("Image Studio", "Create detailed prompts for image-generation tools."),
    "🎬 Video Studio": ("Video Studio", "Create detailed prompts for video-generation tools."),
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
        "welcome": "Merhaba! Ben Lidya. Sana nasıl yardımcı olabilirim?",
        "no_key": "GROQ_API_KEY bulunamadı. Streamlit Secrets ayarını kontrol et.",
        "footer": "Merakla ve Python ile geliştirildi.",
        "search_off": "Bu sürümde canlı internet araştırması henüz bağlı değil.",
        "creative": "Ne oluşturmak istiyorsun?",
        "prepare": "İstemi hazırla",
        "file_note": "Bu sürüm dosyaları doğrudan analiz etmez. Belgeden metni kopyalayıp sohbete yapıştırabilirsin.",
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
        "search_off": "Live web research is not connected in this version.",
        "creative": "What would you like to create?",
        "prepare": "Prepare prompt",
        "file_note": "This version does not directly analyze uploaded files. Paste document text into the chat.",
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
        "search_off": "La recherche Web en direct n'est pas connectée dans cette version.",
        "creative": "Que souhaitez-vous créer ?",
        "prepare": "Préparer le prompt",
        "file_note": "Cette version n'analyse pas directement les fichiers. Collez le texte du document dans le chat.",
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
        "search_off": "Live-Websuche ist in dieser Version nicht verbunden.",
        "creative": "Was möchtest du erstellen?",
        "prepare": "Prompt vorbereiten",
        "file_note": "Diese Version analysiert keine Dateien direkt. Füge den Dokumenttext in den Chat ein.",
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
        "search_off": "La búsqueda web en directo no está conectada en esta versión.",
        "creative": "¿Qué quieres crear?",
        "prepare": "Preparar instrucciones",
        "file_note": "Esta versión no analiza archivos directamente. Pega el texto del documento en el chat.",
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
        "search_off": "La ricerca web in tempo reale non è collegata in questa versione.",
        "creative": "Che cosa vuoi creare?",
        "prepare": "Prepara il prompt",
        "file_note": "Questa versione non analizza direttamente i file. Incolla il testo nel chat.",
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
        "search_off": "このバージョンではライブWeb検索は接続されていません。",
        "creative": "何を作成しますか？",
        "prepare": "プロンプトを準備",
        "file_note": "このバージョンはファイルを直接分析しません。文書のテキストをチャットに貼り付けてください。",
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

QUALITY:
- Understand the question and use relevant conversation context.
- Give accurate, well-structured answers.
- Explain complex topics step by step, but keep simple answers concise.
- For math, check calculations and show the method.
- For programming, give runnable code when possible and explain important parts.
- Never invent facts, citations, URLs, quotes, or actions you did not perform.
- State uncertainty clearly and correct mistakes when noticed.
- Do not claim to have searched the live internet in this version.
- Do not ask for passwords, API keys, or unnecessary sensitive information.

MEDICAL:
Provide educational information only, not a definitive personal diagnosis or treatment plan.
Encourage qualified medical care for important health decisions.

LEGAL:
Provide general legal information, not legal representation. Ask which jurisdiction applies when relevant.

SMART DEVICES:
This app does not directly control physical devices. Never claim a device was activated or changed.
"""

# ======================================================
# 6. SESSION STATE
# ======================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""

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

    module_keys = list(MODULES.keys())
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

    st.caption("🌐 " + ui["search_off"])
    voice_output = st.checkbox(ui["voice"], value=False)

    if st.button(ui["clear"], use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_answer = ""
        st.rerun()

    st.divider()
    st.caption("💜 Lidya AI")

# ======================================================
# 8. HEADER
# ======================================================
st.markdown('<div class="lidya-title">LIDYA AI</div>', unsafe_allow_html=True)
st.markdown(f'<div class="lidya-subtitle">{ui["subtitle"]}</div>', unsafe_allow_html=True)
st.markdown('<div class="orb"></div>', unsafe_allow_html=True)
st.subheader(MODULE_LABELS.get(language, {}).get(selected_module, selected_module))
st.caption(MODULES[selected_module][1])

if selected_module == "📁 File Laboratory":
    st.info(ui["file_note"])
if selected_module == "🩺 Medical & Anatomy":
    st.info("Eğitim amaçlıdır; tanı veya tedavi kararlarının yerini tutmaz." if language == "Türkçe"
            else "For education only; not a substitute for diagnosis or treatment.")

# Creative workspaces prepare prompts only.
if selected_module in ("🎨 Image Studio", "🎬 Video Studio"):
    creative_prompt = st.text_area(ui["creative"], height=150)
    if st.button(ui["prepare"]):
        if creative_prompt.strip():
            st.code(creative_prompt.strip(), language=None)
        else:
            st.warning(ui["creative"])

# ======================================================
# 9. CHAT HISTORY
# ======================================================
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="💜"):
        st.markdown(ui["welcome"])

for message in st.session_state.messages:
    with st.chat_message(
        message["role"],
        avatar="💜" if message["role"] == "assistant" else "🧑‍💻",
    ):
        st.markdown(message["content"])

# ======================================================
# 10. CHAT
# ======================================================
if selected_module not in ("🎨 Image Studio", "🎬 Video Studio"):
    prompt = st.chat_input(ui["chat"])

    if prompt:
        previous_history = list(st.session_state.messages)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="💜"):
            if client is None:
                st.error(ui["no_key"])
            else:
                try:
                    with st.spinner(ui["thinking"]):
                        api_messages = [
                            {
                                "role": "system",
                                "content": build_system_instruction(selected_module, language),
                            }
                        ]

                        # Include recent messages for conversational context.
                        for item in previous_history[-8:]:
                            if item.get("role") in ("user", "assistant"):
                                api_messages.append({
                                    "role": item["role"],
                                    "content": item["content"],
                                })

                        api_messages.append({"role": "user", "content": prompt})

                        completion = client.chat.completions.create(
                            model=MODEL_NAME,
                            messages=api_messages,
                            temperature=0.4,
                            max_completion_tokens=1800,
                        )

                        answer = completion.choices[0].message.content
                        if not answer:
                            raise RuntimeError("Model boş yanıt döndürdü.")

                    st.markdown(answer)
                    st.session_state.last_answer = answer
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                    })

                except Exception as error:
                    st.error(ui["error"])
                    st.caption(f"{type(error).__name__}: {error}")
                    st.info(
                        "Groq Console'da seçilen modelin erişilebilir olduğunu ve "
                        "ücretsiz kullanım kotasının dolmadığını kontrol et. "
                        "API anahtarını hata mesajıyla birlikte paylaşma."
                    )

# ======================================================
# 11. TEXT-TO-SPEECH
# ======================================================
if voice_output and st.session_state.last_answer:
    speech_language = {
        "Türkçe": "tr-TR",
        "English": "en-US",
        "Français": "fr-FR",
        "Deutsch": "de-DE",
        "Español": "es-ES",
        "Italiano": "it-IT",
        "日本語": "ja-JP",
    }[language]

    safe_text = json.dumps(st.session_state.last_answer, ensure_ascii=False)
    components.html(
        f"""
        <script>
        const text = {safe_text};
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "{speech_language}";
        utterance.rate = 1.0;
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
        </script>
        """,
        height=0,
    )

# ======================================================
# 12. FOOTER
# ======================================================
st.markdown(
    f'<div style="text-align:center;color:#b9a9dc;padding:30px 0 10px;font-size:13px;">'
    f'💜 Lidya AI · {ui["footer"]}</div>',
    unsafe_allow_html=True,
)

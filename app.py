import os
import json
import hashlib
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
    "💜 Lidya": (
        "General Assistant",
        "Everyday questions, learning, research, writing and programming."
    ),
    "📁 File Laboratory": (
        "File Laboratory",
        "Help the user understand text pasted from documents."
    ),
    "🩺 Medical & Anatomy": (
        "Medical & Anatomy",
        "Explain anatomy and medical concepts for education."
    ),
    "⚖️ Legal Research": (
        "Legal Research",
        "Explain general legal concepts and applicable jurisdictions."
    ),
    "🌍 Language Teacher": (
        "Language Teacher",
        "Practice languages, grammar, vocabulary, writing and translation."
    ),
    "💻 Software Engineering": (
        "Software Engineering",
        "Programming, debugging, code review and software design."
    ),
    "🔬 Science & Research": (
        "Science & Research",
        "Explain scientific concepts, methods and uncertainty."
    ),
    "📐 Mathematics": (
        "Mathematics",
        "Solve math problems carefully and explain steps."
    ),
    "⚙️ Engineering": (
        "Engineering",
        "Explain engineering principles and calculations."
    ),
    "📚 Education": (
        "Education",
        "Create learning plans, explanations and study activities."
    ),
    "📊 Business & Economics": (
        "Business & Economics",
        "Explain business, economics and data concepts."
    ),
    "✍️ Writing & Creativity": (
        "Writing & Creativity",
        "Help brainstorm, write, revise and edit original text."
    ),
    "📈 Data Analysis": (
        "Data Analysis",
        "Help interpret data and explain analysis methods."
    ),
    "🔐 Cybersecurity": (
        "Cybersecurity",
        "Focus on defensive security, privacy and secure coding."
    ),
    "🏠 Smart Devices": (
        "Smart Devices",
        "Plan safe smart-home integrations without claiming device control."
    ),
    "🎨 Image Studio": (
        "Image Studio",
        "Prepare image ideas and prompts. Image generation needs a connected service."
    ),
    "🎬 Video Studio": (
        "Video Studio",
        "Prepare video ideas and prompts. Video generation needs a connected service."
    ),
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
        "modules": "ÇALIŞMA ALANLARI",
        "clear": "Sohbeti temizle",
        "voice": "Yanıtı sesli oku",
        "thinking": "Lidya düşünüyor...",
        "chat": "Lidya'ya bir şey sor...",
        "welcome": "Merhaba! Ben Lidya. Sana nasıl yardımcı olabilirim?",
        "no_key": "GROQ_API_KEY bulunamadı. Streamlit Secrets ayarını kontrol et.",
        "footer": "Merakla ve Python ile geliştirildi.",
        "search_off": "Canlı internet araştırması bu sürümde bağlı değil.",
        "creative": "Ne oluşturmak istiyorsun?",
        "prepare": "İstemi hazırla",
        "file_note": "Bu sürüm dosyaları doğrudan analiz etmez. Belgeden metni kopyalayıp sohbete yapıştırabilirsin.",
        "error": "Yanıt oluşturulamadı. API anahtarını, model erişimini ve kotanı kontrol et.",
        "record": "🎙️ Sesli soru sor",
        "record_help": "Kısa bir ses kaydı yap; Lidya konuşmanı yazıya dönüştürüp yanıtlasın.",
        "transcribing": "Konuşman yazıya dönüştürülüyor...",
        "transcription_error": "Ses tanınamadı. Tekrar deneyebilir veya mesajını yazabilirsin.",
        "voice_caption": "Sesli giriş Groq kullanım kotasına tabidir.",
        "image_note": "Gerçek görsel üretimi için ayrıca bir görsel üretim hizmeti bağlanmalıdır.",
        "video_note": "Gerçek video üretimi için ayrıca bir video üretim hizmeti bağlanmalıdır.",
        "speak": "🔊 Yanıtı dinle",
        "stop": "⏹️ Durdur",
        "voice_error": "Sesli yanıt oynatılamadı. Tarayıcının ses desteğini kontrol et.",
    },
    "English": {
        "subtitle": "Think. Learn. Create. Discover.",
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
        "record": "🎙️ Ask by voice",
        "record_help": "Record a short clip; Lidya will transcribe it and respond.",
        "transcribing": "Transcribing your speech...",
        "transcription_error": "Speech was not recognized. Try again or type your message.",
        "voice_caption": "Voice input is subject to Groq usage quotas.",
        "image_note": "Real image generation requires a connected image-generation service.",
        "video_note": "Real video generation requires a connected video-generation service.",
        "speak": "🔊 Listen to answer",
        "stop": "⏹️ Stop",
        "voice_error": "Could not play audio. Check your browser's audio support.",
    },
    "Français": {
        "subtitle": "Réfléchir. Apprendre. Créer. Découvrir.",
        "modules": "ESPACES DE TRAVAIL",
        "clear": "Effacer la conversation",
        "voice": "Lire la réponse à voix haute",
        "thinking": "Lidya réfléchit...",
        "chat": "Posez une question à Lidya...",
        "welcome": "Bonjour ! Je suis Lidya. Comment puis-je vous aider ?",
        "no_key": "GROQ_API_KEY introuvable. Vérifiez les Secrets.",
        "footer": "Créé avec curiosité et Python.",
        "search_off": "La recherche Web en direct n'est pas connectée.",
        "creative": "Que souhaitez-vous créer ?",
        "prepare": "Préparer le prompt",
        "file_note": "Collez le texte du document dans le chat.",
        "error": "Impossible de générer une réponse. Vérifiez la clé API et le quota.",
        "record": "🎙️ Poser une question à voix haute",
        "record_help": "Enregistrez un court extrait pour obtenir une réponse.",
        "transcribing": "Transcription en cours...",
        "transcription_error": "Voix non reconnue. Réessayez ou écrivez votre message.",
        "voice_caption": "L'entrée vocale dépend du quota Groq.",
        "image_note": "La génération d'images nécessite un service connecté.",
        "video_note": "La génération vidéo nécessite un service connecté.",
        "speak": "🔊 Écouter la réponse",
        "stop": "⏹️ Arrêter",
        "voice_error": "Lecture audio impossible. Vérifiez le navigateur.",
    },
    "Deutsch": {
        "subtitle": "Denken. Lernen. Gestalten. Entdecken.",
        "modules": "ARBEITSBEREICHE",
        "clear": "Unterhaltung löschen",
        "voice": "Antwort vorlesen",
        "thinking": "Lidya denkt nach...",
        "chat": "Frage Lidya etwas...",
        "welcome": "Hallo! Ich bin Lidya. Wie kann ich dir helfen?",
        "no_key": "GROQ_API_KEY fehlt. Überprüfe die Streamlit-Secrets.",
        "footer": "Mit Neugier und Python entwickelt.",
        "search_off": "Live-Websuche ist nicht verbunden.",
        "creative": "Was möchtest du erstellen?",
        "prepare": "Prompt vorbereiten",
        "file_note": "Füge den Dokumenttext in den Chat ein.",
        "error": "Antwort konnte nicht erstellt werden. Prüfe API-Schlüssel und Kontingent.",
        "record": "🎙️ Per Sprache fragen",
        "record_help": "Nimm einen kurzen Clip auf; Lidya transkribiert und antwortet.",
        "transcribing": "Sprache wird transkribiert...",
        "transcription_error": "Sprache nicht erkannt. Versuche es erneut oder schreibe deine Nachricht.",
        "voice_caption": "Spracheingabe unterliegt Groq-Kontingenten.",
        "image_note": "Bildgenerierung benötigt einen verbundenen Dienst.",
        "video_note": "Videogenerierung benötigt einen verbundenen Dienst.",
        "speak": "🔊 Antwort anhören",
        "stop": "⏹️ Stoppen",
        "voice_error": "Audio konnte nicht abgespielt werden. Prüfe den Browser.",
    },
    "Español": {
        "subtitle": "Piensa. Aprende. Crea. Descubre.",
        "modules": "ESPACIOS DE TRABAJO",
        "clear": "Borrar conversación",
        "voice": "Leer la respuesta en voz alta",
        "thinking": "Lidya está pensando...",
        "chat": "Pregúntale algo a Lidya...",
        "welcome": "¡Hola! Soy Lidya. ¿Cómo puedo ayudarte?",
        "no_key": "No se encontró GROQ_API_KEY. Revisa los Secrets.",
        "footer": "Creado con curiosidad y Python.",
        "search_off": "La búsqueda web en directo no está conectada.",
        "creative": "¿Qué quieres crear?",
        "prepare": "Preparar instrucciones",
        "file_note": "Pega el texto del documento en el chat.",
        "error": "No se pudo generar una respuesta. Revisa la clave API y la cuota.",
        "record": "🎙️ Preguntar por voz",
        "record_help": "Graba un clip corto; Lidya lo transcribirá y responderá.",
        "transcribing": "Transcribiendo tu voz...",
        "transcription_error": "No se reconoció la voz. Inténtalo de nuevo o escribe el mensaje.",
        "voice_caption": "La entrada de voz está sujeta a las cuotas de Groq.",
        "image_note": "La generación de imágenes requiere un servicio conectado.",
        "video_note": "La generación de vídeo requiere un servicio conectado.",
        "speak": "🔊 Escuchar respuesta",
        "stop": "⏹️ Detener",
        "voice_error": "No se pudo reproducir el audio. Revisa el navegador.",
    },
    "Italiano": {
        "subtitle": "Pensa. Impara. Crea. Scopri.",
        "modules": "SPAZI DI LAVORO",
        "clear": "Cancella conversazione",
        "voice": "Leggi la risposta ad alta voce",
        "thinking": "Lidya sta pensando...",
        "chat": "Chiedi qualcosa a Lidya...",
        "welcome": "Ciao! Sono Lidya. Come posso aiutarti?",
        "no_key": "GROQ_API_KEY mancante. Controlla i Secrets.",
        "footer": "Creato con curiosità e Python.",
        "search_off": "La ricerca web in tempo reale non è collegata.",
        "creative": "Che cosa vuoi creare?",
        "prepare": "Prepara il prompt",
        "file_note": "Incolla il testo del documento nella chat.",
        "error": "Impossibile generare una risposta. Controlla la chiave API e la quota.",
        "record": "🎙️ Chiedi con la voce",
        "record_help": "Registra un breve audio; Lidya lo trascriverà e risponderà.",
        "transcribing": "Trascrizione in corso...",
        "transcription_error": "Voce non riconosciuta. Riprova o scrivi il messaggio.",
        "voice_caption": "L'input vocale dipende dalle quote Groq.",
        "image_note": "La generazione di immagini richiede un servizio collegato.",
        "video_note": "La generazione video richiede un servizio collegato.",
        "speak": "🔊 Ascolta la risposta",
        "stop": "⏹️ Ferma",
        "voice_error": "Impossibile riprodurre l'audio. Controlla il browser.",
    },
    "日本語": {
        "subtitle": "考える。学ぶ。創造する。発見する。",
        "modules": "ワークスペース",
        "clear": "会話を消去",
        "voice": "回答を読み上げる",
        "thinking": "Lidyaが考えています...",
        "chat": "Lidyaに質問する...",
        "welcome": "こんにちは！Lidyaです。どのようにお手伝いできますか？",
        "no_key": "GROQ_API_KEYが見つかりません。Secretsを確認してください。",
        "footer": "好奇心とPythonで開発。",
        "search_off": "ライブWeb検索は接続されていません。",
        "creative": "何を作成しますか？",
        "prepare": "プロンプトを準備",
        "file_note": "文書のテキストをチャットに貼り付けてください。",
        "error": "回答を生成できませんでした。APIキーと利用制限を確認してください。",
        "record": "🎙️ 音声で質問",
        "record_help": "短い音声を録音すると、Lidyaが文字起こしして回答します。",
        "transcribing": "音声を文字起こししています...",
        "transcription_error": "音声を認識できませんでした。再試行するか入力してください。",
        "voice_caption": "音声入力にはGroqの利用制限が適用されます。",
        "image_note": "画像生成には接続されたサービスが必要です。",
        "video_note": "動画生成には接続されたサービスが必要です。",
        "speak": "🔊 回答を聞く",
        "stop": "⏹️ 停止",
        "voice_error": "音声を再生できません。ブラウザを確認してください。",
    },
}

SPEECH_LANGUAGES = {
    "Türkçe": "tr",
    "English": "en",
    "Français": "fr",
    "Deutsch": "de",
    "Español": "es",
    "Italiano": "it",
    "日本語": "ja",
}

TTS_LANGUAGES = {
    "Türkçe": "tr-TR",
    "English": "en-US",
    "Français": "fr-FR",
    "Deutsch": "de-DE",
    "Español": "es-ES",
    "Italiano": "it-IT",
    "日本語": "ja-JP",
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
.lidya-subtitle {
    text-align: center;
    color: #d3c8f5;
    font-size: 16px;
}
.orb {
    width: 100px;
    height: 100px;
    margin: 20px auto;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 25%, #fff, #d5a8ff 15%, #8c54ed 40%, #402078 70%, #161126 100%);
    box-shadow: 0 0 25px #b77cff, 0 0 60px #8255ff;
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0%,100% {transform:translateY(0)}
    50% {transform:translateY(-8px)}
}
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(200,170,255,0.17);
    border-radius: 15px;
}
div[data-testid="stAudioInput"] {
    border: 1px solid rgba(200,170,255,0.35);
    border-radius: 12px;
    padding: 8px;
}
footer {
    visibility: hidden;
}
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

if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = ""

if "pending_voice_prompt" not in st.session_state:
    st.session_state.pending_voice_prompt = ""

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
        st.session_state.last_audio_hash = ""
        st.session_state.pending_voice_prompt = ""
        st.rerun()

    st.divider()
    st.caption("💜 Lidya AI")

# ======================================================
# 8. HEADER
# ======================================================
st.markdown(
    '<div class="lidya-title">LIDYA AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="lidya-subtitle">{ui["subtitle"]}</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="orb"></div>', unsafe_allow_html=True)

st.subheader(
    MODULE_LABELS.get(language, {}).get(selected_module, selected_module)
)

st.caption(MODULES[selected_module][1])

if selected_module == "📁 File Laboratory":
    st.info(ui["file_note"])

if selected_module == "🩺 Medical & Anatomy":
    st.info(
        "Eğitim amaçlıdır; tanı veya tedavi kararlarının yerini tutmaz."
        if language == "Türkçe"
        else "For education only; not a substitute for diagnosis or treatment."
    )

# ======================================================
# 9. CREATIVE WORKSPACES
# ======================================================
if selected_module == "🎨 Image Studio":
    st.info(ui["image_note"])

    image_prompt = st.text_area(
        ui["creative"],
        height=150,
        key="image_prompt",
    )

    if st.button(ui["prepare"], key="prepare_image"):
        if image_prompt.strip():
            st.code(image_prompt.strip(), language=None)
        else:
            st.warning(ui["creative"])

if selected_module == "🎬 Video Studio":
    st.info(ui["video_note"])

    video_prompt = st.text_area(
        ui["creative"],
        height=150,
        key="video_prompt",
    )

    if st.button(ui["prepare"], key="prepare_video"):
        if video_prompt.strip():
            st.code(video_prompt.strip(), language=None)
        else:
            st.warning(ui["creative"])

# ======================================================
# 10. CHAT HISTORY
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
# 11. CHAT + VOICE INPUT
# ======================================================
if selected_module not in ("🎨 Image Studio", "🎬 Video Studio"):

    prompt = st.chat_input(ui["chat"])

    audio_value = st.audio_input(
        ui["record"],
        sample_rate=16000,
        key="lidya_voice_input",
        help=ui["record_help"],
    )

    st.caption(ui["voice_caption"])

    # Process a newly recorded audio clip only once.
    if audio_value is not None:
        audio_bytes = audio_value.getvalue()
        audio_hash = hashlib.sha256(audio_bytes).hexdigest()

        if audio_hash != st.session_state.last_audio_hash:
            st.session_state.last_audio_hash = audio_hash

            if client is None:
                st.error(ui["no_key"])

            else:
                try:
                    with st.spinner(ui["transcribing"]):
                        transcription = client.audio.transcriptions.create(
                            file=("lidya_voice.wav", audio_bytes),
                            model="whisper-large-v3-turbo",
                            language=SPEECH_LANGUAGES.get(language, "en"),
                            response_format="text",
                        )

                        if isinstance(transcription, str):
                            spoken_text = transcription
                        else:
                            spoken_text = transcription.text

                    if spoken_text.strip():
                        st.session_state.pending_voice_prompt = spoken_text.strip()
                        st.rerun()
                    else:
                        st.warning(ui["transcription_error"])

                except Exception as error:
                    st.error(ui["transcription_error"])
                    st.caption(f"{type(error).__name__}: {error}")

    # A voice prompt takes priority over an empty chat box.
    if st.session_state.pending_voice_prompt:
        prompt = st.session_state.pending_voice_prompt
        st.session_state.pending_voice_prompt = ""

    if prompt:
        previous_history = list(st.session_state.messages)

        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
        })

        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="💜"):

            if client is None:
                st.error(ui["no_key"])

            else:
                try:
                    with st.spinner(ui["thinking"]):

                        api_messages = [{
                            "role": "system",
                            "content": build_system_instruction(
                                selected_module,
                                language,
                            ),
                        }]

                        # Keep recent context.
                        for item in previous_history[-8:]:
                            if item.get("role") in ("user", "assistant"):
                                api_messages.append({
                                    "role": item["role"],
                                    "content": item["content"],
                                })

                        api_messages.append({
                            "role": "user",
                            "content": prompt,
                        })

                        completion = client.chat.completions.create(
                            model=MODEL_NAME,
                            messages=api_messages,
                            temperature=0.4,
                            max_completion_tokens=1800,
                        )

                        answer = completion.choices[0].message.content

                        if not answer:
                            raise RuntimeError("Model returned an empty response.")

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
                        "Groq Console'da model erişimini ve kullanım kotanı kontrol et. "
                        "API anahtarını hata mesajıyla birlikte paylaşma."
                    )

# ======================================================
# 12. TEXT-TO-SPEECH
# ======================================================
if voice_output and st.session_state.last_answer:

    safe_text = json.dumps(
        st.session_state.last_answer,
        ensure_ascii=False,
    )

    speech_language = TTS_LANGUAGES.get(language, "en-US")

    components.html(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>
            body {{
                background: transparent;
                color: #f4efff;
                font-family: sans-serif;
                text-align: center;
            }}

            button {{
                background: #8151d9;
                color: white;
                border: 1px solid #b99aff;
                border-radius: 12px;
                padding: 12px 18px;
                margin: 5px;
                font-size: 15px;
                cursor: pointer;
            }}

            button:active {{
                transform: scale(0.97);
            }}
        </style>
        </head>

        <body>
            <button onclick="speakAnswer()">
                {ui["speak"]}
            </button>

            <button onclick="stopAnswer()">
                {ui["stop"]}
            </button>

            <script>
                const answerText = {safe_text};
                const speechLanguage = "{speech_language}";

                function speakAnswer() {{
                    if (!("speechSynthesis" in window)) {{
                        alert("Speech synthesis is not supported in this browser.");
                        return;
                    }}

                    window.speechSynthesis.cancel();

                    const utterance = new SpeechSynthesisUtterance(answerText);
                    utterance.lang = speechLanguage;
                    utterance.rate = 1.0;
                    utterance.pitch = 1.0;

                    window.speechSynthesis.speak(utterance);
                }}

                function stopAnswer() {{
                    if ("speechSynthesis" in window) {{
                        window.speechSynthesis.cancel();
                    }}
                }}
            </script>
        </body>
        </html>
        """,
        height=85,
    )

# ======================================================
# 13. FOOTER
# ======================================================
st.markdown(
    f'<div style="text-align:center;color:#b9a9dc;'
    f'padding:30px 0 10px;font-size:13px;">'
    f'💜 Lidya AI · {ui["footer"]}</div>',
    unsafe_allow_html=True,
)

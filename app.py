import os
import io
import json
import base64
import tempfile
import time

import streamlit as st
import streamlit.components.v1 as components

from google import genai


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Lidya AI | Intelligent Workspace",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =====================================================
# 2. CONFIGURATION
# =====================================================

CHAT_MODEL = "gemini-3.8-flash"

IMAGE_MODEL = "gemini-nano-banana-2.1"

VIDEO_MODEL = "veo-3.1-generate-preview"

MAX_UPLOAD_MB = 20

LANGUAGES = {
    "Türkçe": "Turkish",
    "English": "English",
    "Français": "French",
    "Deutsch": "German",
    "Español": "Spanish",
    "Italiano": "Italian",
    "日本語": "Japanese",
}


# =====================================================
# 3. API CLIENT
# =====================================================

@st.cache_resource
def get_client(api_key):
    return genai.Client(api_key=api_key)


api_key = st.secrets.get("GEMINI_API_KEY", "")

client = get_client(api_key) if api_key else None


# =====================================================
# 4. VISUAL DESIGN
# =====================================================

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(
                circle at top,
                #282044 0%,
                #131222 45%,
                #090914 100%
            );
        color: #f4efff;
    }

    h1, h2, h3, p, label {
        color: #f4efff;
    }

    [data-testid="stSidebar"] {
        background: #111020;
        border-right: 1px solid #3b2b59;
    }

    .lidya-title {
        font-size: 54px;
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
        color: #cbbce9;
        font-size: 16px;
        margin-bottom: 20px;
    }

    .orb {
        width: 115px;
        height: 115px;
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
            0 0 30px #b77cff,
            0 0 65px #8255ff;

        animation: float 3s ease-in-out infinite;
    }

    @keyframes float {
        0%, 100% {
            transform: translateY(0);
        }

        50% {
            transform: translateY(-12px);
        }
    }

    [data-testid="stChatMessage"] {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(200,170,255,0.17);
        border-radius: 15px;
    }

    .stButton button {
        border-radius: 12px;
        border: 1px solid #a984ff;
        color: white;
    }

    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# 5. MODULE DEFINITIONS
# =====================================================

MODULES = {
    "💜 Lidya": (
        "General assistant",
        "Help with everyday questions, research, "
        "creative work, reasoning and programming."
    ),

    "📁 File Laboratory": (
        "File analysis",
        "Analyze uploaded images, PDFs, videos and "
        "other supported media."
    ),

    "🩺 Medical & Anatomy": (
        "Medical education",
        "Explain anatomy, medical illustrations, "
        "labels and educational medical concepts. "
        "Never invent an anatomical structure or diagnosis."
    ),

    "⚖️ Legal Research": (
        "Legal information",
        "Explain legal concepts, summarize documents "
        "and identify questions to discuss with a qualified lawyer. "
        "Ask for the relevant country or jurisdiction."
    ),

    "🌍 Language Teacher": (
        "Language learning",
        "Teach vocabulary, grammar, pronunciation, "
        "conversation and translation."
    ),

    "💻 Software Engineering": (
        "Programming",
        "Explain code, debug errors, design software "
        "and discuss secure development."
    ),

    "🔬 Science & Research": (
        "Science",
        "Explain scientific concepts and help organize research."
    ),

    "📐 Mathematics": (
        "Mathematics",
        "Explain mathematical concepts and solve problems."
    ),

    "⚙️ Engineering": (
        "Engineering",
        "Explain engineering principles and help with calculations."
    ),

    "📚 Education": (
        "Education",
        "Create explanations, study guides and learning activities."
    ),

    "📊 Business & Economics": (
        "Business",
        "Explain business concepts, economics and data."
    ),

    "✍️ Writing & Creativity": (
        "Writing",
        "Help with original writing, editing and brainstorming."
    ),

    "📈 Data Analysis": (
        "Data",
        "Analyze supported datasets and explain results."
    ),

    "🔐 Cybersecurity": (
        "Cybersecurity",
        "Focus on defensive security, secure coding "
        "and responsible vulnerability remediation."
    ),

    "🏠 Smart Devices": (
        "Device safety",
        "Help plan safe smart-home integrations. "
        "This version does not directly control devices."
    ),
}


# =====================================================
# 6. SYSTEM INSTRUCTIONS
# =====================================================

def get_system_instruction(module, language):

    module_description = MODULES[module][1]

    shared_rules = """
You are Lidya AI, a thoughtful and helpful AI assistant.

Be accurate, explain your reasoning clearly, and be honest
about uncertainty.

Do not claim to have performed actions that you have not performed.

Protect privacy. Do not request passwords, API keys,
or unnecessary sensitive information.

For medical topics, provide educational information rather
than a personal diagnosis or treatment decision. Encourage
consultation with qualified healthcare professionals.

For legal topics, provide general legal information rather
than claiming to be a user's lawyer. Laws vary by jurisdiction.

For medical illustrations, distinguish what is visibly present
from what you infer. Mention uncertainty when structures or
labels cannot be identified confidently.

For smart devices, never perform or suggest an action that
could create a physical hazard. This application does not
have direct device-control permissions.
"""

    return (
        shared_rules
        + "\n\nCurrent workspace: "
        + module
        + "\nWorkspace purpose: "
        + module_description
        + "\n\nRespond in "
        + language
        + " unless the user requests another language."
    )


# =====================================================
# 7. FILE HELPERS
# =====================================================

def file_to_content(uploaded_file):

    file_bytes = uploaded_file.getvalue()

    mime_type = (
        uploaded_file.type
        or "application/octet-stream"
    )

    filename = uploaded_file.name.lower()

    if len(file_bytes) > MAX_UPLOAD_MB * 1024 * 1024:
        raise ValueError(
            f"File exceeds the {MAX_UPLOAD_MB} MB limit."
        )

    # Images can be passed as base64 data.
    if mime_type.startswith("image/"):

        return {
            "type": "image",
            "data": base64.b64encode(
                file_bytes
            ).decode("utf-8"),
            "mime_type": mime_type,
        }

    # Audio can be passed as audio data.
    if mime_type.startswith("audio/"):

        return {
            "type": "audio",
            "data": base64.b64encode(
                file_bytes
            ).decode("utf-8"),
            "mime_type": mime_type,
        }

    # For PDF and video, upload the file first.
    if (
        mime_type == "application/pdf"
        or mime_type.startswith("video/")
    ):

        suffix = os.path.splitext(filename)[1]

        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix,
            ) as temp_file:

                temp_file.write(file_bytes)
                temp_path = temp_file.name

            uploaded = client.files.upload(
                file=temp_path
            )

            # Wait for processing if the service reports
            # that the file is not ready yet.
            state = getattr(uploaded, "state", None)

            for _ in range(30):

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

                uploaded = client.files.get(
                    name=uploaded.name
                )

                state = getattr(uploaded, "state", None)

            kind = (
                "document"
                if mime_type == "application/pdf"
                else "video"
            )

            return {
                "type": kind,
                "uri": uploaded.uri,
                "mime_type": mime_type,
            }

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    raise ValueError(
        "Unsupported file type. Try an image, PDF, "
        "video or supported audio file."
    )


# =====================================================
# 8. GEMINI CHAT
# =====================================================

def ask_lidya(prompt, module, language, uploaded_file=None):

    if client is None:
        return (
            "GEMINI_API_KEY is missing. "
            "Add it to Streamlit Cloud → Settings → Secrets."
        )

    system_instruction = get_system_instruction(
        module,
        LANGUAGES[language],
    )

    content = [
        {
            "type": "text",
            "text": prompt,
        }
    ]

    if uploaded_file is not None:
        content.append(
            file_to_content(uploaded_file)
        )

    interaction = client.interactions.create(
        model=CHAT_MODEL,
        input=content,
        system_instruction=system_instruction,
    )

    return (
        getattr(interaction, "output_text", None)
        or "The model did not return a text response."
    )


# =====================================================
# 9. IMAGE GENERATION
# =====================================================

def generate_image(prompt):

    if client is None:
        raise RuntimeError(
            "Configure GEMINI_API_KEY first."
        )

    result = client.interactions.create(
        model=IMAGE_MODEL,
        input=prompt,
    )

    image_result = getattr(
        result,
        "output_image",
        None,
    )

    if image_result is None or not image_result.data:
        raise RuntimeError(
            "No image was returned. Check model access "
            "and image-generation availability."
        )

    return base64.b64decode(image_result.data)


# =====================================================
# 10. VIDEO GENERATION
# =====================================================

def generate_video(prompt):

    if client is None:
        raise RuntimeError(
            "Configure GEMINI_API_KEY first."
        )

    operation = client.models.generate_videos(
        model=VIDEO_MODEL,
        prompt=prompt,
    )

    progress = st.progress(0)
    status = st.empty()

    for attempt in range(60):

        if operation.done:
            break

        status.info(
            "Video generation is in progress. "
            "This can take several minutes."
        )

        time.sleep(10)

        operation = client.operations.get(operation)

        progress.progress(
            min(95, int((attempt + 1) / 60 * 95))
        )

    if not operation.done:
        raise TimeoutError(
            "Video generation is taking longer than expected. "
            "Check the generation job before retrying."
        )

    progress.progress(100)

    response = getattr(operation, "response", None)

    if response is None:
        raise RuntimeError(
            "The video service did not return a result."
        )

    generated_videos = getattr(
        response,
        "generated_videos",
        [],
    )

    if not generated_videos:
        raise RuntimeError(
            "No video was returned. Check your model access."
        )

    video_file = generated_videos[0].video

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp4",
    ) as temp_file:

        temp_path = temp_file.name

    try:
        client.files.download(
            file=video_file,
            download_path=temp_path,
        )

        with open(temp_path, "rb") as file:
            return file.read()

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# =====================================================
# 11. SIDEBAR
# =====================================================

with st.sidebar:

    st.markdown("## 💜 Lidya AI")

    st.caption("Your personal intelligent workspace")

    selected_module = st.radio(
        "WORKSPACES",
        list(MODULES.keys()),
        index=0,
    )

    st.divider()

    selected_language = st.selectbox(
        "🌍 Interface / response language",
        list(LANGUAGES.keys()),
        index=0,
    )

    st.divider()

    st.markdown("### 🎙️ Voice")

    voice_output = st.checkbox(
        "Read the latest answer aloud",
        value=False,
    )

    st.caption(
        "Browser speech synthesis is available. "
        "Full real-time Live API conversation is not "
        "implemented in this starter version."
    )

    st.divider()

    if st.button("🗑️ Clear chat", use_container_width=True):

        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.caption("Built with Python and Streamlit")


# =====================================================
# 12. MAIN HEADER
# =====================================================

st.markdown(
    '<div class="lidya-title">LIDYA AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="lidya-subtitle">'
    'Think. Learn. Create. Discover.'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="orb"></div>',
    unsafe_allow_html=True,
)

st.subheader(selected_module)

st.caption(MODULES[selected_module][1])


# =====================================================
# 13. SESSION STATE
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "generated_image" not in st.session_state:
    st.session_state.generated_image = None

if "generated_video" not in st.session_state:
    st.session_state.generated_video = None


# =====================================================
# 14. IMAGE / PDF / VIDEO ANALYSIS
# =====================================================

uploaded_file = None

if selected_module == "📁 File Laboratory":

    st.markdown("### 📂 Upload a file")

    uploaded_file = st.file_uploader(
        "Choose an image, PDF, video or supported audio file",
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

        st.success(
            f"Selected: {uploaded_file.name}"
        )

        if uploaded_file.type.startswith("image/"):
            st.image(
                uploaded_file,
                caption="Uploaded image",
                use_container_width=True,
            )

        if uploaded_file.type.startswith("video/"):
            st.video(uploaded_file)


# =====================================================
# 15. MEDICAL ILLUSTRATION WORKSPACE
# =====================================================

if selected_module == "🩺 Medical & Anatomy":

    st.info(
        "Educational workspace for anatomy and medical "
        "illustrations. Avoid uploading patient-identifiable "
        "records or other people's private medical information."
    )

    medical_file = st.file_uploader(
        "Upload your anatomical illustration",
        type=["png", "jpg", "jpeg", "webp", "pdf"],
        key="medical_file",
    )

    if medical_file:

        if medical_file.type.startswith("image/"):
            st.image(
                medical_file,
                caption="Your illustration",
                use_container_width=True,
            )

        st.caption(
            "Describe the task in the chat below, for example: "
            "'Explain the visible structures and identify "
            "which labels need verification.'"
        )

        uploaded_file = medical_file


# =====================================================
# 16. IMAGE GENERATION WORKSPACE
# =====================================================

if selected_module == "🎨 Image Studio":

    st.markdown("### 🎨 Create an image")

    image_prompt = st.text_area(
        "Describe the image you want to create",
        placeholder=(
            "Example: An educational illustration of the human "
            "heart, with clearly separated chambers, a neutral "
            "background and readable labels."
        ),
        key="image_prompt",
    )

    if st.button("✨ Generate image"):

        if image_prompt.strip():

            with st.spinner("Creating your image..."):

                try:
                    image_bytes = generate_image(
                        image_prompt.strip()
                    )

                    st.session_state.generated_image = image_bytes

                except Exception as error:
                    st.error(
                        f"Image generation failed: {error}"
                    )

        else:
            st.warning("Enter an image description first.")

    if st.session_state.generated_image:

        st.image(
            st.session_state.generated_image,
            caption="Generated by Lidya AI",
            use_container_width=True,
        )

        st.download_button(
            "⬇️ Download image",
            data=st.session_state.generated_image,
            file_name="lidya_generated_image.png",
            mime="image/png",
        )


# =====================================================
# 17. VIDEO GENERATION WORKSPACE
# =====================================================

if selected_module == "🎬 Video Studio":

    st.markdown("### 🎬 Create a short video")

    st.warning(
        "Video generation may require separate model access "
        "and can incur additional charges."
    )

    video_prompt = st.text_area(
        "Describe the video",
        placeholder=(
            "Example: A short, clean 3D animation explaining "
            "how the planets orbit the Sun."
        ),
        key="video_prompt",
    )

    if st.button("🎞️ Generate video"):

        if video_prompt.strip():

            try:
                with st.spinner(
                    "Generating the video. Please wait..."
                ):

                    video_bytes = generate_video(
                        video_prompt.strip()
                    )

                    st.session_state.generated_video = video_bytes

            except Exception as error:
                st.error(
                    f"Video generation failed: {error}"
                )

        else:
            st.warning("Enter a video description first.")

    if st.session_state.generated_video:

        st.video(
            st.session_state.generated_video
        )

        st.download_button(
            "⬇️ Download video",
            data=st.session_state.generated_video,
            file_name="lidya_generated_video.mp4",
            mime="video/mp4",
        )


# =====================================================
# 18. CHAT HISTORY
# =====================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"],
        avatar="💜" if message["role"] == "assistant" else "🧑‍💻",
    ):

        st.markdown(message["content"])


# =====================================================
# 19. CHAT INPUT
# =====================================================

if selected_module not in (
    "🎨 Image Studio",
    "🎬 Video Studio",
):

    prompt = st.chat_input(
        "Ask Lidya anything..."
    )

    if prompt:

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

            with st.spinner(
                "Lidya is thinking..."
            ):

                try:

                    # Include a bounded amount of recent text history.
                    history = st.session_state.messages[-10:]

                    history_text = "\n\n".join(
                        (
                            "User: "
                            if item["role"] == "user"
                            else "Lidya: "
                        )
                        + item["content"]
                        for item in history
                    )

                    answer = ask_lidya(
                        prompt=history_text,
                        module=selected_module,
                        language=selected_language,
                        uploaded_file=uploaded_file,
                    )

                except Exception as error:

                    answer = (
                        "I couldn't complete that request.\n\n"
                        f"Technical details: {error}"
                    )

                st.markdown(answer)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        st.rerun()


# =====================================================
# 20. TEXT-TO-SPEECH
# =====================================================

if (
    voice_output
    and st.session_state.messages
    and st.session_state.messages[-1]["role"] == "assistant"
):

    latest_answer = st.session_state.messages[-1]["content"]

    speech_text = json.dumps(
        latest_answer,
        ensure_ascii=False,
    )

    speech_locale = {
        "Türkçe": "tr-TR",
        "English": "en-US",
        "Français": "fr-FR",
        "Deutsch": "de-DE",
        "Español": "es-ES",
        "Italiano": "it-IT",
        "日本語": "ja-JP",
    }[selected_language]

    components.html(
        f"""
        <script>
        const text = {speech_text};
        const lang = "{speech_locale}";

        if ("speechSynthesis" in window) {{
            window.speechSynthesis.cancel();

            const utterance =
                new SpeechSynthesisUtterance(text);

            utterance.lang = lang;
            utterance.rate = 1.0;
            utterance.pitch = 1.0;

            window.speechSynthesis.speak(utterance);
        }}
        </script>
        """,
        height=0,
    )


# =====================================================
# 21. FOOTER
# =====================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#b9a9dc;
        padding:35px 0 10px 0;
        font-size:13px;
    ">
        💜 Lidya AI — Built with curiosity and Python
    </div>
    """,
    unsafe_allow_html=True,
    )

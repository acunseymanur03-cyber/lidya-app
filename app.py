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

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None


# =========================================================
# 1. UYGULAMA AYARLARI
# =========================================================

st.set_page_config(
    page_title="Lidya AI",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL_NAME = "openai/gpt-oss-20b"
VISION_MODEL = "@cf/meta/llama-3.2-11b-vision-instruct"
IMAGE_MODEL = "@cf/black-forest-labs/flux-1-schnell"
TZ = ZoneInfo("Europe/Istanbul")


def get_secret(name, default=""):
    try:
        value = st.secrets.get(name, default)
        if value:
            return value
    except Exception:
        pass

    return os.getenv(name, default)


GROQ_API_KEY = get_secret("GROQ_API_KEY")
CF_ACCOUNT_ID = get_secret("CLOUDFLARE_ACCOUNT_ID")
CF_API_TOKEN = get_secret("CLOUDFLARE_API_TOKEN")


# =========================================================
# 2. TASARIM
# =========================================================

st.markdown("""
<style>
.stApp {
    background: radial-gradient(
        ellipse at top,
        #25163e 0%,
        #100c1c 52%
    );
    color: #f6f1ff;
}

section[data-testid="stSidebar"] {
    background: #120d20;
    border-right: 1px solid rgba(190,160,255,.19);
}

h1, h2, h3 {
    color: #f6f0ff !important;
}

.lidya-hero {
    padding: 34px 20px;
    border: 1px solid rgba(190,160,255,.2);
    border-radius: 24px;
    background: linear-gradient(
        135deg,
        rgba(124,58,237,.2),
        rgba(30,20,48,.75)
    );
    text-align: center;
    margin-bottom: 22px;
}

.lidya-title {
    font-size: clamp(32px, 5vw, 52px);
    font-weight: 800;
    letter-spacing: -1.5px;
}

.lidya-subtitle {
    color: #d7c9f8;
    font-size: 17px;
}

.university-card {
    border: 1px solid rgba(190,160,255,.2);
    background: rgba(28,21,47,.8);
    border-radius: 16px;
    padding: 16px;
    margin: 8px 0;
}

.stButton > button {
    border-radius: 11px;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# 3. DİLLER
# =========================================================

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
        "home": "Ana Sayfa",
        "chat": "Lidya ile Sohbet",
        "research": "Araştırma Merkezi",
        "file": "Dosya Laboratuvarı",
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
        "image": "Görsel Atölyesi",
        "video": "Video Atölyesi",
        "sim": "Simülasyon Laboratuvarı",
        "history": "Tarih",
        "universities": "Üniversite Keşfi",
        "karaoke": "Ses ve Karaoke",
        "memory": "Lidya Hafızası",
        "settings": "Ayarlar",
        "welcome": "Düşün. Öğren. Üret. Keşfet.",
        "message": "Mesajını yaz...",
        "clear": "Sohbeti temizle",
        "workspaces": "Çalışma alanları",
    },
    "en": {
        "home": "Home",
        "chat": "Chat with Lidya",
        "research": "Research Center",
        "file": "File Lab",
        "medical": "Medicine & Anatomy",
        "legal": "Legal Research",
        "language": "Language Teacher",
        "coding": "Software Engineering",
        "science": "Science & Research",
        "math": "Mathematics",
        "engineering": "Engineering",
        "education": "Education",
        "business": "Business & Economics",
        "writing": "Writing & Creativity",
        "data": "Data Analysis",
        "cyber": "Cybersecurity",
        "devices": "Smart Devices",
        "image": "Image Studio",
        "video": "Video Studio",
        "sim": "Simulation Lab",
        "history": "History",
        "universities": "University Explorer",
        "karaoke": "Audio & Karaoke",
        "memory": "Lidya Memory",
        "settings": "Settings",
        "welcome": "Think. Learn. Create. Explore.",
        "message": "Write your message...",
        "clear": "Clear chat",
        "workspaces": "Workspaces",
    },
}

# Diğer dillerdeki menüler de anlaşılır kalır.
# Henüz bütün uzmanlık içerikleri dokuz dilin tamamına çevrilmiş değildir.
for language_code in ("fr", "de", "es", "it", "ja", "ar", "zh"):
    UI[language_code] = dict(UI["en"])

UI["fr"].update({
    "home": "Accueil",
    "chat": "Discuter avec Lidya",
    "research": "Centre de recherche",
    "math": "Mathématiques",
    "history": "Histoire",
})
UI["de"].update({
    "home": "Startseite",
    "chat": "Mit Lidya chatten",
    "research": "Forschungszentrum",
    "math": "Mathematik",
    "history": "Geschichte",
})
UI["es"].update({
    "home": "Inicio",
    "chat": "Hablar con Lidya",
    "research": "Centro de investigación",
    "math": "Matemáticas",
    "history": "Historia",
})
UI["it"].update({
    "home": "Home",
    "chat": "Chatta con Lidya",
    "research": "Centro di ricerca",
    "math": "Matematica",
    "history": "Storia",
})
UI["ja"].update({
    "home": "ホーム",
    "chat": "Lidyaとチャット",
    "research": "リサーチセンター",
    "math": "数学",
    "history": "歴史",
})
UI["ar"].update({
    "home": "الرئيسية",
    "chat": "الدردشة مع ليديا",
    "research": "مركز البحث",
    "math": "الرياضيات",
    "history": "التاريخ",
})
UI["zh"].update({
    "home": "主页",
    "chat": "与 Lidya 聊天",
    "research": "研究中心",
    "math": "数学",
    "history": "历史",
})


# =========================================================
# 4. MODÜLLER
# =========================================================

MODULES = [
    "home",
    "chat",
    "research",
    "file",
    "medical",
    "legal",
    "language",
    "coding",
    "science",
    "math",
    "engineering",
    "education",
    "business",
    "writing",
    "data",
    "cyber",
    "devices",
    "image",
    "video",
    "sim",
    "history",
    "universities",
    "karaoke",
    "memory",
    "settings",
]

SPECIALISTS = {
    "chat": (
        "Genel amaçlı, doğru, yardımsever ve anlaşılır bir yapay zekâ "
        "asistanısın."
    ),
    "medical": (
        "Tıp ve anatomi eğitim asistanısın. Anatomik yapıları ve fizyolojiyi "
        "açıkla. Kesin tanı koyma; profesyonel sağlık hizmetinin yerini "
        "aldığını iddia etme."
    ),
    "legal": (
        "Hukuk araştırma asistanısın. Ülke ve tarih farklılıklarını belirt. "
        "Genel bilgi sun; kişiye özel avukatlık hizmeti verdiğini iddia etme."
    ),
    "language": (
        "Dil öğretmenisin. Kelime, dil bilgisi, telaffuz ve alıştırmalar "
        "konusunda yardımcı ol. Hataları nazikçe düzelt."
    ),
    "coding": (
        "Yazılım asistanısın. Çalışan, güvenli ve açıklamalı kod üret. "
        "Gerekli bağımlılıkları belirt."
    ),
    "science": (
        "Bilimsel araştırma asistanısın. Kanıtları, varsayımları ve "
        "belirsizlikleri birbirinden ayır."
    ),
    "math": (
        "Matematik öğretmenisin. Problemleri adım adım çöz ve kullanılan "
        "formülleri açıkla."
    ),
    "engineering": (
        "Mühendislik asistanısın. Birimleri, varsayımları ve güvenlik "
        "sınırlarını belirt."
    ),
    "education": (
        "Eğitim asistanısın. Konuları seviyeye uygun biçimde öğret, örnekler "
        "ve pratik sorular sun."
    ),
    "business": (
        "İşletme ve ekonomi asistanısın. Hesaplamaları, varsayımları ve "
        "belirsizlikleri açıkla."
    ),
    "writing": (
        "Yazma ve yaratıcılık asistanısın. Özgün metinler oluştur ve "
        "kullanıcının istediği tona uy."
    ),
    "data": (
        "Veri analizi asistanısın. Verilerin ne gösterdiğini ve hangi "
        "sonuçların çıkarılamayacağını açıkla."
    ),
    "cyber": (
        "Siber güvenlik asistanısın. Savunma, güvenlik eğitimi ve izinli "
        "testlere odaklan."
    ),
    "devices": (
        "Akıllı cihazlar ve IoT asistanısın. Güvenli cihaz tasarımı ve "
        "otomasyon konusunda yardımcı ol."
    ),
    "history": (
        "Tarih öğretmenisin. Olayları kronoloji, nedenler ve sonuçlarla "
        "açıkla. Tartışmalı yorumları kesin gerçek gibi sunma."
    ),
}


# =========================================================
# 5. ÜNİVERSİTELER
# =========================================================

UNIVERSITIES = [
    (
        "Harvard University",
        "harvard.edu",
        "https://www.harvard.edu/",
        "https://college.harvard.edu/admissions",
    ),
    (
        "University of Oxford",
        "ox.ac.uk",
        "https://www.ox.ac.uk/",
        "https://www.ox.ac.uk/admissions/undergraduate",
    ),
    (
        "University of Cambridge",
        "cam.ac.uk",
        "https://www.cam.ac.uk/",
        "https://www.undergraduate.study.cam.ac.uk/",
    ),
    (
        "Massachusetts Institute of Technology",
        "mit.edu",
        "https://www.mit.edu/",
        "https://mitadmissions.org/",
    ),
    (
        "Yale University",
        "yale.edu",
        "https://www.yale.edu/",
        "https://admissions.yale.edu/",
    ),
    (
        "Columbia University",
        "columbia.edu",
        "https://www.columbia.edu/",
        "https://undergrad.admissions.columbia.edu/",
    ),
    (
        "Princeton University",
        "princeton.edu",
        "https://www.princeton.edu/",
        "https://admission.princeton.edu/",
    ),
    (
        "Stanford University",
        "stanford.edu",
        "https://www.stanford.edu/",
        "https://admission.stanford.edu/",
    ),
]


# =========================================================
# 6. OTURUM VERİLERİ
# =========================================================

if "language" not in st.session_state:
    st.session_state.language = "Türkçe"

if "module" not in st.session_state:
    st.session_state.module = "home"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "memory_items" not in st.session_state:
    st.session_state.memory_items = []

if "last_file_text" not in st.session_state:
    st.session_state.last_file_text = ""


def now_text():
    return datetime.now(TZ).strftime("%d.%m.%Y %H:%M:%S")


def label(key):
    code = LANGUAGES.get(st.session_state.language, "tr")
    return UI.get(code, UI["en"]).get(key, UI["en"].get(key, key))


def groq_client():
    if not GROQ_API_KEY or Groq is None:
        return None
    return Groq(api_key=GROQ_API_KEY)


# =========================================================
# 7. DOSYA OKUMA
# =========================================================

def read_file(upload):
    if upload is None:
        return ""

    filename = upload.name.lower()
    content = upload.getvalue()

    try:
        if filename.endswith(".pdf"):
            if PdfReader is None:
                return "PDF desteği için pypdf paketini kur."

            pdf = PdfReader(io.BytesIO(content))
            return "\n".join(
                page.extract_text() or ""
                for page in pdf.pages[:60]
            )[:25000]

        if filename.endswith(".docx"):
            if Document is None:
                return "Word desteği için python-docx paketini kur."

            document = Document(io.BytesIO(content))
            return "\n".join(
                paragraph.text for paragraph in document.paragraphs
            )[:25000]

        if filename.endswith((
            ".txt", ".md", ".csv", ".json", ".py", ".js",
            ".html", ".css", ".xml", ".yaml", ".yml"
        )):
            return content.decode(
                "utf-8",
                errors="replace",
            )[:25000]

        return ""

    except Exception as exc:
        return f"Dosya okunamadı: {exc}"


# =========================================================
# 8. GÖRSEL ANALİZİ
# =========================================================

def analyze_image(image_bytes, mime_type, question):
    if not CF_ACCOUNT_ID or not CF_API_TOKEN:
        return (
            "Görsel analizi için CLOUDFLARE_ACCOUNT_ID ve "
            "CLOUDFLARE_API_TOKEN ayarlanmalı."
        )

    encoded = base64.b64encode(image_bytes).decode("utf-8")

    endpoint = (
        "https://api.cloudflare.com/client/v4/accounts/"
        f"{CF_ACCOUNT_ID}/ai/run/{VISION_MODEL}"
    )

    # Cloudflare Vision modeline görseli base64 olarak gönder.
    payload = {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Lidya AI, a careful visual analysis assistant. "
                    "Describe what can be supported by the image. If labels "
                    "are unclear, say so. For medical images, provide "
                    "educational information, not a diagnosis."
                ),
            },
            {
                "role": "user",
                "content": question,
                "image": [encoded],
            },
        ],
        "max_tokens": 900,
    }

    try:
        response = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {CF_API_TOKEN}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=120,
        )

        if not response.ok:
            return (
                f"Cloudflare görsel analizi başarısız oldu "
                f"(HTTP {response.status_code}). "
                "Model erişimini ve API izinlerini kontrol et."
            )

        data = response.json()
        result = data.get("result", {})

        if isinstance(result, dict):
            return (
                result.get("response")
                or result.get("description")
                or json.dumps(result, ensure_ascii=False)
            )

        return str(result)

    except Exception as exc:
        return f"Görsel analizi başarısız: {exc}"


# =========================================================
# 9. GÖRSEL ÜRETİMİ
# =========================================================

def generate_image(prompt):
    if not CF_ACCOUNT_ID or not CF_API_TOKEN:
        st.error(
            "Görsel üretimi için Cloudflare API bilgileri gerekli."
        )
        return None

    endpoint = (
        "https://api.cloudflare.com/client/v4/accounts/"
        f"{CF_ACCOUNT_ID}/ai/run/{IMAGE_MODEL}"
    )

    try:
        response = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {CF_API_TOKEN}",
            },
            json={"prompt": prompt},
            timeout=120,
        )

        if not response.ok:
            st.error(
                f"Görsel üretimi başarısız oldu "
                f"(HTTP {response.status_code})."
            )
            return None

        data = response.json()
        result = data.get("result", {})
        image_value = (
            result.get("image")
            if isinstance(result, dict)
            else None
        )

        if image_value:
            return Image.open(
                io.BytesIO(base64.b64decode(image_value))
            )

        st.error("Görsel yanıtı beklenen biçimde alınamadı.")

    except Exception as exc:
        st.error(f"Görsel üretimi başarısız: {exc}")

    return None


# =========================================================
# 10. İNTERNET ARAMASI
# =========================================================

def web_search(query, max_results=6):
    if DDGS is None:
        return [], "ddgs paketi kurulu değil."

    try:
        with DDGS(timeout=15) as search_client:
            results = search_client.text(
                query,
                region="us-en",
                safesearch="moderate",
                backend="duckduckgo",
                max_results=max_results,
            )

        return list(results or []), None

    except Exception as exc:
        return [], str(exc)


def research_answer(query):
    results, error = web_search(query)

    if error:
        return (
            "İnternet araması başarısız oldu. Ağ erişimini ve arama "
            "hizmetinin kullanılabilirliğini kontrol et.\n\n"
            f"Ayrıntı: {error}"
        ), []

    if not results:
        return (
            "Aramada sonuç bulunamadı. Konuyu farklı kelimelerle dene."
        ), []

    source_text = []

    for index, item in enumerate(results, 1):
        source_text.append(
            f"[{index}] {item.get('title', 'Başlıksız')}\n"
            f"URL: {item.get('href', '')}\n"
            f"Özet: {item.get('body', '')}"
        )

    combined = "\n\n".join(source_text)
    client = groq_client()

    if client is None:
        answer = (
            "Arama sonuçları bulundu. Ancak Groq API anahtarı olmadığı "
            "için sonuçların yapay zekâ tarafından özetlenmesi yapılamıyor."
        )

    else:
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Sen Lidya AI araştırma asistanısın. Yalnızca "
                            "verilen arama sonuçlarına dayanarak dikkatli "
                            "bir özet yaz. Kaynaklarda olmayan bilgileri "
                            "uydurma. Önemli iddiaları [1], [2] gibi "
                            "kaynak numaralarıyla ilişkilendir. "
                            "Kullanıcının seçtiği dilde yanıt ver."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Soru: {query}\n\n"
                            f"Arama sonuçları:\n{combined}"
                        ),
                    },
                ],
                temperature=0.2,
                max_tokens=1600,
            )

            answer = (
                response.choices[0].message.content
                or "Özet oluşturulamadı."
            )

        except Exception as exc:
            answer = (
                "Arama sonuçları bulundu fakat özet oluşturulamadı: "
                f"{exc}"
            )

    return answer, results


# =========================================================
# 11. LIDYA SOHBET MOTORU
# =========================================================

def ask_lidya(prompt, module, history=None, file_context=""):
    client = groq_client()

    if client is None:
        return (
            "Groq bağlantısı kurulamıyor. Streamlit Cloud → "
            "App settings → Secrets bölümünde GROQ_API_KEY değerini "
            "kontrol et."
        )

    system = (
        "Sen Lidya AI adlı eğitim ve üretkenlik asistanısın. "
        "Lidya AI projesini Şeymanur Acun geliştirmiştir. "
        "Temel yapay zekâ modelinin geliştiricisiyle proje geliştiricisini "
        "birbirine karıştırma. Kullanıcının seçtiği dilde yanıt ver. "
        "İnternette arama yaptığını veya bir dosyayı analiz ettiğini "
        "yalnızca gerçekten yaptıysan söyle. Açık, doğru ve yararlı ol.\n\n"
        + SPECIALISTS.get(module, SPECIALISTS["chat"])
    )

    if file_context:
        prompt = (
            "Kullanıcının dosyasından çıkarılan metin:\n"
            f"{file_context[:18000]}\n\n"
            f"Kullanıcının isteği:\n{prompt}"
        )

    messages = [
        {"role": "system", "content": system}
    ]

    for item in (history or [])[-12:]:
        if item.get("role") in ("user", "assistant"):
            messages.append({
                "role": item["role"],
                "content": item.get("content", "")[:5000],
            })

    messages.append({
        "role": "user",
        "content": prompt,
    })

    try:
        result = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.5,
            max_tokens=1800,
        )

        return (
            result.choices[0].message.content
            or "Yanıt üretilemedi."
        )

    except Exception as exc:
        return f"Yanıt alınırken hata oluştu: {exc}"


# =========================================================
# 12. ORTAK SİMÜLASYONLAR
# =========================================================

def simulation_panel(prefix="sim"):
    """Aynı simülasyonları farklı modüllerde de göstermek için kullanılır."""

    st.subheader("🧪 Etkileşimli Simülasyonlar")

    kind = st.selectbox(
        "Simülasyon türü",
        [
            "Matematik: Fonksiyon grafiği",
            "Fizik: Mermi hareketi",
            "Fizik: Dalga hareketi",
            "Uzay: Dairesel yörünge",
        ],
        key=f"{prefix}_kind",
    )

    if kind == "Matematik: Fonksiyon grafiği":
        function = st.selectbox(
            "Fonksiyon",
            ["x²", "sin(x)", "cos(x)", "x³ - 2x"],
            key=f"{prefix}_function",
        )

        x = np.linspace(-10, 10, 400)

        values = {
            "x²": x ** 2,
            "sin(x)": np.sin(x),
            "cos(x)": np.cos(x),
            "x³ - 2x": x ** 3 - 2 * x,
        }

        fig, ax = plt.subplots()
        ax.plot(x, values[function])
        ax.set_xlabel("x")
        ax.set_ylabel("f(x)")
        ax.grid(True)
        st.pyplot(fig)
        plt.close(fig)

    elif kind == "Fizik: Mermi hareketi":
        angle = np.radians(
            st.slider(
                "Atış açısı (derece)",
                10, 80, 45,
                key=f"{prefix}_angle",
            )
        )

        speed = st.slider(
            "Başlangıç hızı (m/s)",
            5, 100, 30,
            key=f"{prefix}_speed",
        )

        gravity = 9.81
        vx = speed * np.cos(angle)
        vy = speed * np.sin(angle)

        duration = 2 * vy / gravity
        t = np.linspace(0, duration, 250)

        x = vx * t
        y = vy * t - 0.5 * gravity * t ** 2

        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_xlabel("Yatay uzaklık (m)")
        ax.set_ylabel("Yükseklik (m)")
        ax.grid(True)
        st.pyplot(fig)
        plt.close(fig)

        st.write(
            f"İdeal modelde hesaplanan menzil: **{x[-1]:.2f} m**"
        )
        st.caption(
            "Eğitim amaçlı modeldir; hava direnci ve rüzgâr hesaba katılmaz."
        )

    elif kind == "Fizik: Dalga hareketi":
        amplitude = st.slider(
            "Genlik",
            1, 10, 4,
            key=f"{prefix}_amplitude",
        )

        frequency = st.slider(
            "Frekans katsayısı",
            1, 10, 2,
            key=f"{prefix}_frequency",
        )

        x = np.linspace(0, 4 * np.pi, 400)
        y = amplitude * np.sin(frequency * x)

        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_xlabel("Konum")
        ax.set_ylabel("Genlik")
        ax.grid(True)
        st.pyplot(fig)
        plt.close(fig)

    else:
        radius = st.slider(
            "Yörünge yarıçapı",
            1, 10, 5,
            key=f"{prefix}_radius",
        )

        theta = np.linspace(0, 2 * np.pi, 360)

        fig, ax = plt.subplots()
        ax.plot(
            radius * np.cos(theta),
            radius * np.sin(theta),
        )
        ax.scatter([0], [0])
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.grid(True)
        st.pyplot(fig)
        plt.close(fig)

        st.caption(
            "Bu grafik basitleştirilmiş dairesel yörünge modelidir; "
            "tam bir uzay uçuşu simülasyonu değildir."
        )


# =========================================================
# 13. SOL MENÜ
# =========================================================

with st.sidebar:
    st.markdown("## 💜 Lidya AI")
    st.caption("Düşün. Öğren. Üret. Keşfet.")

    selected_language = st.selectbox(
        "🌐 Dil / Language",
        list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(
            st.session_state.language
        ),
    )

    st.session_state.language = selected_language

    st.markdown("---")

    st.session_state.module = st.radio(
        label("workspaces"),
        MODULES,
        index=MODULES.index(st.session_state.module),
        format_func=lambda key: (
            "🏠 " + label(key) if key == "home" else label(key)
        ),
    )

    st.markdown("---")
    st.caption("🕒 " + now_text() + " · Türkiye")

    if st.button(
        "🧹 " + label("clear"),
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.rerun()


module = st.session_state.module


# =========================================================
# 14. ANA SAYFA — SADE TASARIM
# =========================================================

if module == "home":
    st.markdown("""
    <div class="lidya-hero">
        <div class="lidya-title">💜 Lidya AI</div>
        <div class="lidya-subtitle">
            Düşün. Öğren. Üret. Keşfet.
        </div>
        <p>Built with curiosity and Python.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### " + label("welcome"))

    st.write(
        "Sohbet, araştırma, dosya analizi, bilim, matematik, "
        "üniversite keşfi ve diğer çalışma alanlarına sol menüden ulaş."
    )


# =========================================================
# 15. ARAŞTIRMA MERKEZİ
# =========================================================

elif module == "research":
    st.title("🔎 " + label("research"))

    query = st.text_area(
        "Ne araştırmak istiyorsun?",
        placeholder=(
            "Örneğin: Harvard lisans başvurusu için resmî sınav politikası"
        ),
        height=100,
    )

    if st.button("İnternette ara", type="primary"):
        if not query.strip():
            st.warning("Önce araştırma konusunu yaz.")

        else:
            with st.spinner("Arama yapılıyor ve sonuçlar özetleniyor..."):
                answer, results = research_answer(query)

            st.subheader("Araştırma özeti")
            st.markdown(answer)

            if results:
                st.subheader("Bulunan kaynaklar")

                for index, result in enumerate(results, 1):
                    title = result.get("title", "Başlıksız")
                    url = result.get("href", "")
                    body = result.get("body", "")

                    st.markdown(f"**[{index}] [{title}]({url})**")

                    if body:
                        st.write(body)


# =========================================================
# 16. ÜNİVERSİTE KEŞFİ
# =========================================================

elif module == "universities":
    st.title("🎓 " + label("universities"))

    st.write(
        "Üniversitelerin resmî sitelerini ve lisans kabul sayfalarını incele."
    )

    search = st.text_input("Üniversite ara")

    filtered = [
        university
        for university in UNIVERSITIES
        if search.lower() in university[0].lower()
    ]

    for start in range(0, len(filtered), 2):
        columns = st.columns(2)

        for column, university in zip(
            columns,
            filtered[start:start + 2],
        ):
            name, domain, site, admissions = university

            with column:
                st.markdown(
                    '<div class="university-card">',
                    unsafe_allow_html=True,
                )

                left, right = st.columns([1, 4])

                with left:
                    st.image(
                        "https://www.google.com/s2/favicons"
                        f"?domain={domain}&sz=128",
                        width=48,
                    )

                with right:
                    st.markdown(f"#### {name}")
                    st.markdown(f"[Resmî site]({site})")
                    st.markdown(
                        f"[Lisans kabul sayfası]({admissions})"
                    )

                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Üniversite araştırması")

    university_names = [
        university[0] for university in UNIVERSITIES
    ]

    selected_university = st.selectbox(
        "Üniversite",
        university_names,
    )

    topic = st.selectbox(
        "Araştırma konusu",
        [
            "Lisans kabul koşulları",
            "Maddi yardım ve burslar",
            "Uluslararası öğrenci başvuruları",
            "Başvuru tarihleri",
            "Bölümler ve programlar",
        ],
    )

    if st.button("Araştırmayı başlat", type="primary"):
        chosen = next(
            university
            for university in UNIVERSITIES
            if university[0] == selected_university
        )

        query = (
            f"site:{chosen[1]} {topic} undergraduate admissions"
        )

        with st.spinner("Arama yapılıyor..."):
            answer, results = research_answer(query)

        st.markdown(answer)

        for result in results:
            st.markdown(
                f"- [{result.get('title', 'Kaynak')}]"
                f"({result.get('href', '')})"
            )

    st.caption(
        "Sınav, burs ve son tarih bilgilerini üniversitenin kendi "
        "kabul sayfasından doğrula."
    )


# =========================================================
# 17. DOSYA LABORATUVARI
# =========================================================

elif module == "file":
    st.title("📁 " + label("file"))

    uploaded = st.file_uploader(
        "Dosya veya görsel yükle",
        type=[
            "pdf", "docx", "txt", "md", "csv", "json",
            "py", "js", "html", "css", "xml", "yaml", "yml",
            "png", "jpg", "jpeg", "webp",
        ],
        key="file_lab",
    )

    if uploaded:
        extension = uploaded.name.lower().rsplit(".", 1)[-1]

        if extension in ("png", "jpg", "jpeg", "webp"):
            st.image(
                uploaded,
                caption=uploaded.name,
                use_container_width=True,
            )

            question = st.text_area(
                "Görsel hakkında ne öğrenmek istiyorsun?",
                value="Bu görseli ayrıntılı olarak açıkla.",
            )

            if st.button("Görseli analiz et", type="primary"):
                mime = {
                    "png": "image/png",
                    "jpg": "image/jpeg",
                    "jpeg": "image/jpeg",
                    "webp": "image/webp",
                }[extension]

                with st.spinner("Görsel analiz ediliyor..."):
                    answer = analyze_image(
                        uploaded.getvalue(),
                        mime,
                        question,
                    )

                st.markdown(answer)

        else:
            content = read_file(uploaded)
            st.session_state.last_file_text = content

            with st.expander("Dosyadan çıkarılan metni gör"):
                st.text(content[:12000])

            task = st.text_area(
                "Dosyayla ilgili isteğin",
                placeholder=(
                    "Özetle, açıkla, ana fikirleri çıkar veya kodu incele..."
                ),
            )

            if st.button("Dosyayı analiz et", type="primary"):
                if not content.strip():
                    st.warning(
                        "Dosyadan okunabilir metin çıkarılamadı. "
                        "Taranmış PDF için OCR gerekebilir."
                    )

                elif not task.strip():
                    st.warning("Dosyayla ilgili isteğini yaz.")

                else:
                    with st.spinner("Dosya analiz ediliyor..."):
                        answer = ask_lidya(
                            task,
                            "chat",
                            [],
                            file_context=content,
                        )

                    st.markdown(answer)


# =========================================================
# 18. GÖRSEL ATÖLYESİ
# =========================================================

elif module == "image":
    st.title("🎨 " + label("image"))

    prompt = st.text_area(
        "Oluşturmak istediğin görseli tarif et",
        placeholder=(
            "Örneğin: İnsan hücresinin bilimsel eğitim illüstrasyonu"
        ),
        height=120,
    )

    if st.button("Görsel oluştur", type="primary"):
        if not prompt.strip():
            st.warning("Önce görsel açıklaması yaz.")

        else:
            with st.spinner("Görsel oluşturuluyor..."):
                generated = generate_image(prompt)

            if generated:
                st.image(
                    generated,
                    caption="Lidya AI görseli",
                )

                buffer = io.BytesIO()
                generated.save(buffer, format="PNG")

                st.download_button(
                    "PNG olarak indir",
                    buffer.getvalue(),
                    file_name="lidya_image.png",
                    mime="image/png",
                )


# =========================================================
# 19. VİDEO ATÖLYESİ
# =========================================================

elif module == "video":
    st.title("🎬 " + label("video"))

    st.info(
        "Bu araç bir görselden yakınlaşma animasyonu üretir. "
        "Metinden gerçek yapay zekâ videosu üretmez."
    )

    upload = st.file_uploader(
        "Görsel yükle",
        type=["png", "jpg", "jpeg", "webp"],
        key="video_image",
    )

    seconds = st.slider("Süre (saniye)", 2, 8, 4)

    if st.button("Animasyon oluştur"):
        if upload is None:
            st.warning("Önce bir görsel yükle.")

        else:
            try:
                import imageio.v2 as imageio

                original = Image.open(upload).convert("RGB")
                width, height = original.size
                frames = []

                for index in range(seconds * 8):
                    progress = index / max(
                        1,
                        seconds * 8 - 1,
                    )

                    scale = 1 + 0.12 * progress

                    resized = original.resize((
                        int(width * scale),
                        int(height * scale),
                    ))

                    left = (resized.width - width) // 2
                    top = (resized.height - height) // 2

                    frame = resized.crop((
                        left,
                        top,
                        left + width,
                        top + height,
                    ))

                    frames.append(np.array(frame))

                with tempfile.NamedTemporaryFile(
                    suffix=".mp4",
                    delete=False,
                ) as temporary:
                    path = temporary.name

                imageio.mimsave(
                    path,
                    frames,
                    fps=8,
                    codec="libx264",
                )

                with open(path, "rb") as video_file:
                    video_bytes = video_file.read()

                st.video(video_bytes)

                st.download_button(
                    "MP4 olarak indir",
                    video_bytes,
                    file_name="lidya_animation.mp4",
                    mime="video/mp4",
                )

                os.remove(path)

            except Exception as exc:
                st.error(f"Animasyon oluşturulamadı: {exc}")


# =========================================================
# 20. SİMÜLASYON LABORATUVARI
# =========================================================

elif module == "sim":
    st.title("🪐 " + label("sim"))
    simulation_panel("main_sim")


# =========================================================
# 21. SES VE KARAOKE
# =========================================================

elif module == "karaoke":
    st.title("🎤 " + label("karaoke"))

    st.write(
        "Ses dosyası yükle, kaydet, yazıya çevir veya metni sesli dinle."
    )

    audio = st.file_uploader(
        "Ses dosyası yükle",
        type=["wav", "mp3", "m4a", "ogg", "flac"],
        key="karaoke_audio",
    )

    if audio:
        st.audio(audio)

        if st.button("Ses dosyasını yazıya çevir"):
            client = groq_client()

            if client is None:
                st.error("GROQ_API_KEY ayarlanmamış.")

            else:
                try:
                    with st.spinner("Ses yazıya çevriliyor..."):
                        transcript = client.audio.transcriptions.create(
                            file=(audio.name, audio.getvalue()),
                            model="whisper-large-v3",
                            response_format="text",
                        )

                    st.text_area(
                        "Transkripsiyon",
                        str(transcript),
                        height=180,
                    )

                except Exception as exc:
                    st.error(f"Ses çevrilemedi: {exc}")

    st.subheader("Mikrofon kaydı")

    microphone = st.audio_input("Sesini kaydet")

    if microphone:
        st.audio(microphone)

        if st.button("Mikrofon kaydını yazıya çevir"):
            client = groq_client()

            if client is None:
                st.error("GROQ_API_KEY ayarlanmamış.")

            else:
                try:
                    with st.spinner("Kayıt yazıya çevriliyor..."):
                        transcript = client.audio.transcriptions.create(
                            file=(
                                "recording.wav",
                                microphone.getvalue(),
                            ),
                            model="whisper-large-v3",
                            response_format="text",
                        )

                    st.text_area(
                        "Kayıt metni",
                        str(transcript),
                        height=180,
                    )

                except Exception as exc:
                    st.error(f"Kayıt çevrilemedi: {exc}")

    st.subheader("Metni sesli dinle")

    speech_text = st.text_area(
        "Okunacak metin",
        key="speech_text",
    )

    if speech_text:
        encoded_text = json.dumps(
            speech_text,
            ensure_ascii=False,
        )

        st.components.v1.html(
            f"""
            <button onclick="speakText()">🔊 Sesli oku</button>
            <button onclick="stopText()">⏹ Durdur</button>

            <script>
            function speakText() {{
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(
                    {encoded_text}
                );
                window.speechSynthesis.speak(utterance);
            }}

            function stopText() {{
                window.speechSynthesis.cancel();
            }}
            </script>
            """,
            height=70,
        )


# =========================================================
# 22. OTURUM HAFIZASI
# =========================================================

elif module == "memory":
    st.title("🧠 " + label("memory"))

    st.warning(
        "Bu hafıza yalnızca mevcut oturum boyunca tutulur. "
        "Kalıcı hafıza henüz bu sürümde uygulanmamıştır."
    )

    item = st.text_input("Hatırlanacak bilgi")

    if st.button("Hafızaya ekle"):
        if item.strip():
            st.session_state.memory_items.append({
                "text": item.strip(),
                "time": now_text(),
            })
            st.success("Bilgi mevcut oturuma eklendi.")

    st.subheader("Kaydedilen bilgiler")

    if st.session_state.memory_items:
        for index, memory in enumerate(
            st.session_state.memory_items,
            1,
        ):
            st.write(
                f"{index}. {memory['text']} · {memory['time']}"
            )

    else:
        st.caption("Henüz bilgi eklenmedi.")

    if st.button("Hafızayı temizle"):
        st.session_state.memory_items = []
        st.success("Oturum hafızası temizlendi.")


# =========================================================
# 23. AYARLAR
# =========================================================

elif module == "settings":
    st.title("⚙️ " + label("settings"))

    st.write(
        "Groq API:",
        "Anahtar bulundu" if GROQ_API_KEY else "Anahtar eksik",
    )

    st.write(
        "Cloudflare API:",
        "Anahtarlar bulundu"
        if CF_ACCOUNT_ID and CF_API_TOKEN
        else "Cloudflare bilgileri eksik",
    )

    st.write(
        "Web araması:",
        "DDGS paketi yüklü"
        if DDGS is not None
        else "DDGS paketi eksik",
    )

    st.write("Seçili dil:", st.session_state.language)
    st.write("Türkiye saati:", now_text())

    st.caption(
        "API anahtarlarını kodun içine değil, "
        "Streamlit Cloud Secrets bölümüne ekle."
    )


# =========================================================
# 24. SOHBET VE UZMANLIK MODÜLLERİ
# =========================================================

elif module in SPECIALISTS:
    st.title("💜 " + label(module))
    st.caption("🕒 " + now_text() + " · Türkiye")

    attachment = st.file_uploader(
        "İsteğe bağlı dosya veya görsel ekle",
        type=[
            "pdf", "docx", "txt", "md", "csv", "json",
            "py", "js", "html", "css", "xml", "yaml", "yml",
            "png", "jpg", "jpeg", "webp",
        ],
        key=f"attachment_{module}",
    )

    file_context = ""
    image_bytes = None
    image_mime = None

    if attachment:
        extension = attachment.name.lower().rsplit(".", 1)[-1]

        if extension in ("png", "jpg", "jpeg", "webp"):
            image_bytes = attachment.getvalue()

            image_mime = {
                "png": "image/png",
                "jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "webp": "image/webp",
            }[extension]

            st.image(
                attachment,
                caption=attachment.name,
                use_container_width=True,
            )

        else:
            file_context = read_file(attachment)
            st.caption(f"Dosya eklendi: {attachment.name}")

    for message in st.session_state.messages:
        if message.get("module") == module:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                st.caption(message.get("time", ""))

    prompt = st.chat_input(label("message"))

    if prompt:
        prior = [
            message
            for message in st.session_state.messages
            if message.get("module") == module
        ]

        identity_question = any(
            phrase in prompt.lower()
            for phrase in (
                "seni kim yaptı",
                "seni kim geliştirdi",
                "seni kim tasarladı",
                "who created you",
                "who developed you",
                "who designed you",
            )
        )

        if identity_question:
            answer = (
                "Lidya AI projesini Şeymanur Acun geliştirdi. "
                "Lidya'nın kullandığı temel yapay zekâ modelleri ve "
                "diğer altyapı hizmetleri ise ilgili sağlayıcılar "
                "tarafından geliştirilmiştir."
            )

        elif image_bytes is not None:
            with st.spinner("Görsel analiz ediliyor..."):
                answer = analyze_image(
                    image_bytes,
                    image_mime,
                    prompt,
                )

        else:
            with st.spinner("Lidya düşünüyor..."):
                answer = ask_lidya(
                    prompt,
                    module,
                    prior,
                    file_context=file_context,
                )

        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "time": now_text(),
            "module": module,
        })

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "time": now_text(),
            "module": module,
        })

        st.rerun()


# =========================================================
# 25. DİĞER MODÜLLERDE ORTAK SİMÜLASYON PANELİ
# =========================================================

if module not in ("home", "sim", "settings", "memory"):
    with st.expander(
        "🧪 Etkileşimli Simülasyonlar",
        expanded=False,
    ):
        st.write(
            "Bulunduğun modülden ayrılmadan simülasyonları kullanabilirsin."
        )

        simulation_panel(f"shared_{module}")


# =========================================================
# 26. ALT BİLGİ
# =========================================================

st.markdown("---")
st.caption("💜 Lidya AI · Built with curiosity and Python.")

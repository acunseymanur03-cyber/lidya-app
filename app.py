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
# 1. TEMEL AYARLAR
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


def secret(name, default=""):
    try:
        value = st.secrets.get(name, default)
        if value:
            return value
    except Exception:
        pass
    return os.getenv(name, default)


GROQ_API_KEY = secret("GROQ_API_KEY")
CF_ACCOUNT_ID = secret("CLOUDFLARE_ACCOUNT_ID")
CF_API_TOKEN = secret("CLOUDFLARE_API_TOKEN")


# =========================================================
# 2. TASARIM
# =========================================================

st.markdown("""
<style>
.stApp {
    background: radial-gradient(ellipse at top, #25163e 0%, #100c1c 52%);
    color: #f6f1ff;
}
section[data-testid="stSidebar"] {
    background: #120d20;
    border-right: 1px solid rgba(190,160,255,.19);
}
h1, h2, h3 { color: #f6f0ff !important; }
.lidya-hero {
    padding: 34px 20px;
    border: 1px solid rgba(190,160,255,.2);
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(124,58,237,.2),
                rgba(30,20,48,.75));
    text-align: center;
    margin-bottom: 22px;
}
.lidya-title {
    font-size: clamp(32px, 5vw, 52px);
    font-weight: 800;
    letter-spacing: -1.5px;
}
.lidya-subtitle { color: #d7c9f8; font-size: 17px; }
.lidya-card, .university-card {
    border: 1px solid rgba(190,160,255,.2);
    background: rgba(28,21,47,.8);
    border-radius: 16px;
    padding: 16px;
    margin: 8px 0;
}
.small-muted { color: #b9abcf; font-size: 13px; }
.stButton > button { border-radius: 11px; }
</style>
""", unsafe_allow_html=True)


# =========================================================
# 3. DİLLER VE MODÜLLER
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
        "home": "Ana Sayfa", "chat": "Lidya ile Sohbet",
        "research": "Araştırma Merkezi", "file": "Dosya Laboratuvarı",
        "medical": "Tıp ve Anatomi", "legal": "Hukuk Araştırmaları",
        "language": "Dil Öğretmeni", "coding": "Yazılım Mühendisliği",
        "science": "Bilim ve Araştırma", "math": "Matematik",
        "engineering": "Mühendislik", "education": "Eğitim",
        "business": "İşletme ve Ekonomi", "writing": "Yazma ve Yaratıcılık",
        "data": "Veri Analizi", "cyber": "Siber Güvenlik",
        "devices": "Akıllı Cihazlar", "image": "Görsel Atölyesi",
        "video": "Video Atölyesi", "sim": "Simülasyon Laboratuvarı",
        "history": "Tarih", "universities": "Üniversite Keşfi",
        "karaoke": "Ses ve Karaoke", "memory": "Lidya Hafızası",
        "settings": "Ayarlar", "welcome": "Düşün. Öğren. Üret. Keşfet.",
        "message": "Mesajını yaz...", "clear": "Sohbeti temizle",
    },
    "en": {
        "home": "Home", "chat": "Chat with Lidya",
        "research": "Research Center", "file": "File Lab",
        "medical": "Medicine & Anatomy", "legal": "Legal Research",
        "language": "Language Teacher", "coding": "Software Engineering",
        "science": "Science & Research", "math": "Mathematics",
        "engineering": "Engineering", "education": "Education",
        "business": "Business & Economics", "writing": "Writing & Creativity",
        "data": "Data Analysis", "cyber": "Cybersecurity",
        "devices": "Smart Devices", "image": "Image Studio",
        "video": "Video Studio", "sim": "Simulation Lab",
        "history": "History", "universities": "University Explorer",
        "karaoke": "Audio & Karaoke", "memory": "Lidya Memory",
        "settings": "Settings", "welcome": "Think. Learn. Create. Explore.",
        "message": "Write your message...", "clear": "Clear chat",
    },
}

for lang in ("fr", "de", "es", "it", "ja", "ar", "zh"):
    UI[lang] = dict(UI["en"])

UI["fr"].update(home="Accueil", chat="Discuter avec Lidya",
    research="Centre de recherche", math="Mathématiques",
    history="Histoire", universities="Découvrir les universités")
UI["de"].update(home="Startseite", chat="Mit Lidya chatten",
    research="Forschungszentrum", math="Mathematik",
    history="Geschichte", universities="Universitäten entdecken")
UI["es"].update(home="Inicio", chat="Hablar con Lidya",
    research="Centro de investigación", math="Matemáticas",
    history="Historia", universities="Explorar universidades")
UI["it"].update(home="Home", chat="Chatta con Lidya",
    research="Centro di ricerca", math="Matematica",
    history="Storia", universities="Esplora università")
UI["ja"].update(home="ホーム", chat="Lidyaとチャット",
    research="リサーチセンター", math="数学",
    history="歴史", universities="大学を探す")
UI["ar"].update(home="الرئيسية", chat="الدردشة مع ليديا",
    research="مركز البحث", math="الرياضيات",
    history="التاريخ", universities="استكشاف الجامعات")
UI["zh"].update(home="主页", chat="与 Lidya 聊天",
    research="研究中心", math="数学",
    history="历史", universities="探索大学")

MODULES = [
    "home", "chat", "research", "file", "medical", "legal", "language",
    "coding", "science", "math", "engineering", "education", "business",
    "writing", "data", "cyber", "devices", "image", "video", "sim",
    "history", "universities", "karaoke", "memory", "settings",
]

SPECIALISTS = {
    "chat": "Genel amaçlı, doğru ve yardımsever bir yapay zekâ asistanısın.",
    "medical": (
        "Tıp ve anatomi eğitim asistanısın. Anatomik yapıları açıkla. "
        "Kesin tanı koyma; profesyonel sağlık hizmetinin yerini aldığını söyleme."
    ),
    "legal": (
        "Hukuk araştırma asistanısın. Ülke ve tarih farklılıklarını belirt. "
        "Genel bilgi sun; kişiye özel avukatlık hizmeti verdiğini iddia etme."
    ),
    "language": "Dil öğretmenisin. Örnekler, alıştırmalar ve nazik düzeltmeler sun.",
    "coding": "Yazılım asistanısın. Çalışan, güvenli ve açıklamalı kod üret.",
    "science": "Bilimsel araştırma asistanısın. Kanıtları ve belirsizlikleri ayır.",
    "math": "Matematik öğretmenisin. Çözümleri adım adım açıkla.",
    "engineering": "Mühendislik asistanısın. Birimleri ve varsayımları belirt.",
    "education": "Eğitim asistanısın. Konuları basitten karmaşığa öğret.",
    "business": "İşletme ve ekonomi asistanısın. Varsayımları açıkla.",
    "writing": "Yazma asistanısın. Özgün metinler yaz ve düzenle.",
    "data": "Veri analizi asistanısın. Sonuçları verinin sınırlarıyla birlikte açıkla.",
    "cyber": "Siber güvenlik asistanısın. Savunma ve izinli testlere odaklan.",
    "devices": "Akıllı cihazlar ve IoT asistanısın. Güvenli çözümler öner.",
    "history": (
        "Tarih öğretmenisin. Olayları kronoloji, nedenler ve sonuçlarla açıkla. "
        "Tartışmalı yorumları kesin gerçek gibi sunma."
    ),
}

UNIVERSITIES = [
    ("Harvard University", "harvard.edu",
     "https://www.harvard.edu/", "https://college.harvard.edu/admissions"),
    ("University of Oxford", "ox.ac.uk",
     "https://www.ox.ac.uk/", "https://www.ox.ac.uk/admissions/undergraduate"),
    ("University of Cambridge", "cam.ac.uk",
     "https://www.cam.ac.uk/", "https://www.undergraduate.study.cam.ac.uk/"),
    ("Massachusetts Institute of Technology", "mit.edu",
     "https://www.mit.edu/", "https://mitadmissions.org/"),
    ("Yale University", "yale.edu",
     "https://www.yale.edu/", "https://admissions.yale.edu/"),
    ("Columbia University", "columbia.edu",
     "https://www.columbia.edu/", "https://undergrad.admissions.columbia.edu/"),
    ("Princeton University", "princeton.edu",
     "https://www.princeton.edu/", "https://admission.princeton.edu/"),
    ("Stanford University", "stanford.edu",
     "https://www.stanford.edu/", "https://admission.stanford.edu/"),
]


# =========================================================
# 4. OTURUM
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
if "last_file_name" not in st.session_state:
    st.session_state.last_file_name = ""


def now_text():
    return datetime.now(TZ).strftime("%d.%m.%Y %H:%M:%S")


def label(key):
    lang = LANGUAGES.get(st.session_state.language, "tr")
    return UI.get(lang, UI["en"]).get(key, UI["en"].get(key, key))


def groq_client():
    if not GROQ_API_KEY or Groq is None:
        return None
    return Groq(api_key=GROQ_API_KEY)


# =========================================================
# 5. DOSYA OKUMA
# =========================================================

def read_file(upload):
    if upload is None:
        return ""

    name = upload.name.lower()
    data = upload.getvalue()

    try:
        if name.endswith(".pdf"):
            if PdfReader is None:
                return "PDF desteği için pypdf paketini kur."
            pdf = PdfReader(io.BytesIO(data))
            return "\n".join(
                page.extract_text() or "" for page in pdf.pages[:60]
            )[:25000]

        if name.endswith(".docx"):
            if Document is None:
                return "Word desteği için python-docx paketini kur."
            doc = Document(io.BytesIO(data))
            return "\n".join(p.text for p in doc.paragraphs)[:25000]

        if name.endswith((
            ".txt", ".md", ".csv", ".json", ".py", ".js", ".html",
            ".css", ".xml", ".yaml", ".yml"
        )):
            return data.decode("utf-8", errors="replace")[:25000]

        return ""
    except Exception as exc:
        return f"Dosya okunamadı: {exc}"


# =========================================================
# 6. GÖRSEL ANALİZİ — CLOUDFLARE VISION
# =========================================================

def analyze_image(image_bytes, mime_type, question):
    if not CF_ACCOUNT_ID or not CF_API_TOKEN:
        return (
            "Görsel analizi için CLOUDFLARE_ACCOUNT_ID ve "
            "CLOUDFLARE_API_TOKEN gerekli."
        )

    encoded = base64.b64encode(image_bytes).decode("utf-8")
    image_data_url = f"data:{mime_type};base64,{encoded}"

    endpoint = (
        f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}"
        f"/ai/run/{VISION_MODEL}"
    )

    payload = {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Lidya AI, a careful visual analysis assistant. "
                    "Describe only what can be supported by the image. "
                    "If labels are unclear, say so. For medical images, "
                    "provide educational information, not a diagnosis."
                ),
            },
            {"role": "user", "content": question},
        ],
        "image": image_data_url,
        "max_tokens": 900,
    }

    try:
        response = requests.post(
            endpoint,
            headers={"Authorization": f"Bearer {CF_API_TOKEN}"},
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
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
        return (
            "Görsel analiz isteği başarısız oldu. Cloudflare hesabında "
            "Vision modelinin kullanılabilirliğini ve erişim iznini kontrol et. "
            f"Ayrıntı: {exc}"
        )


# =========================================================
# 7. GÖRSEL ÜRETİMİ
# =========================================================

def generate_image(prompt):
    if not CF_ACCOUNT_ID or not CF_API_TOKEN:
        st.error("Görsel üretimi için Cloudflare API bilgileri gerekli.")
        return None

    endpoint = (
        f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}"
        f"/ai/run/{IMAGE_MODEL}"
    )

    try:
        response = requests.post(
            endpoint,
            headers={"Authorization": f"Bearer {CF_API_TOKEN}"},
            json={"prompt": prompt},
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        result = data.get("result", {})
        image_value = result.get("image") if isinstance(result, dict) else None

        if image_value:
            return Image.open(io.BytesIO(base64.b64decode(image_value)))

        st.error("Görsel yanıtı beklenen biçimde alınamadı.")
    except Exception as exc:
        st.error(f"Görsel üretimi başarısız: {exc}")
    return None


# =========================================================
# 8. İNTERNET ARAŞTIRMASI
# =========================================================

def web_search(query, max_results=6):
    if DDGS is None:
        return [], "Araştırma için ddgs paketi kurulu değil."

    try:
        with DDGS() as search_client:
            results = search_client.text(
                query,
                region="wt-wt",
                safesearch="moderate",
                max_results=max_results,
            )
        return list(results or []), None
    except Exception as exc:
        return [], str(exc)


def research_answer(query):
    results, error = web_search(query, max_results=6)

    if error:
        return (
            "İnternet araması yapılamadı. Bağlantıyı ve ddgs paketini kontrol et.\n\n"
            f"Ayrıntı: {error}"
        ), []

    if not results:
        return "Aramada sonuç bulunamadı. İsteğini farklı kelimelerle dene.", []

    source_text = []
    for i, item in enumerate(results, 1):
        source_text.append(
            f"[{i}] {item.get('title', 'Başlıksız')}\n"
            f"URL: {item.get('href', '')}\n"
            f"Özet: {item.get('body', '')}"
        )

    combined = "\n\n".join(source_text)
    client = groq_client()

    if client is None:
        answer = (
            "Arama sonuçları bulundu. API anahtarı olmadan sonuçların "
            "yapay zekâ tarafından özetlenmesi yapılamıyor."
        )
    else:
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Sen Lidya AI araştırma asistanısın. Yalnızca verilen "
                            "arama sonuçlarına dayanarak dikkatli bir özet yaz. "
                            "Kaynaklarda olmayan bilgileri uydurma. Kaynakların "
                            "güvenilirliğinin ayrıca kontrol edilmesi gerekebileceğini "
                            "belirt. Her önemli iddiayı [1], [2] gibi sonuç "
                            "numaralarıyla ilişkilendir. Kullanıcının dilinde cevap ver."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Soru: {query}\n\nArama sonuçları:\n{combined}",
                    },
                ],
                temperature=0.2,
                max_tokens=1600,
            )
            answer = response.choices[0].message.content or "Özet oluşturulamadı."
        except Exception as exc:
            answer = f"Sonuçlar bulundu ama özet oluşturulamadı: {exc}"

    return answer, results


# =========================================================
# 9. LIDYA SOHBETİ
# =========================================================

def ask_lidya(prompt, module, history=None, file_context=""):
    client = groq_client()
    if client is None:
        return (
            "Groq bağlantısı kurulamıyor. Streamlit Cloud → App settings → "
            "Secrets bölümünde GROQ_API_KEY değerini kontrol et."
        )

    system = (
        "Sen Lidya AI adlı eğitim ve üretkenlik asistanısın. "
        "Lidya AI projesini Şeymanur Acun geliştirmiştir; temel modelin "
        "geliştiricisiyle proje geliştiricisini birbirine karıştırma. "
        "Kullanıcının seçtiği dilde yanıt ver. İnternette arama yaptığını "
        "veya dosyayı analiz ettiğini yalnızca gerçekten yapıldığında söyle. "
        "Açık, doğru, güvenli ve yararlı ol.\n"
        + SPECIALISTS.get(module, SPECIALISTS["chat"])
    )

    if file_context:
        prompt = (
            "Kullanıcının eklediği dosyadan çıkarılan metin:\n"
            + file_context[:18000]
            + "\n\nKullanıcının isteği:\n"
            + prompt
        )

    messages = [{"role": "system", "content": system}]
    for item in (history or [])[-12:]:
        if item.get("role") in ("user", "assistant"):
            messages.append({
                "role": item["role"],
                "content": item.get("content", "")[:5000],
            })
    messages.append({"role": "user", "content": prompt})

    try:
        result = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.5,
            max_tokens=1800,
        )
        return result.choices[0].message.content or "Yanıt üretilemedi."
    except Exception as exc:
        return f"Yanıt alınırken hata oluştu: {exc}"


# =========================================================
# 10. SOL MENÜ
# =========================================================

with st.sidebar:
    st.markdown("## 💜 Lidya AI")
    st.caption("Düşün. Öğren. Üret. Keşfet.")

    language = st.selectbox(
        "🌐 Dil / Language",
        list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.language),
    )
    st.session_state.language = language

    st.markdown("---")
    chosen = st.radio(
        "Çalışma alanları",
        MODULES,
        index=MODULES.index(st.session_state.module),
        format_func=lambda key: (
            "🏠 " + label(key) if key == "home" else label(key)
        ),
        label_visibility="collapsed",
    )
    st.session_state.module = chosen

    st.markdown("---")
    st.caption("🕒 " + now_text() + " · Türkiye")

    if st.button("🧹 " + label("clear"), use_container_width=True):
        st.session_state.messages = []
        st.rerun()


module = st.session_state.module


# =========================================================
# 11. ANA SAYFA
# =========================================================

if module == "home":
    st.markdown("""
    <div class="lidya-hero">
      <div class="lidya-title">💜 Lidya AI</div>
      <div class="lidya-subtitle">Düşün. Öğren. Üret. Keşfet.</div>
      <p class="small-muted">Built with curiosity and Python.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### " + label("welcome"))
    st.write(
        "Bütün çalışma alanları sol menüde. Sohbet, araştırma, dosya analizi, "
        "bilim, matematik, üniversite keşfi ve yaratıcı araçlara buradan ulaş."
    )
    st.info(
        "Araştırma ve görsel analiz API bağlantıları hizmet erişimine ve "
        "kullanım limitlerine bağlıdır. Yanıtlardaki kaynakları açıp "
        "doğrulamayı unutma."
    )


# =========================================================
# 12. ARAŞTIRMA MERKEZİ
# =========================================================

elif module == "research":
    st.title("🔎 " + label("research"))
    st.write(
        "İnternette arama yap, bulunan sonuçların özetini gör ve kaynak sayfalarını aç."
    )

    query = st.text_area(
        "Ne araştırmak istiyorsun?",
        placeholder="Örneğin: Harvard lisans başvurusu için resmî sınav politikası",
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
                for i, result in enumerate(results, 1):
                    title = result.get("title", "Başlıksız")
                    url = result.get("href", "")
                    body = result.get("body", "")
                    st.markdown(f"**[{i}] [{title}]({url})**")
                    if body:
                        st.write(body)
                    st.caption("Kaynağı açıp tarihin ve bilginin doğruluğunu kontrol et.")


# =========================================================
# 13. ÜNİVERSİTE KEŞFİ
# =========================================================

elif module == "universities":
    st.title("🎓 " + label("universities"))
    st.write(
        "Üniversitelerin resmî sitelerini ve lisans kabul sayfalarını incele. "
        "Logoların yerine sitelerin simgeleri gösterilir; simgeler her zaman "
        "resmî yüksek çözünürlüklü arma değildir."
    )

    search = st.text_input("Üniversite ara")
    filtered = [u for u in UNIVERSITIES if search.lower() in u[0].lower()]

    for start in range(0, len(filtered), 2):
        cols = st.columns(2)
        for col, uni in zip(cols, filtered[start:start + 2]):
            name, domain, site, admissions = uni
            with col:
                st.markdown('<div class="university-card">', unsafe_allow_html=True)
                left, right = st.columns([1, 4])
                with left:
                    st.image(
                        f"https://www.google.com/s2/favicons?domain={domain}&sz=128",
                        width=48,
                    )
                with right:
                    st.markdown(f"#### {name}")
                    st.markdown(f"[Resmî site]({site})")
                    st.markdown(f"[Lisans kabul sayfası]({admissions})")
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Bir üniversite hakkında araştırma yap")
    uni_names = [u[0] for u in UNIVERSITIES]
    selected_uni = st.selectbox("Üniversite", uni_names)
    topic = st.selectbox(
        "Araştırma konusu",
        [
            "Lisans kabul koşulları",
            "Maddi yardım ve burslar",
            "Uluslararası öğrenci başvuruları",
            "Başvuru tarihleri",
            "İlgilendiğim bölüm ve programlar",
        ],
    )

    if st.button("Resmî sayfaları araştır", type="primary"):
        chosen_uni = next(u for u in UNIVERSITIES if u[0] == selected_uni)
        search_query = f"site:{chosen_uni[1]} {topic} undergraduate admissions"
        with st.spinner("Web'de arama yapılıyor..."):
            answer, results = research_answer(search_query)
        st.markdown(answer)
        st.markdown("### Sonuçlar")
        for result in results:
            st.markdown(
                f"- [{result.get('title', 'Kaynak')}]"
                f"({result.get('href', '')}) — {result.get('body', '')}"
            )

    st.caption(
        "Arama motoru sonuçları tek başına resmî doğrulama değildir. "
        "Özellikle sınav, burs ve son tarih bilgilerini üniversitenin kendi "
        "kabul sayfasından doğrula."
    )


# =========================================================
# 14. DOSYA LABORATUVARI
# =========================================================

elif module == "file":
    st.title("📁 " + label("file"))
    st.write("Metin dosyalarını oku veya görsel yükleyerek görsel analizi yap.")

    uploaded = st.file_uploader(
        "Dosya yükle",
        type=[
            "pdf", "docx", "txt", "md", "csv", "json", "py", "js",
            "html", "css", "xml", "yaml", "yml", "png", "jpg", "jpeg", "webp"
        ],
        key="file_lab",
    )

    if uploaded:
        st.session_state.last_file_name = uploaded.name
        ext = uploaded.name.lower().rsplit(".", 1)[-1]

        if ext in ("png", "jpg", "jpeg", "webp"):
            st.image(uploaded, caption=uploaded.name, use_container_width=True)
            image_question = st.text_area(
                "Bu görsel hakkında ne öğrenmek istiyorsun?",
                value="Bu görseli ayrıntılı olarak açıkla.",
                key="image_question",
            )
            if st.button("Görseli analiz et", type="primary"):
                mime = {
                    "png": "image/png",
                    "jpg": "image/jpeg",
                    "jpeg": "image/jpeg",
                    "webp": "image/webp",
                }.get(ext, "image/png")
                with st.spinner("Görsel analiz ediliyor..."):
                    result = analyze_image(
                        uploaded.getvalue(), mime, image_question
                    )
                st.markdown(result)

        else:
            text_content = read_file(uploaded)
            st.session_state.last_file_text = text_content
            with st.expander("Dosyadan çıkarılan metin"):
                st.text(text_content[:12000])

            task = st.text_area(
                "Dosyayla ilgili isteğin",
                placeholder="Özetle, açıkla, ana fikirleri çıkar, kodu incele...",
                key="file_task",
            )
            if st.button("Dosyayı analiz et", type="primary"):
                if not text_content.strip():
                    st.warning(
                        "Dosyadan okunabilir metin çıkarılamadı. "
                        "Taranmış PDF'ler için OCR gerekebilir."
                    )
                elif not task.strip():
                    st.warning("Dosyayla ilgili ne istediğini yaz.")
                else:
                    with st.spinner("Dosya analiz ediliyor..."):
                        result = ask_lidya(
                            task, "chat", [], file_context=text_content
                        )
                    st.markdown(result)


# =========================================================
# 15. GÖRSEL ATÖLYESİ
# =========================================================

elif module == "image":
    st.title("🎨 " + label("image"))
    prompt = st.text_area(
        "Oluşturmak istediğin görseli tarif et",
        placeholder="Örneğin: İnsan hücresinin bilimsel eğitim illüstrasyonu",
        height=120,
    )

    if st.button("Görsel oluştur", type="primary"):
        if not prompt.strip():
            st.warning("Önce bir açıklama yaz.")
        else:
            with st.spinner("Görsel oluşturuluyor..."):
                generated = generate_image(prompt)
            if generated:
                st.image(generated, caption="Lidya AI görseli")
                buf = io.BytesIO()
                generated.save(buf, format="PNG")
                st.download_button(
                    "PNG olarak indir",
                    buf.getvalue(),
                    file_name="lidya_image.png",
                    mime="image/png",
                )


# =========================================================
# 16. SİMÜLASYON LABORATUVARI
# =========================================================

elif module == "sim":
    st.title("🪐 " + label("sim"))
    kind = st.selectbox(
        "Simülasyon",
        ["Fonksiyon grafiği", "Mermi hareketi", "Dalga hareketi", "Dairesel yörünge"],
    )

    if kind == "Fonksiyon grafiği":
        function = st.selectbox("Fonksiyon", ["x²", "sin(x)", "cos(x)", "x³ - 2x"])
        x = np.linspace(-10, 10, 400)
        y = {
            "x²": x ** 2,
            "sin(x)": np.sin(x),
            "cos(x)": np.cos(x),
            "x³ - 2x": x ** 3 - 2 * x,
        }[function]
        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_xlabel("x")
        ax.set_ylabel("f(x)")
        ax.grid(True)
        st.pyplot(fig)
        plt.close(fig)

    elif kind == "Mermi hareketi":
        angle = np.radians(st.slider("Atış açısı", 10, 80, 45))
        speed = st.slider("Başlangıç hızı (m/s)", 5, 100, 30)
        gravity = 9.81
        vx, vy = speed * np.cos(angle), speed * np.sin(angle)
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
        st.write(f"İdeal modelde yaklaşık menzil: **{x[-1]:.1f} m**")
        st.caption("Hava direnci ve arazi yüksekliği hesaba katılmamıştır.")

    elif kind == "Dalga hareketi":
        amp = st.slider("Genlik", 1, 10, 4)
        freq = st.slider("Frekans", 1, 10, 2)
        x = np.linspace(0, 4 * np.pi, 400)
        y = amp * np.sin(freq * x)
        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_xlabel("Konum")
        ax.set_ylabel("Genlik")
        ax.grid(True)
        st.pyplot(fig)
        plt.close(fig)

    else:
        radius = st.slider("Yörünge yarıçapı", 1, 10, 5)
        theta = np.linspace(0, 2 * np.pi, 360)
        fig, ax = plt.subplots()
        ax.plot(radius * np.cos(theta), radius * np.sin(theta))
        ax.scatter([0], [0])
        ax.set_aspect("equal", adjustable="box")
        ax.set_title("Basitleştirilmiş dairesel yörünge")
        ax.grid(True)
        st.pyplot(fig)
        plt.close(fig)


# =========================================================
# 17. VİDEO ATÖLYESİ
# =========================================================

elif module == "video":
    st.title("🎬 " + label("video"))
    st.info(
        "Bu sürüm tek bir görselden yakınlaşma animasyonu üretebilir. "
        "Bu, metinden gerçek yapay zekâ videosu üretimi değildir."
    )
    video_upload = st.file_uploader(
        "Görsel yükle",
        type=["png", "jpg", "jpeg", "webp"],
        key="video_upload",
    )
    seconds = st.slider("Animasyon süresi (saniye)", 2, 8, 4)

    if st.button("Animasyon oluştur"):
        if not video_upload:
            st.warning("Önce görsel yükle.")
        else:
            try:
                import imageio.v2 as imageio
                original = Image.open(video_upload).convert("RGB")
                width, height = original.size
                frames = []

                for i in range(seconds * 8):
                    scale = 1 + 0.12 * i / max(1, seconds * 8 - 1)
                    resized = original.resize(
                        (int(width * scale), int(height * scale))
                    )
                    left = (resized.width - width) // 2
                    top = (resized.height - height) // 2
                    frame = resized.crop((left, top, left + width, top + height))
                    frames.append(np.array(frame))

                with tempfile.NamedTemporaryFile(
                    suffix=".mp4", delete=False
                ) as temp:
                    path = temp.name

                imageio.mimsave(path, frames, fps=8, codec="libx264")
                with open(path, "rb") as video_file:
                    video_bytes = video_file.read()

                st.video(video_bytes)
                st.download_button(
                    "MP4 olarak indir",
                    video_bytes,
                    file_name="lidya_animation.mp4",
                    mime="video/mp4",
                )
            except Exception as exc:
                st.error(f"Animasyon oluşturulamadı: {exc}")


# =========================================================
# 18. SES VE KARAOKE
# =========================================================

elif module == "karaoke":
    st.title("🎤 " + label("karaoke"))
    st.write("Ses dosyası yükleyebilir, kaydedebilir ve yazıya çevirebilirsin.")

    audio = st.file_uploader(
        "Ses dosyası yükle",
        type=["wav", "mp3", "m4a", "ogg", "flac"],
        key="audio_upload",
    )

    if audio:
        st.audio(audio)
        if st.button("Ses dosyasını yazıya çevir"):
            client = groq_client()
            if client is None:
                st.error("GROQ_API_KEY ayarlı değil.")
            else:
                try:
                    with st.spinner("Ses yazıya çevriliyor..."):
                        transcription = client.audio.transcriptions.create(
                            file=(audio.name, audio.getvalue()),
                            model="whisper-large-v3",
                            response_format="text",
                        )
                    st.text_area("Transkripsiyon", str(transcription), height=180)
                except Exception as exc:
                    st.error(f"Ses çevrilemedi: {exc}")

    st.markdown("### Mikrofon kaydı")
    microphone = st.audio_input("Sesini kaydet")
    if microphone:
        st.audio(microphone)
        if st.button("Mikrofon kaydını yazıya çevir"):
            client = groq_client()
            if client is None:
                st.error("GROQ_API_KEY ayarlı değil.")
            else:
                try:
                    with st.spinner("Kayıt yazıya çevriliyor..."):
                        transcription = client.audio.transcriptions.create(
                            file=("recording.wav", microphone.getvalue()),
                            model="whisper-large-v3",
                            response_format="text",
                        )
                    st.text_area("Kayıt metni", str(transcription), height=180)
                except Exception as exc:
                    st.error(f"Kayıt çevrilemedi: {exc}")

    st.markdown("### Metni sesli dinle")
    tts_text = st.text_area("Okunacak metin", key="tts_text")
    if tts_text:
        escaped = json.dumps(tts_text, ensure_ascii=False)
        st.components.v1.html(
            f"""
            <button onclick='speak()'>🔊 Sesli oku</button>
            <button onclick='window.speechSynthesis.cancel()'>⏹ Durdur</button>
            <script>
            function speak() {{
                const u = new SpeechSynthesisUtterance({escaped});
                window.speechSynthesis.speak(u);
            }}
            </script>
            """,
            height=70,
        )


# =========================================================
# 19. OTURUM HAFIZASI
# =========================================================

elif module == "memory":
    st.title("🧠 " + label("memory"))
    st.warning(
        "Bu sürümde hafıza yalnızca mevcut oturumda tutulur. "
        "Kalıcı hafıza için veritabanı ve kullanıcıya özel kayıt sistemi gerekir."
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
        for i, memory in enumerate(st.session_state.memory_items, 1):
            st.write(f"{i}. {memory['text']} · {memory['time']}")
    else:
        st.caption("Henüz bilgi eklenmedi.")

    if st.button("Hafızayı temizle"):
        st.session_state.memory_items = []
        st.success("Oturum hafızası temizlendi.")


# =========================================================
# 20. AYARLAR
# =========================================================

elif module == "settings":
    st.title("⚙️ " + label("settings"))
    st.write(
        "Groq sohbet API:",
        "Anahtar bulundu" if GROQ_API_KEY else "GROQ_API_KEY eksik",
    )
    st.write(
        "Cloudflare API:",
        "Anahtarlar bulundu" if (CF_ACCOUNT_ID and CF_API_TOKEN)
        else "Cloudflare API bilgileri eksik",
    )
    st.write(
        "Web araması:",
        "ddgs kullanılabilir" if DDGS is not None else "ddgs paketi eksik",
    )
    st.write("Dil:", st.session_state.language)
    st.write("Türkiye saati:", now_text())
    st.caption("API anahtarlarını kodun içine değil, Streamlit Secrets'a ekle.")


# =========================================================
# 21. SOHBET VE ALAN UZMANLARI
# =========================================================

elif module in SPECIALISTS:
    st.title("💜 " + label(module))
    st.caption("🕒 " + now_text() + " · Türkiye")

    attachment = st.file_uploader(
        "İsteğe bağlı dosya veya görsel ekle",
        type=[
            "pdf", "docx", "txt", "md", "csv", "json", "py", "js",
            "html", "css", "xml", "yaml", "yml", "png", "jpg", "jpeg", "webp"
        ],
        key=f"attachment_{module}",
    )

    image_bytes = None
    image_mime = None
    file_context = ""

    if attachment:
        ext = attachment.name.lower().rsplit(".", 1)[-1]
        if ext in ("png", "jpg", "jpeg", "webp"):
            image_bytes = attachment.getvalue()
            image_mime = {
                "png": "image/png",
                "jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "webp": "image/webp",
            }[ext]
            st.image(attachment, caption=attachment.name, use_container_width=True)
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
            m for m in st.session_state.messages if m.get("module") == module
        ]

        if any(term in prompt.lower() for term in (
            "seni kim yaptı", "seni kim geliştirdi", "seni kim tasarladı",
            "who created you", "who developed you", "who designed you"
        )):
            answer = (
                "Lidya AI projesini Şeymanur Acun geliştirdi. "
                "Lidya'nın kullandığı temel yapay zekâ modeli ve diğer "
                "hizmetler ilgili sağlayıcılar tarafından geliştirilmiştir."
            )

        elif image_bytes is not None:
            with st.spinner("Görsel analiz ediliyor..."):
                answer = analyze_image(image_bytes, image_mime, prompt)

        else:
            with st.spinner("Lidya düşünüyor..."):
                answer = ask_lidya(
                    prompt, module, prior, file_context=file_context
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
# 22. ALT BİLGİ
# =========================================================

st.markdown("---")
st.caption("💜 Lidya AI · Built with curiosity and Python.")

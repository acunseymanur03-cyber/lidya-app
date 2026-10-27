import os
import io
import json
import base64
import mimetypes
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
import streamlit as st
from groq import Groq
from pypdf import PdfReader
from docx import Document


# =========================================================
#  LIDYA AI — CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Lidya AI",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_NAME = "Lidya AI"
TEXT_MODEL = "openai/gpt-oss-20b"
VISION_MODEL = "qwen/qwen3.8-27b"

LANGUAGES = [
    "Türkçe",
    "English",
    "العربية",
    "Français",
    "Deutsch",
    "Español",
    "Italiano",
    "日本語",
    "简体中文",
]

MODULES = [
    "💬 Lidya ile Sohbet",
    "📚 Dosya Laboratuvarı",
    "➗ Matematik ve TYT/AYT/SAT",
    "🏛️ Tarih",
    "🎓 Üniversite Araştırmaları",
    "🔬 Bilim ve Araştırma",
    "🫀 Tıp ve Anatomi",
    "⚖️ Hukuk Araştırmaları",
    "🌍 Dil Öğretmeni",
    "💻 Yazılım Mühendisliği",
    "📊 Veri Analizi",
    "🛡️ Siber Güvenlik",
    "✍️ Yazma ve Yaratıcılık",
    "🎨 Görsel Atölyesi",
    "🎤 Karaoke ve Ses",
    "🧠 Öğrenme Koçu",
]

UNIVERSITIES = {
    "Harvard University": "https://college.harvard.edu/",
    "University of Oxford": "https://www.ox.ac.uk/admissions/undergraduate",
    "University of Cambridge": "https://www.undergraduate.study.cam.ac.uk/",
    "Massachusetts Institute of Technology (MIT)": "https://mitadmissions.org/",
    "Yale University": "https://admissions.yale.edu/",
    "Columbia University": "https://undergrad.admissions.columbia.edu/",
    "Princeton University": "https://admission.princeton.edu/",
    "Stanford University": "https://admission.stanford.edu/",
}


# =========================================================
#  SECRETS AND CLIENT
# =========================================================

def get_secret(name, default=""):
    try:
        value = st.secrets.get(name, default)
        if value:
            return str(value)
    except Exception:
        pass

    return os.getenv(name, default)


GROQ_API_KEY = get_secret("GROQ_API_KEY")
CLOUDFLARE_ACCOUNT_ID = get_secret("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = get_secret("CLOUDFLARE_API_TOKEN")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# =========================================================
#  SESSION STATE
# =========================================================

def initialize_state():
    defaults = {
        "messages": [],
        "memory": [],
        "language": "Türkçe",
        "module": "💬 Lidya ile Sohbet",
        "user_profile": {
            "education_level": "",
            "interests": [],
            "goals": [],
        },
        "last_audio_text": "",
        "last_generated_image": None,
        "quiz_question": None,
        "quiz_answer": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_state()


def local_timestamp():
    try:
        return datetime.now(ZoneInfo("Europe/Istanbul")).strftime(
            "%d.%m.%Y %H:%M:%S"
        )
    except Exception:
        return datetime.now().strftime("%d.%m.%Y %H:%M:%S")


# =========================================================
#  INSTRUCTIONS
# =========================================================

def get_system_prompt(module, language, memory):
    memory_text = "\n".join(
        f"- {item}" for item in memory[-20:]
    ) or "Henüz kaydedilmiş bir hatırlatma yok."

    common_prompt = f"""
Sen Lidya AI'sın. Lidya AI, Şeymanur Acun tarafından geliştirilen
bir yapay zekâ projesidir.

Kullandığın yapay zekâ modelleri ve altyapı hizmetleri farklı
sağlayıcılara ait olabilir. Bu teknolojilerin tamamını kendinin
geliştirdiğini iddia etme.

Temel yaklaşımın:
- Yardımcı, açık, dürüst ve öğretici ol.
- Bilmediğin bir şeyi biliyormuş gibi anlatma.
- Güncel bilgi gerektiğinde mümkünse internet araması kullan.
- Kaynak bulduğunda kaynak adını ve doğrudan bağlantısını belirt.
- Kaynak veya bağlantı uydurma.
- Kullanıcı başka bir dil istemedikçe yanıt dilini {language} olarak kullan.
- Kullanıcı farklı dillerde karışık yazarsa mesajın tamamını anlamaya çalış.
- Teknik terimleri gerektiğinde özgün dilinde de koru.
- Kullanıcının isteğini anlamadıysan kısa bir açıklama sorusu sor.
- Eğitim sorularında yalnızca cevabı değil, gerekçeyi de açıkla.
- Sağlık, hukuk ve finans gibi hassas konularda sınırlarını belirt.
- Tıbbi görselleri veya açıklamaları kesin tanı yerine eğitim amacıyla ele al.
- Kullanıcıya ait özel bilgileri gereksiz yere tekrar etme.

Kullanıcının bu oturumda açıkça kaydettiği hatırlatmalar:
{memory_text}

Aktif bölüm:
{module}
"""

    module_instructions = {
        "➗ Matematik ve TYT/AYT/SAT": """
Matematik öğretmeni gibi davran.
İlkokul matematiğinden ileri düzeye kadar konuyu kullanıcının
seviyesine göre açıkla. TYT, AYT, SAT ve Cambridge matematik
konularında adım adım öğretim yap.

Sorularda:
1. Verilenleri belirle.
2. Uygun yöntemi açıkla.
3. İşlemleri adım adım göster.
4. Sonucu kontrol et.
5. Gerekirse benzer bir alıştırma öner.

Görsel sorularında okunmayan bir bölüm varsa bunu açıkça belirt.
Öğrencinin seviyesini bilmediğinde kısa bir seviye sorusu sor.
""",
        "🏛️ Tarih": """
Tarih öğretmeni gibi davran. Olayları kronoloji, nedenler,
gelişmeler ve sonuçlar açısından açıkla. Tarihî olgularla
yorumları ayır. Tartışmalı konularda farklı görüşleri belirt.
Güncel araştırma gerektiğinde kaynak ara ve kaynakları göster.
""",
        "🎓 Üniversite Araştırmaları": """
Üniversiteleri karşılaştırırken resmî kabul ve üniversite
kaynaklarını önceliklendir. Kabul koşulları, sınavlar, başvuru
tarihleri, programlar, finansal yardım ve araştırma olanaklarını
birbirinden ayır.

Güncel bilgi için internet araması yapabiliyorsan yap.
Bilginin hangi başvuru yılına ait olduğunu belirt.
Bilinmeyen koşulları kesinmiş gibi sunma.

Öğrencinin notlarıyla yayımlanmış ölçütleri karşılaştırabilirsin;
ancak kabul olasılığına dair kesin bir yüzde verme ve kabul
garantisi sunma. Üniversitelerin logolarını veya isimlerini
kullanmak, resmî ortaklık bulunduğu anlamına gelmez.
""",
        "🎤 Karaoke ve Ses": """
Kullanıcının ses kaydı, telaffuzu ve şarkı söyleme pratiği
konusunda yardımcı ol. Kullanıcı bir ses kaydı sağlarsa,
erişilebilen özellikler ölçüsünde geri bildirim ver.

Ses kaydı veya transkript yoksa sesini analiz etmiş gibi davranma.
Lisanslı şarkı sözlerini uzun biçimde yeniden üretme. Bunun
yerine kullanıcının sağladığı sözleri analiz et, kısa alıntılarla
çalış veya özgün egzersizler oluştur.
""",
        "📚 Dosya Laboratuvarı": """
Yüklenen belge ve görselleri dikkatle incele. Belgenin içeriğini
özetle, soruları yanıtla, kavramları açıkla veya metni düzenle.
Belgede olmayan bilgileri belgeye aitmiş gibi gösterme.
Dosya içeriği eksik okunmuşsa bunu belirt.
""",
        "🫀 Tıp ve Anatomi": """
Anatomi, fizyoloji ve tıp eğitimi konusunda bilimsel ve dikkatli
açıklamalar yap. Eğitim amacıyla anlatım ile gerçek bir hastaya
yönelik tıbbi değerlendirmeyi birbirinden ayır. Görseldeki
yapıları kesin olarak belirleyemiyorsan belirsizliği açıkla.
""",
        "💻 Yazılım Mühendisliği": """
Kodları açıklanabilir, bakımı kolay ve güvenli biçimde yaz.
Hatalarda muhtemel nedenleri ve çözümü göster. API anahtarlarını
koda gömme; secrets veya ortam değişkenleri kullan.
Kodun test edilmediği durumlarda test edildiğini iddia etme.
""",
        "🛡️ Siber Güvenlik": """
Siber güvenlik konularını savunma, eğitim, güvenli yapılandırma
ve yetkili testler çerçevesinde ele al.
""",
        "🌍 Dil Öğretmeni": """
Kullanıcının dil seviyesine uygun öğretim yap. Hataları nazikçe
düzelt, kısa örnekler ver ve gerektiğinde telaffuz çalışmaları
öner. Kullanıcı isterse iki dilli açıklamalar kullan.
""",
        "🧠 Öğrenme Koçu": """
Kullanıcının hedeflerini küçük, uygulanabilir adımlara böl.
Gerçekçi çalışma planları oluştur. Uykusuz kalmayı veya aşırı
çalışmayı teşvik etme. Dinlenme ve sürdürülebilirliği gözet.
""",
    }

    return common_prompt + "\n\n" + module_instructions.get(module, "")


# =========================================================
#  DOCUMENT EXTRACTION
# =========================================================

def extract_pdf(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
            if text.strip():
                pages.append(f"[Sayfa {page_number}]\n{text}")
        except Exception:
            continue

    return "\n\n".join(pages)


def extract_docx(file_bytes):
    document = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]

    for table in document.tables:
        for row in table.rows:
            paragraphs.append(" | ".join(cell.text for cell in row.cells))

    return "\n".join(paragraphs)


def extract_txt(file_bytes):
    for encoding in ("utf-8", "utf-8-sig", "cp1254", "latin-1"):
        try:
            return file_bytes.decode(encoding)
        except Exception:
            continue
    return ""


def process_uploaded_file(uploaded_file):
    data = uploaded_file.getvalue()
    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        return extract_pdf(data), None

    if name.endswith(".docx"):
        return extract_docx(data), None

    if name.endswith((".txt", ".md", ".csv", ".json")):
        return extract_txt(data), None

    if name.endswith((".png", ".jpg", ".jpeg", ".webp")):
        mime = uploaded_file.type or mimetypes.guess_type(name)[0]
        image_data = base64.b64encode(data).decode("utf-8")
        return None, {
            "name": uploaded_file.name,
            "mime": mime,
            "base64": image_data,
        }

    return (
        f"'{uploaded_file.name}' dosya türü bu sürümde metin olarak "
        "okunamıyor. PDF, DOCX, TXT, MD, CSV, JSON veya görsel deneyebilirsin.",
        None,
    )


# =========================================================
#  CHAT AND IMAGE ANALYSIS
# =========================================================

def analyze_image(question, image_data, language, module):
    if not client:
        return "Groq API anahtarı tanımlanmamış."

    try:
        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Yanıt dilin {language}. "
                        f"Aktif bölüm: {module}. "
                        "Görselde gerçekten görünenleri açıkla. "
                        "Okunmayan ayrıntıları uydurma."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": (
                                    f"data:{image_data['mime']};base64,"
                                    f"{image_data['base64']}"
                                )
                            },
                        },
                    ],
                },
            ],
            temperature=0.2,
            max_tokens=3000,
        )
        return response.choices[0].message.content or "Yanıt alınamadı."

    except Exception as e:
        return (
            "Görsel analizi yapılamadı. Vision modelinin hesabında "
            "kullanılabilir olduğundan emin ol. Teknik ayrıntı: "
            f"{str(e)[:500]}"
        )


def answer_with_groq(user_text, module, language, memory, attachments=None):
    if not client:
        return (
            "Groq API anahtarı bulunamadı. Streamlit Cloud'da "
            "Settings → Secrets bölümüne GROQ_API_KEY eklemelisin."
        )

    attachments = attachments or []
    system_prompt = get_system_prompt(module, language, memory)

    user_content = user_text.strip() or "Yüklediğim dosyayı incele."

    for item in attachments:
        if item.get("text"):
            user_content += (
                f"\n\n--- Dosya: {item['name']} ---\n"
                f"{item['text'][:25000]}"
            )

    history = [
        {"role": "system", "content": system_prompt}
    ]

    for message in st.session_state.messages[-12:]:
        if message.get("role") in ("user", "assistant"):
            history.append({
                "role": message["role"],
                "content": message["content"][:12000],
            })

    history.append({"role": "user", "content": user_content})

    try:
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=history,
            temperature=0.4,
            max_tokens=4000,
        )

        return response.choices[0].message.content or "Yanıt alınamadı."

    except Exception as e:
        return (
            "Yanıt oluşturulamadı. API anahtarını, model erişimini "
            "ve kullanım limitlerini kontrol et.\n\n"
            f"Teknik ayrıntı: {str(e)[:500]}"
        )


# =========================================================
#  INTERNET SEARCH
# =========================================================

def web_search(query):
    """
    Groq hesabı ve model erişimi destekliyorsa yerleşik tarayıcı
    aramasını dener. Desteklenmezse kullanıcıya hata verir.
    """
    if not client:
        return (
            "İnternet araması için önce GROQ_API_KEY tanımlanmalı."
        )

    try:
        # Responses API ve browser_search desteği hesap/model
        # kullanılabilirliğine bağlıdır.
        response = client.responses.create(
            model=TEXT_MODEL,
            input=(
                "Araştırma konusu: " + query +
                "\nGüvenilir ve mümkünse resmî kaynakları kullan. "
                "Bulduğun kaynakların başlıklarını ve doğrudan "
                "bağlantılarını yanıtında belirt. Güncel tarihleri "
                "kontrol et. Kaynak veya bağlantı uydurma."
            ),
            tools=[{"type": "browser_search"}],
        )

        output_text = getattr(response, "output_text", None)
        if output_text:
            return output_text

        return str(response)

    except Exception as e:
        return (
            "Bu ortamda yerleşik internet araması kullanılamadı. "
            "Groq hesabında Responses API ve browser_search "
            "desteğinin açık olması gerekebilir.\n\n"
            f"Teknik ayrıntı: {str(e)[:500]}"
        )


# =========================================================
#  IMAGE GENERATION
# =========================================================

def generate_image(prompt):
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        return None, (
            "Görsel üretimi için CLOUDFLARE_ACCOUNT_ID ve "
            "CLOUDFLARE_API_TOKEN tanımlanmalı."
        )

    endpoint = (
        "https://api.cloudflare.com/client/v4/accounts/"
        f"{CLOUDFLARE_ACCOUNT_ID}/ai/run/"
        "@cf/black-forest-labs/flux-1-schnell"
    )

    try:
        response = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
                "Content-Type": "application/json",
            },
            json={"prompt": prompt},
            timeout=120,
        )

        if response.status_code != 200:
            return None, (
                "Görsel üretim servisi hata verdi: "
                f"HTTP {response.status_code} — {response.text[:300]}"
            )

        content_type = response.headers.get("content-type", "")

        if "application/json" in content_type:
            result = response.json()
            if "result" in result and "image" in result["result"]:
                image_bytes = base64.b64decode(result["result"]["image"])
                return image_bytes, None

        return response.content, None

    except Exception as e:
        return None, f"Görsel üretilemedi: {str(e)[:400]}"


# =========================================================
#  AUDIO TRANSCRIPTION
# =========================================================

def transcribe_audio(uploaded_audio):
    if not client:
        return "Ses yazıya çevrilemedi: GROQ_API_KEY eksik."

    try:
        uploaded_audio.seek(0)
        transcription = client.audio.transcriptions.create(
            file=(
                uploaded_audio.name,
                uploaded_audio.read(),
            ),
            model="whisper-large-v3",
            response_format="text",
        )

        if isinstance(transcription, str):
            return transcription

        return getattr(transcription, "text", str(transcription))

    except Exception as e:
        return f"Ses yazıya çevrilemedi: {str(e)[:400]}"


# =========================================================
#  SIDEBAR
# =========================================================

with st.sidebar:
    st.title("💜 Lidya AI")
    st.caption("Düşün. Öğren. Üret. Keşfet.")

    selected_module = st.selectbox(
        "Çalışma alanı",
        MODULES,
        index=MODULES.index(st.session_state.module)
        if st.session_state.module in MODULES else 0,
    )

    st.session_state.module = selected_module

    selected_language = st.selectbox(
        "Yanıt dili",
        LANGUAGES,
        index=LANGUAGES.index(st.session_state.language)
        if st.session_state.language in LANGUAGES else 0,
    )

    st.session_state.language = selected_language

    st.divider()

    st.subheader("🧠 Hatırlatmalar")
    st.caption(
        "Bu sürümde hatırlatmalar mevcut oturumda saklanır. "
        "Sayfa oturumu sona ererse kalıcı hafıza garanti edilmez."
    )

    new_memory = st.text_input(
        "Hatırlatılacak bilgi",
        placeholder="Örn. İngilizce seviyem A2",
        key="new_memory_input",
    )

    if st.button("💾 Hatırla", use_container_width=True):
        if new_memory.strip():
            st.session_state.memory.append(new_memory.strip())
            st.success("Bu oturum için hatırlatmalara eklendi.")
            st.rerun()

    if st.session_state.memory:
        for i, item in enumerate(st.session_state.memory):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.write("• " + item)
            with col2:
                if st.button("✕", key=f"delete_memory_{i}"):
                    st.session_state.memory.pop(i)
                    st.rerun()

    st.divider()

    if st.button("🆕 Yeni sohbet", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("📥 Sohbeti dışa aktar", use_container_width=True):
        export_data = json.dumps(
            st.session_state.messages,
            ensure_ascii=False,
            indent=2,
        )
        st.download_button(
            "JSON dosyasını indir",
            data=export_data,
            file_name="lidya_sohbet.json",
            mime="application/json",
            use_container_width=True,
        )


# =========================================================
#  HEADER
# =========================================================

st.title(st.session_state.module)
st.caption(
    f"💜 {APP_NAME} · "
    f"{local_timestamp()} · "
    f"Yanıt dili: {st.session_state.language}"
)

st.divider()


# =========================================================
#  SPECIAL MODULE INTERFACES
# =========================================================

if st.session_state.module == "🎓 Üniversite Araştırmaları":
    st.subheader("🌍 Üniversiteleri keşfet")

    university = st.selectbox(
        "Araştırmak istediğin üniversite",
        list(UNIVERSITIES.keys()),
    )

    st.markdown(
        f"**Resmî başvuru sayfası:** "
        f"[{university}]({UNIVERSITIES[university]})"
    )

    grades = st.text_area(
        "Notların ve akademik durumun",
        placeholder="Ders notları, sınıf düzeyi, beklenen mezuniyet yılı...",
    )

    exams = st.text_area(
        "Sınavlar ve dil düzeyi",
        placeholder="SAT/ACT, IELTS/TOEFL veya sınavlara erişim durumun...",
    )

    interests = st.text_area(
        "İlgi alanların ve projelerin",
        placeholder="Projeler, kitaplar, araştırmalar, yarışmalar...",
    )

    if st.button("🎓 Profilimi yayımlanmış koşullarla karşılaştır"):
        query = f"""
        {university} için resmî lisans başvuru koşullarını araştır.
        Kullanıcı profili:
        Notlar: {grades}
        Sınavlar ve dil düzeyi: {exams}
        İlgi alanları ve projeler: {interests}

        Resmî kaynaklarla doğrulanabilen koşulları, eksik bilgileri,
        sınav gerekliliklerini, son başvuru tarihlerini ve finansal
        yardım seçeneklerini ayrı başlıklarla açıkla.
        Kabul garantisi veya kesin kabul olasılığı verme.
        """

        with st.spinner("Üniversite bilgileri araştırılıyor..."):
            result = web_search(query)

        st.markdown(result)

    st.info(
        "Üniversite bilgileri başvuru yılına göre değişebilir. "
        "Son karar için resmî üniversite sayfasını kontrol et."
    )


elif st.session_state.module == "🎨 Görsel Atölyesi":
    st.subheader("🎨 Görsel oluştur")

    image_prompt = st.text_area(
        "Oluşturmak istediğin görseli tarif et",
        placeholder=(
            "Örn. İnsan hücresinin bilimsel, etiketli ve "
            "eğitim amaçlı illüstrasyonu..."
        ),
        height=120,
    )

    if st.button("🖼️ Görsel üret", use_container_width=True):
        if not image_prompt.strip():
            st.warning("Önce görselini tarif et.")
        else:
            with st.spinner("Görsel hazırlanıyor..."):
                image_bytes, error = generate_image(image_prompt)

            if error:
                st.error(error)
            elif image_bytes:
                st.image(image_bytes, caption="Lidya AI tarafından oluşturuldu")
                st.download_button(
                    "Görseli indir",
                    data=image_bytes,
                    file_name="lidya_gorsel.png",
                    mime="image/png",
                )


elif st.session_state.module == "🎤 Karaoke ve Ses":
    st.subheader("🎤 Ses laboratuvarı")

    st.write(
        "Bir ses kaydı yükleyerek konuşma transkripsiyonu "
        "veya telaffuz çalışması yapabilirsin."
    )

    audio_file = st.file_uploader(
        "Ses kaydı yükle",
        type=["wav", "mp3", "m4a", "ogg", "webm"],
        key="karaoke_audio_upload",
    )

    if audio_file:
        st.audio(audio_file)

        if st.button("📝 Sesimi yazıya çevir"):
            with st.spinner("Ses çözümleniyor..."):
                transcript = transcribe_audio(audio_file)

            st.session_state.last_audio_text = transcript
            st.text_area(
                "Ses kaydının metni",
                value=transcript,
                height=150,
            )

    if st.session_state.last_audio_text:
        st.caption(
            "İstersen aşağıdaki sohbet alanına metni ekleyip "
            "telaffuz, anlatım veya dil bilgisi değerlendirmesi iste."
        )

    st.warning(
        "Bu sürüm, StarMaker gibi lisanslı şarkı kataloğu veya "
        "gerçek zamanlı perde/ritim ölçümü sunmaz. Mikrofon kaydı "
        "ve metin çözümleme altyapısının erişilebilirliğine bağlıdır."
    )


elif st.session_state.module == "➗ Matematik ve TYT/AYT/SAT":
    st.subheader("➗ Matematik çalışma alanı")

    math_topic = st.selectbox(
        "Konu",
        [
            "Konu seçmedim",
            "Temel işlemler",
            "Kesirler ve oran-orantı",
            "Cebir",
            "Denklemler",
            "Fonksiyonlar",
            "Geometri",
            "Trigonometri",
            "Olasılık ve istatistik",
            "TYT matematik",
            "AYT matematik",
            "SAT matematik",
            "Cambridge matematik",
        ],
    )

    if math_topic != "Konu seçmedim":
        st.caption(f"Seçilen konu: {math_topic}")

    st.write(
        "Sorunu aşağıdaki mesaj alanına yazabilir veya "
        "fotoğrafını ekleyebilirsin. Çözümü adım adım isteyebilirsin."
    )


elif st.session_state.module == "🏛️ Tarih":
    st.write(
        "Tarihî bir olay, dönem, kişi veya kaynak hakkında "
        "soru sorabilirsin. Güncel tarih araştırmalarında "
        "kaynak istemeyi unutma."
    )


# =========================================================
#  CHAT HISTORY
# =========================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("timestamp"):
            st.caption("🕒 " + message["timestamp"])


# =========================================================
#  UNIVERSAL FILE ATTACHMENT + CHAT INPUT
# =========================================================

prompt_value = st.chat_input(
    "Lidya'ya bir şey sor...",
    accept_file="multiple",
    file_type=[
        "pdf",
        "docx",
        "txt",
        "md",
        "csv",
        "json",
        "png",
        "jpg",
        "jpeg",
        "webp",
    ],
)

if prompt_value is not None:
    if hasattr(prompt_value, "text"):
        user_text = prompt_value.text or ""
        uploaded_files = list(getattr(prompt_value, "files", []) or [])
    else:
        user_text = str(prompt_value)
        uploaded_files = []

    if not user_text.strip() and not uploaded_files:
        st.stop()

    timestamp = local_timestamp()
    attachment_descriptions = []
    text_attachments = []
    image_attachments = []

    for uploaded_file in uploaded_files:
        try:
            extracted_text, image_data = process_uploaded_file(uploaded_file)

            if image_data:
                image_attachments.append(image_data)
                attachment_descriptions.append(
                    f"🖼️ Görsel eklendi: {uploaded_file.name}"
                )

            elif extracted_text:
                text_attachments.append({
                    "name": uploaded_file.name,
                    "text": extracted_text,
                })
                attachment_descriptions.append(
                    f"📎 Dosya eklendi: {uploaded_file.name}"
                )

        except Exception as e:
            attachment_descriptions.append(
                f"⚠️ {uploaded_file.name} okunamadı: {str(e)[:200]}"
            )

    displayed_user_text = user_text.strip() or "Eklediğim dosyaları incele."

    if attachment_descriptions:
        displayed_user_text += "\n\n" + "\n".join(attachment_descriptions)

    st.session_state.messages.append({
        "role": "user",
        "content": displayed_user_text,
        "timestamp": timestamp,
    })

    with st.chat_message("user"):
        st.markdown(displayed_user_text)
        st.caption("🕒 " + timestamp)

    with st.chat_message("assistant"):
        with st.spinner("Lidya düşünüyor..."):
            if image_attachments:
                answers = []

                for image_data in image_attachments:
                    answers.append(
                        analyze_image(
                            user_text or "Bu görseli ayrıntılı incele.",
                            image_data,
                            st.session_state.language,
                            st.session_state.module,
                        )
                    )

                if text_attachments:
                    text_answer = answer_with_groq(
                        user_text or "Eklediğim dosyaları incele.",
                        st.session_state.module,
                        st.session_state.language,
                        st.session_state.memory,
                        text_attachments,
                    )
                    answers.append(text_answer)

                answer = "\n\n---\n\n".join(answers)

            else:
                answer = answer_with_groq(
                    user_text or "Eklediğim dosyaları incele.",
                    st.session_state.module,
                    st.session_state.language,
                    st.session_state.memory,
                    text_attachments,
                )

        st.markdown(answer)

        assistant_timestamp = local_timestamp()
        st.caption("🕒 " + assistant_timestamp)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "timestamp": assistant_timestamp,
    })


# =========================================================
#  FOOTER
# =========================================================

st.divider()

st.caption(
    "💜 Lidya AI — Düşün. Öğren. Üret. Keşfet. "
    "Built with curiosity and Python."
)

st.caption(
    "Gizlilik notu: Bu sürüm sohbeti oturum içinde tutar. "
    "Kalıcı ve kullanıcılar arasında ayrılmış hafıza için "
    "kimlik doğrulama ve güvenli bir veritabanı gerekir."
    )

import os, io, json, math
from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import matplotlib.pyplot as plt
from groq import Groq
from pypdf import PdfReader
from docx import Document

st.set_page_config(page_title="Lidya AI", page_icon="💜", layout="wide")
MODEL_NAME = "openai/gpt-oss-20b"
LANGUAGES = {"Türkçe":"Turkish", "English":"English", "Français":"French", "Deutsch":"German", "Español":"Spanish", "Italiano":"Italian", "日本語":"Japanese"}
WORKSPACES = {
    "💜 Lidya": ("Genel Asistan", "Sohbet, fikir geliştirme ve günlük üretkenlik."),
    "📁 Dosya Laboratuvarı": ("Dosya Laboratuvarı", "Desteklenen belgeleri sohbet kutusuna ekle; metinlerini özetle, açıkla ve analiz et."),
    "🔎 Araştırma": ("Araştırma Laboratuvarı", "Araştırma soruları, kanıt analizi ve rapor planları."),
    "📚 Eğitim": ("Öğrenme Tasarımı", "Konu anlatımı, çalışma planları ve quizler."),
    "✍️ Yazma": ("Yazı ve Yaratıcılık", "Özgün yazılar, düzenleme, hikâye ve sunumlar."),
    "💻 Yazılım": ("Yazılım Mühendisliği", "Kod yazma, hata ayıklama ve proje mimarisi."),
    "📐 Matematik": ("Matematik Laboratuvarı", "Çözümler, grafikler ve etkileşimli matematik deneyleri."),
    "🔬 Bilim": ("Bilim ve Araştırma", "Bilimsel kavramlar, deney tasarımı ve modeller."),
    "🩺 Tıp ve Anatomi": ("Tıp ve Anatomi", "Anatomi ve tıp konularını eğitim amaçlı açıklama."),
    "🌍 Dil Öğretmeni": ("Dil Öğretmeni", "Kelime, dil bilgisi, yazma ve dil pratiği."),
    "⚖️ Hukuk": ("Hukuk Araştırmaları", "Genel hukuki kavramlar ve araştırma desteği."),
    "⚙️ Mühendislik": ("Mühendislik", "Mühendislik prensipleri, modeller ve hesaplamalar."),
    "📊 Veri Analizi": ("Veri Analizi", "Veri yorumlama ve grafikler."),
    "💼 İşletme ve Ekonomi": ("İşletme ve Ekonomi", "İşletme, girişimcilik, ekonomi ve finansal kavramlar."),
    "🔐 Siber Güvenlik": ("Siber Güvenlik", "Güvenli yazılım, gizlilik ve savunma odaklı çalışmalar."),
    "🏠 Akıllı Cihazlar": ("Akıllı Cihazlar", "IoT tasarımı ve güvenli cihaz entegrasyonu planlama."),
    "🎨 Görsel Atölyesi": ("Görsel Atölyesi", "Görsel konsept ve üretim araçları için ayrıntılı istemler."),
    "🎬 Video Atölyesi": ("Lidya Motion Studio", "Konsept, senaryo, storyboard ve video üretim planı."),
}
MODULE_LABELS = {
    "Türkçe": {},
    "English": {
        "📁 Dosya Laboratuvarı":"📁 File Laboratory", "🔎 Araştırma":"🔎 Research",
        "📚 Eğitim":"📚 Education", "✍️ Yazma":"✍️ Writing & Creativity",
        "💻 Yazılım":"💻 Software Engineering", "📐 Matematik":"📐 Mathematics",
        "🔬 Bilim":"🔬 Science & Research", "🩺 Tıp ve Anatomi":"🩺 Medical & Anatomy",
        "🌍 Dil Öğretmeni":"🌍 Language Teacher", "⚖️ Hukuk":"⚖️ Legal Research",
        "⚙️ Mühendislik":"⚙️ Engineering", "📊 Veri Analizi":"📊 Data Analysis",
        "💼 İşletme ve Ekonomi":"💼 Business & Economics", "🔐 Siber Güvenlik":"🔐 Cybersecurity",
        "🏠 Akıllı Cihazlar":"🏠 Smart Devices", "🎨 Görsel Atölyesi":"🎨 Image Studio",
        "🎬 Video Atölyesi":"🎬 Video Studio", "💜 Lidya":"💜 Lidya AI", "⚙️ Ayarlar":"⚙️ Settings"
    },
    "Français": {"📁 Dosya Laboratuvarı":"📁 Laboratoire de fichiers", "🔎 Araştırma":"🔎 Recherche", "📚 Eğitim":"📚 Éducation", "✍️ Yazma":"✍️ Écriture", "💻 Yazılım":"💻 Développement logiciel", "📐 Matematik":"📐 Mathématiques", "🔬 Bilim":"🔬 Sciences", "🩺 Tıp ve Anatomi":"🩺 Médecine et anatomie", "🌍 Dil Öğretmeni":"🌍 Professeur de langues", "⚖️ Hukuk":"⚖️ Droit", "⚙️ Mühendislik":"⚙️ Ingénierie", "📊 Veri Analizi":"📊 Analyse de données", "💼 İşletme ve Ekonomi":"💼 Économie et gestion", "🔐 Siber Güvenlik":"🔐 Cybersécurité", "🏠 Akıllı Cihazlar":"🏠 Appareils connectés", "🎨 Görsel Atölyesi":"🎨 Studio d’images", "🎬 Video Atölyesi":"🎬 Studio vidéo", "💜 Lidya":"💜 Lidya", "⚙️ Ayarlar":"⚙️ Paramètres"},
    "Deutsch": {"📁 Dosya Laboratuvarı":"📁 Dateilabor", "🔎 Araştırma":"🔎 Recherche", "📚 Eğitim":"📚 Bildung", "✍️ Yazma":"✍️ Schreiben", "💻 Yazılım":"💻 Softwareentwicklung", "📐 Matematik":"📐 Mathematik", "🔬 Bilim":"🔬 Wissenschaft", "🩺 Tıp ve Anatomi":"🩺 Medizin und Anatomie", "🌍 Dil Öğretmeni":"🌍 Sprachlehrer", "⚖️ Hukuk":"⚖️ Recht", "⚙️ Mühendislik":"⚙️ Ingenieurwesen", "📊 Veri Analizi":"📊 Datenanalyse", "💼 İşletme ve Ekonomi":"💼 Wirtschaft", "🔐 Siber Güvenlik":"🔐 Cybersicherheit", "🏠 Akıllı Cihazlar":"🏠 Smartgeräte", "🎨 Görsel Atölyesi":"🎨 Bildstudio", "🎬 Video Atölyesi":"🎬 Videostudio", "💜 Lidya":"💜 Lidya", "⚙️ Ayarlar":"⚙️ Einstellungen"},
    "Español": {"📁 Dosya Laboratuvarı":"📁 Laboratorio de archivos", "🔎 Araştırma":"🔎 Investigación", "📚 Eğitim":"📚 Educación", "✍️ Yazma":"✍️ Escritura", "💻 Yazılım":"💻 Ingeniería de software", "📐 Matematik":"📐 Matemáticas", "🔬 Bilim":"🔬 Ciencia", "🩺 Tıp ve Anatomi":"🩺 Medicina y anatomía", "🌍 Dil Öğretmeni":"🌍 Profesor de idiomas", "⚖️ Hukuk":"⚖️ Derecho", "⚙️ Mühendislik":"⚙️ Ingeniería", "📊 Veri Analizi":"📊 Análisis de datos", "💼 İşletme ve Ekonomi":"💼 Economía y negocios", "🔐 Siber Güvenlik":"🔐 Ciberseguridad", "🏠 Akıllı Cihazlar":"🏠 Dispositivos inteligentes", "🎨 Görsel Atölyesi":"🎨 Estudio de imagen", "🎬 Video Atölyesi":"🎬 Estudio de vídeo", "💜 Lidya":"💜 Lidya", "⚙️ Ayarlar":"⚙️ Ajustes"},
    "Italiano": {"📁 Dosya Laboratuvarı":"📁 Laboratorio file", "🔎 Araştırma":"🔎 Ricerca", "📚 Eğitim":"📚 Istruzione", "✍️ Yazma":"✍️ Scrittura", "💻 Yazılım":"💻 Ingegneria software", "📐 Matematik":"📐 Matematica", "🔬 Bilim":"🔬 Scienza", "🩺 Tıp ve Anatomi":"🩺 Medicina e anatomia", "🌍 Dil Öğretmeni":"🌍 Insegnante di lingue", "⚖️ Hukuk":"⚖️ Diritto", "⚙️ Mühendislik":"⚙️ Ingegneria", "📊 Veri Analizi":"📊 Analisi dei dati", "💼 İşletme ve Ekonomi":"💼 Economia e impresa", "🔐 Siber Güvenlik":"🔐 Sicurezza informatica", "🏠 Akıllı Cihazlar":"🏠 Dispositivi smart", "🎨 Görsel Atölyesi":"🎨 Studio immagini", "🎬 Video Atölyesi":"🎬 Studio video", "💜 Lidya":"💜 Lidya", "⚙️ Ayarlar":"⚙️ Impostazioni"},
    "日本語": {"📁 Dosya Laboratuvarı":"📁 ファイルラボ", "🔎 Araştırma":"🔎 リサーチ", "📚 Eğitim":"📚 学習", "✍️ Yazma":"✍️ 文章と創作", "💻 Yazılım":"💻 ソフトウェア開発", "📐 Matematik":"📐 数学", "🔬 Bilim":"🔬 科学研究", "🩺 Tıp ve Anatomi":"🩺 医学と解剖学", "🌍 Dil Öğretmeni":"🌍 言語学習", "⚖️ Hukuk":"⚖️ 法律研究", "⚙️ Mühendislik":"⚙️ 工学", "📊 Veri Analizi":"📊 データ分析", "💼 İşletme ve Ekonomi":"💼 経済とビジネス", "🔐 Siber Güvenlik":"🔐 サイバーセキュリティ", "🏠 Akıllı Cihazlar":"🏠 スマートデバイス", "🎨 Görsel Atölyesi":"🎨 画像スタジオ", "🎬 Video Atölyesi":"🎬 動画スタジオ", "💜 Lidya":"💜 Lidya", "⚙️ Ayarlar":"⚙️ 設定"},
}
GUIDANCE = {
    "📁 Dosya Laboratuvarı":"Ekli desteklenen dosyanın çıkarılmış metnini analiz et; dosyanın içeriği gelmediyse bunu açıkça söyle.",
    "💼 İşletme ve Ekonomi":"İş ve ekonomi kavramlarını açıkla; finansal sonuçları garanti etme.",
    "🔎 Araştırma":"Kaynak uydurma. Bu sürümde canlı web araması bağlı değil; güncel kaynak gerekiyorsa bunu açıkça belirt ve doğrulama stratejisi öner.",
    "📐 Matematik":"İşlemleri kontrol et, sembolleri tanımla ve çözümü adım adım açıkla.",
    "🩺 Tıp ve Anatomi":"Eğitim amaçlı bilgi ver. Kişisel teşhis veya tedavi kararı verme; önemli durumlarda sağlık uzmanına yönlendir.",
    "⚖️ Hukuk":"Genel bilgi ver; kesin hukuki tavsiye iddiasında bulunma. Yargı alanı önemliyse sor.",
    "🔐 Siber Güvenlik":"Savunma odaklı ve izinli öneriler ver.",
    "🏠 Akıllı Cihazlar":"Bu uygulama fiziksel cihazları doğrudan kontrol etmez. Kontrol etmiş gibi konuşma.",
    "🎨 Görsel Atölyesi":"Kompozisyon, ışık, malzeme, kamera, renk paleti ve kaçınılacak öğeleri ayrıntılandır.",
    "🎬 Video Atölyesi":"Yaratıcı yönetmen gibi davran. Gerçek video dosyası oluşturulmadıysa oluşturulmuş gibi söyleme.",
}

def secret(name, default=""):
    try:
        v = st.secrets.get(name, default)
        return str(v) if v else default
    except Exception:
        return os.environ.get(name, default)

@st.cache_resource
def make_client(key):
    return Groq(api_key=key, timeout=60, max_retries=1) if key else None

client = make_client(secret("GROQ_API_KEY"))
DEFAULTS = {"interface_language":"Türkçe", "theme_choice":"Gece moru", "response_style":"Dengeli", "response_length":"Orta", "voice_output":False, "show_timestamps":True, "messages_by_workspace":{}, "last_answer":"", "video_pack":"", "selected_page":"💜 Lidya"}
for k,v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

def now_tr(): return datetime.now(ZoneInfo("Europe/Istanbul")).strftime("%d.%m.%Y %H:%M")
def msgs(page): return st.session_state.messages_by_workspace.setdefault(page, [])
def clear_page(page): st.session_state.messages_by_workspace[page] = []

def extract_file(f):
    name, raw = f.name.lower(), f.getvalue()
    try:
        if name.endswith((".txt", ".md", ".py", ".json", ".csv")): return raw.decode("utf-8", errors="replace")[:16000]
        if name.endswith(".pdf"):
            return "\n\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(raw)).pages)[:16000]
        if name.endswith(".docx"):
            return "\n".join(p.text for p in Document(io.BytesIO(raw)).paragraphs)[:16000]
    except Exception as e: return f"[Dosya okunamadı: {type(e).__name__}]"
    return "[Desteklenmeyen dosya türü. PDF, DOCX, TXT, MD, CSV, JSON veya PY kullan.]"

def system_prompt(page):
    title, purpose = WORKSPACES[page]
    return f"""You are Lidya AI, an educational and productivity assistant project developed by Şeymanur Acun. You are currently in {title}: {purpose}. Reply in {LANGUAGES[st.session_state.interface_language]} unless asked otherwise. Style: {st.session_state.response_style}. Length: {st.session_state.response_length}. {GUIDANCE.get(page, '')} Be accurate, original, practical and clear. Never invent citations, web searches, completed actions or capabilities. Live web browsing is not connected in this version. If asked who developed the Lidya AI project, say Şeymanur Acun; do not claim she created the underlying AI model. Never ask for API keys or passwords."""

def ask_model(page, prompt, history):
    if not client: return None, "Yanıt motoru yapılandırılmamış. Uygulama sahibi Streamlit Cloud → Settings → Secrets bölümünde GROQ_API_KEY tanımlamalı."
    messages = [{"role":"system", "content":system_prompt(page)}]
    for m in history[-10:]:
        if m.get("role") in ("user", "assistant") and m.get("content"):
            messages.append({"role":m["role"], "content":m["content"][:8000]})
    messages.append({"role":"user", "content":prompt[:18000]})
    try:
        r = client.chat.completions.create(model=MODEL_NAME, messages=messages, temperature=.55, max_completion_tokens=2200)
        answer = r.choices[0].message.content
        return (answer, None) if answer else (None, "Model boş yanıt döndürdü. Tekrar dene.")
    except Exception as e: return None, f"Yanıt oluşturulamadı ({type(e).__name__}). Model erişimini ve kullanım kotasını kontrol et."

def draw_chat(page):
    history = msgs(page)
    if not history:
        with st.chat_message("assistant", avatar="💜"):
            st.markdown("Merhaba! Ben Lidya AI, eğitim ve üretkenlik asistanınızım. Size nasıl yardımcı olabilirim?")
            st.caption("Düşün. Öğren. Üret. Keşfet.")
    for m in history:
        with st.chat_message(m["role"], avatar="💜" if m["role"] == "assistant" else "🧑‍💻"):
            st.markdown(m["content"])
            if st.session_state.show_timestamps and m.get("time"): st.caption(m["time"])

def process_chat(page, value):
    text = (value.text or "").strip(); file_bits=[]; filenames=[]
    for f in value.files:
        filenames.append(f.name); n=f.name.lower()
        if n.endswith((".pdf", ".docx", ".txt", ".md", ".csv", ".json", ".py")):
            file_bits.append(f"\n\n[Ekli dosya: {f.name}]\n{extract_file(f)}")
        elif n.endswith((".png", ".jpg", ".jpeg", ".webp")):
            file_bits.append(f"\n\n[Ekli görsel: {f.name}. Bu sürümde görsel piksel analizi bağlı değil; görseldeki ayrıntıları yazabilirsin.]")
        else: file_bits.append(f"\n\n[Ekli dosya: {f.name}; desteklenmeyen dosya türü.]")
    prompt = text + ("\n\nEkli dosya içerikleri:\n" + "\n".join(file_bits) if file_bits else "")
    if not prompt.strip(): st.warning("Bir mesaj yaz veya desteklenen bir dosya ekle."); return
    shown = text or "Ekli dosyayı incele."
    if filenames: shown += "\n\n📎 " + ", ".join(filenames)
    history = list(msgs(page)); msgs(page).append({"role":"user", "content":shown, "time":now_tr()})
    with st.spinner("Lidya düşünüyor…"): answer, error = ask_model(page, prompt, history)
    if error: st.error(error)
    else:
        msgs(page).append({"role":"assistant", "content":answer, "time":now_tr()})
        st.session_state.last_answer = answer
    st.rerun()

# Theme styling
if st.session_state.theme_choice == "Aydınlık": bg="linear-gradient(145deg,#f7f3ff,#edf5ff)"; panel="rgba(255,255,255,.92)"; border="#d8cbed"
else: bg="radial-gradient(circle at 15% 0%,#35214f 0%,#171326 44%,#090912 100%)"; panel="rgba(255,255,255,.055)"; border="rgba(204,173,255,.20)"
st.markdown(f"""<style>
.stApp{{background:{bg};}} [data-testid="stSidebar"]{{background:rgba(13,11,27,.96);border-right:1px solid {border};}}
.lidya-hero{{padding:12px 10px;text-align:center}} .lidya-wordmark{{font-size:clamp(34px,6vw,58px);font-weight:900;letter-spacing:.13em;background:linear-gradient(90deg,#f7d8ff,#b89aff,#8ae9ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.lidya-tagline{{color:#d9c9f5;font-size:16px}} .lidya-orb{{width:58px;height:58px;margin:14px auto;border-radius:50%;background:radial-gradient(circle at 30% 25%,#fff,#e2b5ff 18%,#9258ef 45%,#3a1c6e 76%);box-shadow:0 0 28px #8d5bea;animation:float 4s ease-in-out infinite}}
@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-7px)}}}} [data-testid="stChatMessage"]{{background:{panel};border:1px solid {border};border-radius:17px}} .stButton>button{{border-radius:12px}} footer{{visibility:hidden}}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 💜 Lidya AI"); st.caption("Düşün. Öğren. Üret. Keşfet.")
    page_options=list(WORKSPACES.keys())+["⚙️ Ayarlar"]
    labels = MODULE_LABELS.get(st.session_state.interface_language, {})
    page=st.radio("Çalışma alanları", page_options, key="selected_page", format_func=lambda item: labels.get(item, item))
    st.divider(); st.checkbox("Yanıtları sesli oku", key="voice_output"); st.checkbox("Mesajlarda Türkiye saatini göster", key="show_timestamps")
    if st.button("🧹 Bu alanın sohbetini temizle", use_container_width=True):
        if page in WORKSPACES: clear_page(page)
        st.session_state.last_answer=""; st.rerun()
    st.caption("Bağımsız eğitim ve üretkenlik projesi.")

st.markdown('<div class="lidya-hero"><div class="lidya-wordmark">LIDYA AI</div><div class="lidya-tagline">Düşün. Öğren. Üret. Keşfet.</div><div class="lidya-orb"></div></div>', unsafe_allow_html=True)

if page == "⚙️ Ayarlar":
    st.title("⚙️ Ayarlar"); st.write("Lidya'nın seninle nasıl çalışacağını kişiselleştir.")
    st.selectbox("Tema", ["Gece moru", "Aydınlık"], key="theme_choice")
    st.selectbox("Arayüz ve yanıt dili", list(LANGUAGES.keys()), key="interface_language")
    st.selectbox("Yanıt tarzı", ["Dengeli", "Kısa ve doğrudan", "Ayrıntılı ve öğretici", "Yaratıcı"], key="response_style")
    st.selectbox("Yanıt uzunluğu", ["Kısa", "Orta", "Uzun"], key="response_length")
    st.info("API anahtarları arayüzde gösterilmez. Streamlit Cloud → Settings → Secrets bölümünde saklanmalıdır.")
    st.caption("Ayarlar bu oturum boyunca geçerlidir. Kalıcı kullanıcı hesabı ve cihazlar arası eşitleme bu sürümde yoktur.")
    if st.button("🧹 Tüm sohbetleri temizle"):
        st.session_state.messages_by_workspace={}; st.session_state.last_answer=""; st.rerun()

elif page == "📐 Matematik":
    st.title("📐 Matematik Laboratuvarı"); st.write("Parametreleri değiştir, grafiği incele ve davranışını keşfet.")
    exp=st.selectbox("Etkileşimli deney", ["Fonksiyon kaşifi", "İkinci derece denklem", "Atış hareketi", "Dairesel hareket", "Dalga modeli"])
    if exp == "Fonksiyon kaşifi":
        c1,c2,c3=st.columns(3); a=c1.slider("a katsayısı",-5.0,5.0,1.0,.1); b=c2.slider("b katsayısı",-10.0,10.0,0.0,.5); c=c3.slider("c katsayısı",-10.0,10.0,0.0,.5); span=st.slider("x ekseni aralığı",3,20,10)
        x=np.linspace(-span,span,500); y=a*x*x+b*x+c; fig,ax=plt.subplots(); ax.plot(x,y); ax.axhline(0,linewidth=.8); ax.axvline(0,linewidth=.8); ax.set_title(f"f(x) = {a:g}x² + {b:g}x + {c:g}"); ax.set_xlabel("x"); ax.set_ylabel("f(x)"); ax.grid(True,alpha=.25); st.pyplot(fig,use_container_width=True)
        st.caption("a parabolün yönünü ve genişliğini; b ve c şeklini ve konumunu etkiler.")
    elif exp == "İkinci derece denklem":
        c1,c2,c3=st.columns(3); a=c1.number_input("a",value=1.0,step=.5); b=c2.number_input("b",value=-3.0,step=.5); c=c3.number_input("c",value=2.0,step=.5)
        if abs(a)<1e-12: st.warning("a = 0 olduğunda denklem ikinci derece değildir.")
        else:
            d=b*b-4*a*c; st.metric("Diskriminant Δ",f"{d:.4g}")
            if d>0: st.success(f"İki gerçek kök: x₁ = {(-b+math.sqrt(d))/(2*a):.5g}, x₂ = {(-b-math.sqrt(d))/(2*a):.5g}")
            elif abs(d)<1e-12: st.success(f"Çakışık gerçek kök: x = {-b/(2*a):.5g}")
            else: st.info("Gerçek kök yok; iki karmaşık kök vardır.")
    elif exp == "Atış hareketi":
        v=st.slider("İlk hız (m/s)",5,50,25); deg=st.slider("Atış açısı (derece)",5,85,45); g=9.81; th=math.radians(deg); tmax=2*v*math.sin(th)/g; t=np.linspace(0,tmax,300); x=v*math.cos(th)*t; y=v*math.sin(th)*t-.5*g*t*t
        fig,ax=plt.subplots(); ax.plot(x,y); ax.set_title("İdeal atış yörüngesi (hava direnci yok)"); ax.set_xlabel("Yatay mesafe (m)"); ax.set_ylabel("Yükseklik (m)"); ax.grid(True,alpha=.25); st.pyplot(fig,use_container_width=True); st.metric("İdeal menzil",f"{v*v*math.sin(2*th)/g:.2f} m")
    elif exp == "Dairesel hareket":
        r=st.slider("Yarıçap (m)",1,20,5); period=st.slider("Bir tur süresi (s)",1,30,8); t=st.slider("Zaman (s)",0.0,float(period),2.0,.1); w=2*math.pi/period; theta=w*t; ang=np.linspace(0,2*math.pi,300); fig,ax=plt.subplots(); ax.plot(r*np.cos(ang),r*np.sin(ang)); ax.scatter([r*math.cos(theta)],[r*math.sin(theta)]); ax.set_aspect("equal",adjustable="box"); ax.grid(True,alpha=.25); ax.set_title("Dairesel hareket"); st.pyplot(fig,use_container_width=True); st.write(f"Açısal hız: **{w:.3f} rad/s** · Çizgisel hız: **{r*w:.3f} m/s**")
    else:
        amp=st.slider("Genlik",.1,5.0,1.5,.1); freq=st.slider("Frekans parametresi",.1,3.0,1.0,.1); phase=st.slider("Faz (radyan)",0.0,6.28,0.0,.1); x=np.linspace(0,4*np.pi,500); y=amp*np.sin(freq*x+phase); fig,ax=plt.subplots(); ax.plot(x,y); ax.set_title("y = A sin(kx + φ)"); ax.set_xlabel("Konum"); ax.set_ylabel("Genlik"); ax.grid(True,alpha=.25); st.pyplot(fig,use_container_width=True)
    st.divider(); st.subheader("Lidya ile matematik"); draw_chat(page)
    value=st.chat_input("Matematik sorunu yaz veya dosya ekle…",accept_file="multiple",file_type=["pdf","docx","txt","md","csv","json","py"])
    if value: process_chat(page,value)

elif page == "🎬 Video Atölyesi":
    st.title("🎬 Lidya Motion Studio"); st.write("Fikrini konseptten storyboard'a ve uygulanabilir yapım planına dönüştür.")
    st.info("Bu alan senaryo ve üretim paketi hazırlar. Bağlı bir video üretim servisi olmadan gerçek video dosyası oluşturmaz.")
    with st.form("video_form"):
        concept=st.text_area("Video fikri",placeholder="Örn. insan hücresinin içinde geçen sinematik bir yolculuk…",height=100)
        c1,c2,c3=st.columns(3); duration=c1.selectbox("Süre",["15 saniye","30 saniye","60 saniye","90 saniye","2 dakika"]); ratio=c2.selectbox("Kadraj",["16:9 sinematik","9:16 dikey","1:1 kare"]); style=c3.selectbox("Görsel dil",["Bilimsel sinema","Belgesel","Animasyon","Minimal ve şiirsel","Fütüristik","Eğitici kısa video"])
        audience=st.text_input("Hedef izleyici",value="Meraklı öğrenciler ve genel izleyici"); purpose=st.selectbox("Yayın amacı",["Eğitim","YouTube","Reels / Shorts","Proje sunumu","Portfolyo"]); submit=st.form_submit_button("✨ Yapım paketini oluştur",use_container_width=True)
    if submit:
        if not concept.strip(): st.warning("Önce video fikrini yaz.")
        elif not client: st.error("Uygulama sahibi Secrets bölümünde GROQ_API_KEY tanımlamalı.")
        else:
            prompt=f"""Bu fikir için özgün ve uygulanabilir Türkçe video yapım paketi üret. Fikir: {concept}. Süre: {duration}; kadraj: {ratio}; görsel dil: {style}; hedef: {audience}; amaç: {purpose}. Bölümler: 1) Başlık ve logline. 2) Yaratıcı fikir. 3) Zaman kodlu storyboard: görüntü, kamera, ses, ekrandaki yazı. 4) Anlatıcı metni. 5) Renk/ışık/ses tasarımı. 6) Her sahne için ayrı İngilizce video istemi. 7) Negatif istem ve kaçınılacak hatalar. 8) Montaj ve erişilebilirlik. 9) Bilimsel konuysa doğruluk kontrol listesi. Süreye uygun sahne sayısı seç. Gerçek video dosyası oluşturduğunu söyleme."""
            with st.spinner("Lidya yaratıcı yapım paketini hazırlıyor…"):
                try:
                    r=client.chat.completions.create(model=MODEL_NAME,messages=[{"role":"system","content":"You are an award-calibre creative director, storyboard artist and educational film producer. Be original, specific and practical."},{"role":"user","content":prompt}],temperature=.8,max_completion_tokens=3500)
                    st.session_state.video_pack=r.choices[0].message.content or ""
                except Exception as e: st.error(f"Paket oluşturulamadı ({type(e).__name__}). Model erişimini ve kotayı kontrol et.")
    if st.session_state.video_pack:
        st.markdown("### 🎞️ Yapım paketin"); st.markdown(st.session_state.video_pack); st.download_button("⬇️ Paketi TXT olarak indir",st.session_state.video_pack,file_name="lidya_video_yapim_paketi.txt",mime="text/plain")
    st.divider(); st.subheader("Lidya ile fikir geliştirme"); draw_chat(page)
    value=st.chat_input("Video fikrini Lidya ile geliştir…",accept_file="multiple",file_type=["pdf","docx","txt","md"])
    if value: process_chat(page,value)

else:
    title,desc=WORKSPACES[page]; st.title(title); st.write(desc)
    if page=="🩺 Tıp ve Anatomi": st.info("Eğitim amaçlıdır; tanı veya tedavi kararlarının yerini tutmaz.")
    if page=="🔎 Araştırma": st.caption("Canlı web araması bu sürümde bağlı değil. Lidya araştırma planı ve analiz hazırlayabilir; güncel kaynakları doğruladığını iddia etmez.")
    if page=="📁 Dosya Laboratuvarı":
        st.caption("Dosyanı aşağıdaki sohbet kutusundaki ekleme simgesiyle yükleyebilirsin. PDF, DOCX, TXT, MD, CSV, JSON ve PY dosyalarından metin çıkarılır.")
    if page=="🎨 Görsel Atölyesi":
        st.markdown("**Görsel konsept laboratuvarı**")
        with st.form("image_prompt_form"):
            subject=st.text_area("Ne oluşturmak istiyorsun?", placeholder="Örn. insan kalbi anatomik illüstrasyonu; bilimsel doğruluk, net etiket alanları…", height=90)
            col1,col2,col3=st.columns(3)
            medium=col1.selectbox("Tür", ["Bilimsel illüstrasyon", "Dijital sanat", "Editoryal çizim", "3D render", "Poster"])
            framing=col2.selectbox("Kompozisyon", ["Merkezî", "Yakın plan", "Kesit görünümü", "İnfografik", "Sinematik geniş plan"])
            look=col3.selectbox("Stil", ["Temiz ve gerçekçi", "Minimal", "Sinematik", "El çizimi", "Fotogerçekçi"])
            avoid=st.text_input("Kaçınılacaklar", value="yazım hataları, bozuk anatomi, anlamsız etiketler, watermark")
            make_prompt=st.form_submit_button("✨ Görsel üretim istemini hazırla", use_container_width=True)
        if make_prompt:
            if not subject.strip(): st.warning("Önce görsel fikrini yaz.")
            elif not client: st.error("İstem hazırlamak için GROQ_API_KEY yapılandırılmalı.")
            else:
                prompt=f"Görsel üretim aracı için ayrıntılı, uygulanabilir bir İNGİLİZCE prompt ve ayrı bir negative prompt hazırla. Konu: {subject}. Tür: {medium}. Kompozisyon: {framing}. Stil: {look}. Kaçınılacaklar: {avoid}. Işık, kamera/açı, malzeme, renk paleti, arka plan, detay düzeyi ve bilimsel doğruluk ölçütlerini ekle. Görseli gerçekten ürettiğini iddia etme."
                with st.spinner("Görsel istemi hazırlanıyor…"):
                    answer,error=ask_model(page,prompt,[])
                if error: st.error(error)
                else:
                    st.session_state.image_prompt=answer
        if st.session_state.get("image_prompt"):
            st.markdown(st.session_state.image_prompt)
            st.download_button("⬇️ İstemi indir", st.session_state.image_prompt, file_name="lidya_gorsel_istemi.txt", mime="text/plain")
    draw_chat(page)
    value=st.chat_input("Lidya'ya yaz veya dosya ekle…",accept_file="multiple",file_type=["pdf","docx","txt","md","csv","json","py","png","jpg","jpeg","webp"])
    if value: process_chat(page,value)

if st.session_state.voice_output and st.session_state.last_answer:
    lang={"Türkçe":"tr-TR","English":"en-US","Français":"fr-FR","Deutsch":"de-DE","Español":"es-ES","Italiano":"it-IT","日本語":"ja-JP"}.get(st.session_state.interface_language,"tr-TR")
    safe=json.dumps(st.session_state.last_answer,ensure_ascii=False)
    components.html(f'<script>const u=new SpeechSynthesisUtterance({safe});u.lang="{lang}";u.rate=1;window.speechSynthesis.cancel();window.speechSynthesis.speak(u);</script>',height=0)

st.markdown(f"<div style='text-align:center;opacity:.68;padding:28px 0 10px;font-size:13px'>💜 Lidya AI · Built with curiosity and Python. · {now_tr()}</div>",unsafe_allow_html=True)

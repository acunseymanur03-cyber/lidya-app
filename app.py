import streamlit as st
import google.generativeai as genai

# 1. TEMEL AYARLAR & CSS (Senin orijinal mükemmel stillerin buraya gelmeli!)
st.set_page_config(page_title="🧠 Lidya", layout="wide")

# Örnek Mavi Dijital Beyin ve Estetik Still (Kendi CSS'ini buraya yapıştır)
st.markdown("""
<style>
    .stApp { background-color: #f0f4f8; } /* Arka plan */
    .lab-title {
        color: #1e3a8a; /* Mavi dijital beyin rengine uygun mavi */
        text-align: center;
        font-family: 'Courier New', monospace; /* Bilimsel hava */
        font-size: 40px;
        font-weight: bold;
    }
    .lab-intro {
        text-align: center;
        color: #4b5563;
        font-size: 20px;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)


# 2. SESSION STATE & İSİM KONTROLÜ
if "user_name" not in st.session_state:
    st.session_state.user_name = None

# Eğer sohbet geçmişin varsa onu da session state'de tut
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# 3. İSİM ALMA EKRANI (İsim girilmediyse burası görünür)
if not st.session_state.user_name:
    # --- İŞTE O MÜKEMMEL GİRİŞ EKRANINI BURADA OLUŞTURUYORUZ ---
    st.markdown('<p class="lab-title">🧠 Lidya - Laboratuvara Hoş Geldin! 🧪✨</p>', unsafe_allow_html=True)
    st.markdown('<p class="lab-intro">Zihnim aktif, bugün hangi mucizevi ve asimetrik fikir üzerinde çalışıyoruz?</p>', unsafe_allow_html=True)
    
    # Buraya kendi CSS'inle süslenmiş resimlerini veya ikonlarını da koyabilirsin
    # Örn: st.image("mavi_beyin.png", width=100) veya HTML ile:
    # st.markdown('<div class="dijital-beyin-kutusu">...</div>', unsafe_allow_html=True)

    st.write("---") # Ayırıcı çizgi

    # İsim alma alanı
    with st.container():
        st.write("### Sohbet etmeden önce, sana nasıl hitap etmemi istersin?")
        name_input = st.text_input("Adın nedir?", placeholder="Örn: Aslı, Barış...")
        
        if st.button("Sohbete Başla", key="start_chat_btn") and name_input:
            st.session_state.user_name = name_input
            st.rerun()  # Sayfayı yenileyip sohbet ekranına geçirir


# 4. SOHBET EKRANI (İsim girildikten sonra burası çalışır)
else:
    # Lidya'nın dinamik sistem talimatı (İSMİ BURADA KULLANIYORUZ)
    system_prompt = f"""
    Senin adın Lidya. Enerjik, mucizeler ve yenilikler peşinde olan, bilim odaklı bir yapay zekasın.
    Şu an sohbet ettiğin kullanıcının adı: {st.session_state.user_name}.
    Kullanıcıya kendi adıyla ({st.session_state.user_name}) hitap et.
    """

    # Model ve Sohbet Nesnesini Başlat (Eğer yoksa)
    # Kendi API konfigurasyonunu buraya ekle (Secrets kullanman daha güvenli)
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"]) 
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_prompt)
    chat = model.start_chat(history=st.session_state.chat_history)

    # Sohbet Başlığı (Dinamik İsimle)
    st.markdown(f'<p class="lab-title">🧠 Lidya & {st.session_state.user_name} Laboratuvarı</p>', unsafe_allow_html=True)
    st.write(f"### Hoş geldin **{st.session_state.user_name}**! Today is a perfect day to innovate. 🧪✨")

    # --- SOHBET GÖRÜNTÜLEME VE MESAJ YAZMA ALANI (BUNLARI GERİ GETİRDİK) ---
    # Sohbet geçmişini ekrana yazdır
    for message in chat.history:
        role = "Lidya" if message.role == "model" else st.session_state.user_name
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

    # Kullanıcının mesaj yazacağı yer (chat_input)
    if prompt := st.chat_input(f"Lidya'ya bir şeyler yaz, {st.session_state.user_name}..."):
        # Kullanıcının mesajını ekrana ekle
        with st.chat_message(st.session_state.user_name):
            st.markdown(prompt)
        
        # Yapay zekadan yanıt al
        with st.chat_message("Lidya"):
            response = chat.send_message(prompt)
            st.markdown(response.text)
            
        # Sohbet geçmişini session state'e kaydet (Modelin kendi history'sini kullanıyoruz)
        st.session_state.chat_history = chat.history

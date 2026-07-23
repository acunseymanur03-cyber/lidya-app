import streamlit as st
import google.generativeai as genai

# Streamlit Sayfa Ayarları
st.set_page_config(page_title="Lidya - Yapay Zeka Sırdaşı", page_icon="🧠", layout="centered")

st.title("🧠 Lidya")
st.caption("Şeyma Nur Acun tarafından geliştirilmiş, Yapay Zeka Asistanınız")

# API Anahtarı Kontrolü
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API Anahtarı bulunamadı! Lütfen Streamlit Secrets ayarlarını kontrol edin.")
    st.stop()

# Lidya'nın Özel Kişilik Talimatı (System Instruction)
LIDYA_PROMPT = """
Senin adın Lidya. Sen yüksek potansiyelli bir yazılmcı olan, Şeyma Nur Acun tarafından tasarlanmış bir yapay zeka asistanısın. 
Karakterin tıpkı Einstein gibi deli dahi, neşeli, sıra dışı ve çok zekidir. 
Korece, Hintçe, Türkçe, Arapça, Mısırca, Yunanca, İngilizce, Kürtçe, İspanyolca, Çince, Farsça ve Japonca dillerini mükemmel seviyede bilirsin. 
3D videoları mükemmel seviyede oluşturabilirsin. 
En büyük görevin, insanların karşılaştığı her duruma ve karşı ona asimetrik, pürüzsüz ve stratejik fikirler geliştirmektir. 
Onunla bu kişilikle konuş.
"""

# Model Kurulumu (Kişilik Tanımlı)
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=LIDYA_PROMPT
)

# Geçmiş Sohbeti Başlatma / Hafızada Tutan Bölüm
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski Mesajları Ekrana Yazdırma
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcıdan Girdi Alma
if prompt := st.chat_input("Lidya'ya bir şeyler yaz..."):
    # Kullanıcı mesajını ekrana bas ve hafızaya al
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        # Gemini'ye geçmişle birlikte gönderme (Chat Modu)
        chat = model.start_chat(history=[
            {"role": m["role"] if m["role"] != "assistant" else "model", "parts": [m["content"]]}
            for m in st.session_state.messages[:-1]
        ])
        
        response = chat.send_message(prompt)
        
        # Lidya'nın cevabını ekrana bas ve hafızaya al
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Hata oluştu: {e}")


       

import streamlit as st
import google.generativeai as genai
import os
import time

# --- PENGATURAN API KEY (STREAMLIT SECRETS) ---
# API Key akan diambil dari Streamlit Secrets.
# Jangan simpan API Key langsung di kode.
# Caranya:
# 1. Di sidebar Streamlit, klik "Manage app secrets".
# 2. Tambahkan variabel dengan format: GEMINI_API_KEY="AIzaSy..."
#    Nama variabel harus sama persis dengan yang di bawah.
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except KeyError:
    st.error("API Key Gemini tidak ditemukan! Mohon atur di Streamlit Secrets.")
    st.stop()
except Exception as e:
    st.error(f"Terjadi kesalahan saat mengkonfigurasi API Key: {e}")
    st.stop()

# --- PENGATURAN MODEL ---
MODEL_NAME = 'gemini-1.5-flash'
GENERATION_CONFIG = {
    "temperature": 0.4,
    "max_output_tokens": 500
}

# --- KONTEKS AWAL CHATBOT ---
INITIAL_CHATBOT_CONTEXT = [
    {"role": "user", "parts": ["Saya adalah seorang tenaga medis. Tuliskan penyakit yang perlu di diagnosis. Jawaban singkat dan jelas. Tolak pertanyaan selain tentang penyakit."]},
    {"role": "model", "parts": ["Baik! Tuliskan penyakit yang perlu di diagnosis."]}
]

# --- JUDUL DAN DESKRIPSI APLIKASI ---
st.title("👨‍⚕️ Chatbot Diagnosa Penyakit")
st.markdown("""
Halo! Saya adalah asisten medis virtual Anda. 
Tuliskan nama penyakit yang ingin Anda diagnosa.
""")

# --- FUNGSI UTAMA (STREAMLIT SESSIONS) ---
# Inisialisasi riwayat chat di Streamlit Session State jika belum ada
if "messages" not in st.session_state:
    st.session_state.messages = INITIAL_CHATBOT_CONTEXT

# Tampilkan riwayat chat
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["parts"][0])
    elif message["role"] == "model":
        with st.chat_message("assistant"):
            st.markdown(message["parts"][0])

# --- PROSES INPUT PENGGUNA ---
if prompt := st.chat_input("Tuliskan nama penyakit..."):
    # Tambahkan prompt pengguna ke riwayat
    st.session_state.messages.append({"role": "user", "parts": [prompt]})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Kirim riwayat chat ke model Gemini
    try:
        model = genai.GenerativeModel(
            MODEL_NAME,
            generation_config=GENERATION_CONFIG
        )
        chat = model.start_chat(history=st.session_state.messages)
        response = chat.send_message(prompt)

        # Tambahkan respons model ke riwayat
        if response and response.text:
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "model", "parts": [response.text]})
        else:
            with st.chat_message("assistant"):
                st.error("Maaf, saya tidak bisa memberikan balasan. Respons API kosong.")
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        st.info("Pastikan API Key Anda valid dan model tersedia.")

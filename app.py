import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import whisper
import tempfile
import yt_dlp
import glob

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Toolkit PRO MAX", layout="wide")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------- CSS ----------------
st.markdown("""
<style>
body {background-color: #0e1117; color: white;}
.block-container {padding-top: 2rem;}
div.stButton > button {
    background-color: #ff4b4b;
    color: white;
    border-radius: 10px;
    height: 45px;
    width: 100%;
    font-weight: bold;
}
.card {
    background-color: #161b22;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- VOICE ----------------
async def generate_voice(text):
    tts = edge_tts.Communicate(text, "my-MM-NilarNeural")
    await tts.save("voice.mp3")

# ---------------- SESSION ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"

# ---------------- HOME ----------------
if st.session_state.page == "home":
    st.title("🚀 Your Creative AI Toolkit")
    st.write("Scripts, stories, translations, thumbnails & voices — all powered by AI")

    cols = st.columns(3)

    tools = [
        ("🎬 Recapper", "recap"),
        ("🔊 AI Voice", "voice"),
        ("🌍 Translate", "translate"),
        ("✍️ Content Creator", "content"),
        ("📝 Video → SRT", "srt"),
        ("📺 YouTube AI", "yt"),
    ]

    for i, (name, key) in enumerate(tools):
        with cols[i % 3]:
            st.markdown(f"<div class='card'><h3>{name}</h3></div>", unsafe_allow_html=True)
            if st.button("Launch →", key=key):
                st.session_state.page = key

# ---------------- RECAP ----------------
elif st.session_state.page == "recap":

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    st.header("🎬 Movie Recapper")

    text = st.text_area("📄 Paste Transcript")

    if st.button("Generate Recap"):
        if text:
            recap = model.generate_content(
                f"ဒီစာကို exciting Burmese movie recap style နဲ့ရေးပါ:\n{text}"
            ).text

            st.subheader("🎬 Recap")
            st.write(recap)

            asyncio.run(generate_voice(recap))
            with open("voice.mp3", "rb") as f:
                st.audio(f.read(), format="audio/mp3")

# ---------------- VOICE ----------------
elif st.session_state.page == "voice":

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    st.header("🔊 AI Voice")

    text = st.text_area("📄 Enter Text")

    if st.button("Generate Voice"):
        if text:
            asyncio.run(generate_voice(text))
            with open("voice.mp3", "rb") as f:
                st.audio(f.read(), format="audio/mp3")

# ---------------- TRANSLATE ----------------
elif st.session_state.page == "translate":

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    st.header("🌍 Translate")

    text = st.text_area("📄 Enter Text")

    if st.button("Translate"):
        if text:
            result = model.generate_content(f"ဒီစာကို မြန်မာလို ဘာသာပြန်ပါ:\n{text}")
            st.write(result.text)

# ---------------- CONTENT ----------------
elif st.session_state.page == "content":

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    st.header("✍️ Content Creator")

    text = st.text_area("📄 Topic")

    if st.button("Generate Content"):
        if text:
            result = model.generate_content(f"{text} social media script ရေးပါ")
            st.write(result.text)

# ---------------- VIDEO → SRT ----------------
elif st.session_state.page == "srt":

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    st.header("📝 Video → SRT")

    file = st.file_uploader("Upload Video", type=["mp4", "mov", "mkv"])

    if file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.read())
            path = tmp.name

        st.info("Transcribing...")

        model_w = whisper.load_model("tiny")  # faster
        result = model_w.transcribe(path)

        srt = ""
        for i, seg in enumerate(result["segments"]):
            srt += f"{i+1}\n{seg['start']} --> {seg['end']}\n{seg['text']}\n\n"

        st.text(srt)

        st.download_button("⬇ Download SRT", srt, file_name="subtitles.srt")

# ---------------- YOUTUBE ----------------
elif st.session_state.page == "yt":

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    st.header("📺 YouTube AI")

    url = st.text_input("Paste YouTube Link")

    if st.button("Process"):
        if url:
            st.info("Downloading audio...")

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'audio.%(ext)s',
                'quiet': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            st.info("Transcribing...")

            model_w = whisper.load_model("tiny")
            audio_file = glob.glob("audio.*")[0]

            result = model_w.transcribe(audio_file)

            transcript = result["text"]

            st.subheader("📄 Transcript")
            st.write(transcript)

            recap = model.generate_content(
                f"ဒီ video ကို Burmese recap style နဲ့ရေး:\n{transcript}"
            ).text

            st.subheader("🎬 Recap")
            st.write(recap)

            asyncio.run(generate_voice(recap))
            with open("voice.mp3", "rb") as f:
                st.audio(f.read(), format="audio/mp3")

            srt = ""
            for i, seg in enumerate(result["segments"]):
                srt += f"{i+1}\n{seg['start']} --> {seg['end']}\n{seg['text']}\n\n"

            st.download_button("⬇ Download SRT", srt, file_name="youtube.srt")

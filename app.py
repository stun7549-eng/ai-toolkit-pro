import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import whisper
import tempfile
import yt_dlp
import glob

# CONFIG
st.set_page_config(page_title="AI Toolkit PRO MAX", layout="wide")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# VOICE
async def generate_voice(text):
    tts = edge_tts.Communicate(text, "my-MM-NilarNeural")
    await tts.save("voice.mp3")

# SESSION
if "page" not in st.session_state:
    st.session_state.page = "home"

# ---------------- HOME UI ----------------
if st.session_state.page == "home":
    st.title("🚀 Your Creative AI Toolkit")
    st.write("Scripts, stories, translations, thumbnails & voices — all powered by AI")

    cols = st.columns(4)

    tools = [
        ("🎬 Recapper", "recap"),
        ("🔊 AI Voice", "voice"),
        ("🌍 Translate", "translate"),
        ("✍️ Content Creator", "content"),
        ("📝 SRT Sub", "srt"),
        ("📺 YouTube AI", "yt"),
    ]

    for i, (name, key) in enumerate(tools):
        with cols[i % 4]:
            st.subheader(name)
            if st.button("Launch →", key=key):
                st.session_state.page = key

# ---------------- BACK BUTTON ----------------
if st.session_state.page != "home":
    if st.button("⬅ Back"):
        st.session_state.page = "home"

# ---------------- RECAP ----------------
if st.session_state.page == "recap":
    st.header("🎬 Movie Recapper")

    text = st.text_area("📄 Paste Transcript")

    if st.button("Generate"):
        if text:
            recap = model.generate_content(
                f"ဒီစာကို exciting Burmese movie recap style နဲ့ရေးပါ:\n{text}"
            ).text

            st.write(recap)

            asyncio.run(generate_voice(recap))
            with open("voice.mp3", "rb") as f:
                st.audio(f.read(), format="audio/mp3")

# ---------------- VOICE ----------------
elif st.session_state.page == "voice":
    st.header("🔊 AI Voice")

    text = st.text_area("📄 Text")

    if st.button("Generate"):
        if text:
            asyncio.run(generate_voice(text))
            with open("voice.mp3", "rb") as f:
                st.audio(f.read(), format="audio/mp3")

# ---------------- TRANSLATE ----------------
elif st.session_state.page == "translate":
    st.header("🌍 Translate")

    text = st.text_area("📄 Enter text")

    if st.button("Translate"):
        if text:
            st.write(model.generate_content(f"မြန်မာလိုဘာသာပြန်:\n{text}").text)

# ---------------- CONTENT ----------------
elif st.session_state.page == "content":
    st.header("✍️ Content Creator")

    text = st.text_area("📄 Topic")

    if st.button("Generate"):
        if text:
            st.write(model.generate_content(f"{text} social media script").text)

# ---------------- SRT ----------------
elif st.session_state.page == "srt":
    st.header("📝 Video → SRT")

    file = st.file_uploader("Upload Video", type=["mp4"])

    if file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.read())
            path = tmp.name

        st.info("Processing...")
        model_w = whisper.load_model("tiny")
        result = model_w.transcribe(path)

        srt = ""
        for i, seg in enumerate(result["segments"]):
            srt += f"{i+1}\n{seg['start']} --> {seg['end']}\n{seg['text']}\n\n"

        st.text(srt)
        st.download_button("Download SRT", srt)

# ---------------- YOUTUBE ----------------
elif st.session_state.page == "yt":
    st.header("📺 YouTube AI")

    url = st.text_input("YouTube Link")

    if st.button("Process"):
        if url:
            st.info("Downloading...")

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
            st.subheader("Transcript")
            st.write(transcript)

            recap = model.generate_content(
                f"ဒီ video ကို Burmese recap style နဲ့ရေး:\n{transcript}"
            ).text

            st.subheader("Recap")
            st.write(recap)

            asyncio.run(generate_voice(recap))
            with open("voice.mp3", "rb") as f:
                st.audio(f.read(), format="audio/mp3")

            srt = ""
            for i, seg in enumerate(result["segments"]):
                srt += f"{i+1}\n{seg['start']} --> {seg['end']}\n{seg['text']}\n\n"

            st.download_button("Download SRT", srt)

import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import whisper
import tempfile

st.set_page_config(page_title="AI Toolkit PRO", layout="wide")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

st.title("🚀 Your Creative AI Toolkit")
st.write("Scripts, stories, translations, thumbnails & voices — all powered by AI")

menu = st.radio("Select Tool", [
    "🎬 Recapper",
    "🔊 AI Voice",
    "🌍 Translate",
    "✍️ Content Creator",
    "📝 SRT Sub"
])

# Voice
async def generate_voice(text):
    tts = edge_tts.Communicate(text, "my-MM-NilarNeural")
    await tts.save("voice.mp3")

# Recapper
if menu == "🎬 Recapper":
    text = st.text_area("📄 Paste Transcript")

    if st.button("Generate Recap"):
        if text:
            recap = model.generate_content(
                f"ဒီစာကို exciting Burmese movie recap style နဲ့ရေးပါ:\n{text}"
            ).text

            st.write(recap)
            asyncio.run(generate_voice(recap))

            with open("voice.mp3", "rb") as f:
                st.audio(f.read(), format="audio/mp3")

# Voice tool
elif menu == "🔊 AI Voice":
    text = st.text_area("📄 Text")

    if st.button("Generate Voice"):
        if text:
            asyncio.run(generate_voice(text))

            with open("voice.mp3", "rb") as f:
                st.audio(f.read(), format="audio/mp3")

# Translate
elif menu == "🌍 Translate":
    text = st.text_area("📄 Enter text")

    if st.button("Translate"):
        if text:
            st.write(
                model.generate_content(f"မြန်မာလိုဘာသာပြန်:\n{text}").text
            )

# SRT Tool
elif menu == "📝 SRT Sub":
    uploaded = st.file_uploader("📹 Upload Video", type=["mp4"])

    if uploaded:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded.read())
            path = tmp.name

        st.info("⏳ Processing...")
        model_w = whisper.load_model("base")
        result = model_w.transcribe(path)

        srt = ""
        for i, seg in enumerate(result["segments"]):
            srt += f"{i+1}\n{seg['start']} --> {seg['end']}\n{seg['text']}\n\n"

        st.text(srt)

        st.download_button("Download SRT", srt)

# Content
elif menu == "✍️ Content Creator":
    text = st.text_area("📄 Topic")

    if st.button("Generate"):
        if text:
            st.write(
                model.generate_content(f"{text} social media script").text
            )

import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts

# CONFIG
st.set_page_config(page_title="AI Toolkit PRO", layout="wide")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------- HOME ----------------
st.title("🚀 Your Creative AI Toolkit")
st.write("Scripts, stories, translations, thumbnails & voices — all powered by AI")

menu = st.radio("Select Tool", [
    "🎬 Recapper",
    "🔊 AI Voice",
    "🌍 Translate",
    "✍️ Content Creator"
])"📝 SRT Sub",

# ---------------- VOICE FUNCTION ----------------
async def generate_voice(text):
    tts = edge_tts.Communicate(text, "my-MM-NilarNeural")
    await tts.save("voice.mp3")

# ---------------- RECAPPER ----------------
if menu == "🎬 Recapper":
    st.header("🎬 Movie Recapper")

    text = st.text_area("📄 Paste Transcript")

    if st.button("Generate Recap"):
        if text:
            result = model.generate_content(
                f"ဒီစာကို exciting Burmese movie recap style နဲ့ရေးပါ:\n{text}"
            )
            recap = result.text

            st.subheader("🎬 Recap Script")
            st.write(recap)

            asyncio.run(generate_voice(recap))

            with open("voice.mp3", "rb") as audio_file:
                st.audio(audio_file.read(), format="audio/mp3")
        else:
            st.warning("စာသားထည့်ပါ")

# ---------------- AI VOICE ----------------
elif menu == "🔊 AI Voice":
    st.header("🔊 Text to Burmese Voice")

    text = st.text_area("📄 Text")

    if st.button("Generate Voice"):
        if text:
            asyncio.run(generate_voice(text))

            with open("voice.mp3", "rb") as audio_file:
                st.audio(audio_file.read(), format="audio/mp3")
        else:
            st.warning("စာသားထည့်ပါ")

# ---------------- TRANSLATE ----------------
elif menu == "🌍 Translate":
    st.header("🌍 Translate")

    text = st.text_area("📄 Enter text")

    if st.button("Translate to Burmese"):
        if text:
            result = model.generate_content(
                f"ဒီစာကို မြန်မာလို ဘာသာပြန်ပေးပါ:\n{text}"
            )
            st.write(result.text)
        else:
            st.warning("စာသားထည့်ပါ")import whisper
import tempfile

# ---------------- SRT TOOL ----------------
elif menu == "📝 SRT Sub":
    st.header("📝 Video → SRT Subtitle")

    uploaded_file = st.file_uploader("📹 Upload Video", type=["mp4", "mov", "mkv"])

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            tmp_file.write(uploaded_file.read())
            video_path = tmp_file.name

        st.info("⏳ Transcribing...")

        model_whisper = whisper.load_model("base")
        result = model_whisper.transcribe(video_path)

        # Convert to SRT
        def format_time(seconds):
            hrs = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds - int(seconds)) * 1000)
            return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"

        srt_content = ""
        for i, seg in enumerate(result["segments"]):
            start = format_time(seg["start"])
            end = format_time(seg["end"])
            text = seg["text"]

            srt_content += f"{i+1}\n{start} --> {end}\n{text}\n\n"

        st.subheader("📄 SRT Preview")
        st.text(srt_content)

        st.download_button(
            label="⬇️ Download SRT",
            data=srt_content,
            file_name="subtitles.srt",
            mime="text/plain"
        )

# ---------------- CONTENT CREATOR ----------------
elif menu == "✍️ Content Creator":
    st.header("✍️ Content Creator")

    text = st.text_area("📄 Topic")

    if st.button("Generate Content"):
        if text:
            result = model.generate_content(
                f"{text} အတွက် engaging social media script ရေးပေးပါ"
            )
            st.write(result.text)
        else:
            st.warning("စာသားထည့်ပါ")

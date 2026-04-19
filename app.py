import streamlit as st
import whisper
import tempfile
import asyncio
import edge_tts

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Myanmar AI Tools", layout="centered")

# ---------------- WHISPER ----------------
@st.cache_resource
def load_model():
    return whisper.load_model("base")

# ---------------- VOICE ----------------
async def generate_voice(text):
    tts = edge_tts.Communicate(text, "my-MM-NilarNeural")
    await tts.save("voice.mp3")

# ---------------- TIME FORMAT ----------------
def format_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"

# ---------------- UI ----------------
st.title("🇲🇲 Myanmar AI Tools")

tab1, tab2 = st.tabs(["🎬 Video → SRT", "🔊 Text → Voice"])

# ---------------- VIDEO TO SRT ----------------
with tab1:
    st.header("🎬 Video → Myanmar Subtitle (SRT)")

    file = st.file_uploader("Upload Video", type=["mp4", "mov", "mkv"])

    if file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.read())
            path = tmp.name

        st.info("Transcribing... (wait a bit)")

        model = load_model()
        result = model.transcribe(path, language="my")  # 👈 force Myanmar

        srt = ""
        for i, seg in enumerate(result["segments"]):
            srt += f"{i+1}\n{format_time(seg['start'])} --> {format_time(seg['end'])}\n{seg['text']}\n\n"

        st.success("Done!")
        st.text_area("SRT Preview", srt, height=300)

        st.download_button("⬇️ Download SRT", srt, "subtitle.srt")

# ---------------- TEXT TO VOICE ----------------
with tab2:
    st.header("🔊 Myanmar Text → Voice")

    text = st.text_area("Enter Myanmar Script")

    if st.button("Generate Voice"):
        if text:
            st.info("Generating voice...")
            asyncio.run(generate_voice(text))

            st.success("Done!")
            st.audio("voice.mp3")

            with open("voice.mp3", "rb") as f:
                st.download_button(
                    "⬇️ Download Voice",
                    f,
                    "voice.mp3",
                    "audio/mpeg"
                )

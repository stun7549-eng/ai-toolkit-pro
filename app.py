import streamlit as st
import whisper
import tempfile
import asyncio
import edge_tts

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Myanmar AI Tools PRO", layout="centered")

# ---------------- WHISPER ----------------
@st.cache_resource
def load_model():
    return whisper.load_model("base")

# ---------------- VOICE ----------------
async def generate_voice(text, rate):
    tts = edge_tts.Communicate(text, "my-MM-NilarNeural", rate=rate)
    await tts.save("voice.mp3")

# ---------------- TIME ----------------
def format_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"

# ---------------- SIMPLE TRANSLATE ----------------
def simple_translate(text):
    # basic EN → MM keywords (lightweight)
    replace_dict = {
        "hello": "မင်္ဂလာပါ",
        "thank you": "ကျေးဇူးတင်ပါတယ်",
        "yes": "ဟုတ်ကဲ့",
        "no": "မဟုတ်ပါ",
    }
    for k, v in replace_dict.items():
        text = text.replace(k, v)
    return text

# ---------------- UI ----------------
st.title("🇲🇲 Myanmar AI Tools PRO")

tab1, tab2 = st.tabs(["🎬 Video → SRT", "🔊 Text → Voice"])

# ---------------- VIDEO → SRT ----------------
with tab1:
    st.header("🎬 Video Subtitle Generator")

    file = st.file_uploader("Upload Video", type=["mp4", "mov", "mkv"])

    translate = st.checkbox("🌍 Translate to Myanmar")

    if file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.read())
            path = tmp.name

        st.info("Transcribing...")

        model = load_model()
        result = model.transcribe(path)

        srt = ""

        for i, seg in enumerate(result["segments"]):
            text = seg["text"]

            if translate:
                text = simple_translate(text.lower())

            srt += f"{i+1}\n{format_time(seg['start'])} --> {format_time(seg['end'])}\n{text}\n\n"

        st.success("Done!")
        st.text_area("Preview", srt, height=300)

        st.download_button("⬇️ Download SRT", srt, "subtitle.srt")

# ---------------- TEXT → VOICE ----------------
with tab2:
    st.header("🔊 Myanmar Voice Generator")

    text = st.text_area("Enter Script")

    speed = st.selectbox(
        "🎚 Voice Speed",
        {
            "🐢 Slow": "-20%",
            "🚶 Normal": "0%",
            "🏃 Fast": "+20%"
        }
    )

    if st.button("Generate Voice"):
        if text:
            st.info("Generating voice...")
            asyncio.run(generate_voice(text, speed))

            st.success("Done!")
            st.audio("voice.mp3")

            with open("voice.mp3", "rb") as f:
                st.download_button("⬇️ Download Voice", f, "voice.mp3")

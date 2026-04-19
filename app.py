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

genai.configure(api_key=st.secrets.get("GEMINI_API_KEY", ""))
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------- VOICE ----------------
async def generate_voice(text, voice):
    try:
        tts = edge_tts.Communicate(text, voice)
        await tts.save("voice.mp3")
    except:
        tts = edge_tts.Communicate(text, "th-TH-NiwatNeural")
        await tts.save("voice.mp3")

# ---------------- WHISPER ----------------
@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

# ---------------- UTILS ----------------
def format_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"

# ---------------- SESSION ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"

# ---------------- HOME ----------------
if st.session_state.page == "home":
    st.title("🚀 AI Toolkit PRO MAX")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🎬 Recapper"):
            st.session_state.page = "recap"

    with col2:
        if st.button("🔊 AI Voice"):
            st.session_state.page = "voice"

    with col3:
        if st.button("🌍 Translate"):
            st.session_state.page = "translate"

    col4, col5 = st.columns(2)

    with col4:
        if st.button("📝 SRT Subtitle Tool"):
            st.session_state.page = "srt"

    with col5:
        if st.button("📺 YouTube AI"):
            st.session_state.page = "yt"

# ---------------- RECAP ----------------
elif st.session_state.page == "recap":
    st.header("🎬 Recapper")

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    text = st.text_area("Paste Transcript")

    if st.button("Generate Recap"):
        if text:
            res = model.generate_content(f"ဒီစာကို Burmese recap style နဲ့ရေး:\n{text}")
            recap = res.text
            st.write(recap)

            asyncio.run(generate_voice(recap, "th-TH-NiwatNeural"))
            st.audio("voice.mp3")

            with open("voice.mp3", "rb") as f:
                st.download_button("⬇️ Download Voice", f, "recap.mp3")

# ---------------- VOICE ----------------
elif st.session_state.page == "voice":
    st.header("🔊 AI Voice")

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    text = st.text_area("Enter Text")

    voice_options = {
        "🎙 Thai Male (Best Myanmar Style)": "th-TH-NiwatNeural",
        "🎙 English Male": "en-US-GuyNeural",
        "🎙 UK Male": "en-GB-RyanNeural",
    }

    selected_voice = st.selectbox("🎙 Choose Voice", list(voice_options.keys()))
    voice = voice_options[selected_voice]

    if st.button("Generate Voice"):
        if text:
            asyncio.run(generate_voice(text, voice))
            st.audio("voice.mp3")

            with open("voice.mp3", "rb") as f:
                st.download_button("⬇️ Download Voice", f, "voice.mp3")

# ---------------- TRANSLATE ----------------
elif st.session_state.page == "translate":
    st.header("🌍 Translate")

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    text = st.text_area("Enter Text")

    if st.button("Translate"):
        if text:
            res = model.generate_content(f"မြန်မာလို ဘာသာပြန်ပါ:\n{text}")
            st.write(res.text)

# ---------------- SRT ----------------
elif st.session_state.page == "srt":
    st.header("📝 SRT Subtitle Tool")

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    file = st.file_uploader("Upload Video")

    if file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.read())
            path = tmp.name

        st.info("Transcribing...")

        model_w = load_whisper()
        result = model_w.transcribe(path)

        srt = ""
        for i, seg in enumerate(result["segments"]):
            srt += f"{i+1}\n{format_time(seg['start'])} --> {format_time(seg['end'])}\n{seg['text']}\n\n"

        st.text(srt)
        st.download_button("Download SRT", srt, "subtitles.srt")

# ---------------- YOUTUBE ----------------
elif st.session_state.page == "yt":
    st.header("📺 YouTube AI")

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    url = st.text_input("YouTube URL")

    if st.button("Process") and url:
        st.info("Downloading...")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'audio.%(ext)s',
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        audio_file = glob.glob("audio.*")[0]

        st.info("Transcribing...")

        model_w = load_whisper()
        result = model_w.transcribe(audio_file)

        transcript = result["text"]
        st.write(transcript)

        recap = model.generate_content(
            f"ဒီ video ကို Burmese recap style နဲ့ရေး:\n{transcript}"
        ).text

        st.write(recap)

        asyncio.run(generate_voice(recap, "th-TH-NiwatNeural"))
        st.audio("voice.mp3")

        srt = ""
        for i, seg in enumerate(result["segments"]):
            srt += f"{i+1}\n{format_time(seg['start'])} --> {format_time(seg['end'])}\n{seg['text']}\n\n"

        st.download_button("Download SRT", srt, "youtube.srt")

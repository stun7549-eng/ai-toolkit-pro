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

# ✅ GEMINI API KEY
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# ✅ SAFE MODEL (fallback)
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
except:
    model = genai.GenerativeModel("gemini-1.5-flash-001")

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

# ---------------- WHISPER CACHE ----------------
@st.cache_resource
def load_whisper():
    return whisper.load_model("tiny")

# ---------------- SRT TIME FORMAT ----------------
def format_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"

# ---------------- VOICE ---------------- # 
# SRT → text ပြောင်း
def srt_to_text(srt_content):
    lines = srt_content.split("\n")
    text = []

    for line in lines:
        if "-->" in line:
            continue
        if line.strip().isdigit():
            continue
        if line.strip() == "":
            continue
        text.append(line)

    return " ".join(text)

# Voice generate
async def generate_voice(text, voice):
    import edge_tts
    tts = edge_tts.Communicate(text, voice)
    await tts.save("voice.mp3")

# ---------------- SESSION ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"

# ---------------- HOME ----------------
if st.session_state.page == "home":
    st.title("🚀 Your Creative AI Toolkit")

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
            if st.button(name):
                st.session_state.page = key

# ---------------- RECAP ----------------
elif st.session_state.page == "recap":
    if st.button("⬅ Back"):
        st.session_state.page = "home"

    text = st.text_area("Paste Transcript")

    if st.button("Generate Recap"):
        if text.strip():
            try:
                response = model.generate_content(
                    f"ဒီစာကို Burmese movie recap style နဲ့ရေး:\n{text}"
                )
                recap = response.text or "No response"
                st.write(recap)

                asyncio.run(generate_voice(recap))
                st.audio("voice.mp3")

            except Exception as e:
                st.error(e)

# ---------------- VOICE ----------------
elif st.session_state.page == "voice":
    if st.button("⬅ Back"):
        st.session_state.page = "home"

    st.header("🔊 AI Voice Generator")

    # ✅ Voice Select
    # ---------------- VOICE + SRT TO VOICE ----------------
elif st.session_state.page == "voice":

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    st.header("🔊 AI Voice Generator")

    # 📝 Text input
    text = st.text_area("📄 Enter Text (or leave empty if using SRT)")

    # 📂 SRT Upload
    uploaded_srt = st.file_uploader("📂 Upload SRT file", type=["srt"])

    # 🔥 SRT → Text function
    def srt_to_text(srt_content):
        lines = srt_content.split("\n")
        text_lines = []
        for line in lines:
            if "-->" not in line and not line.strip().isdigit():
                if line.strip():
                    text_lines.append(line.strip())
        return " ".join(text_lines)

    # 🎤 Voice list (20 voices)
    voices = {
        "👩 Female 1 (MM Nilar)": "my-MM-NilarNeural",
        "👨 Male 1 (MM Thiha)": "my-MM-ThihaNeural",

        "👩 Female 2": "en-US-JennyNeural",
        "👩 Female 3": "en-GB-SoniaNeural",
        "👩 Female 4": "en-AU-NatashaNeural",
        "👩 Female 5": "en-IN-NeerjaNeural",
        "👩 Female 6": "en-US-AriaNeural",
        "👩 Female 7": "en-US-AnaNeural",
        "👩 Female 8": "en-CA-ClaraNeural",
        "👩 Female 9": "en-GB-LibbyNeural",
        "👩 Female 10": "en-NZ-MollyNeural",

        "👨 Male 2": "en-US-GuyNeural",
        "👨 Male 3": "en-GB-RyanNeural",
        "👨 Male 4": "en-AU-WilliamNeural",
        "👨 Male 5": "en-IN-PrabhatNeural",
        "👨 Male 6": "en-US-DavisNeural",
        "👨 Male 7": "en-CA-LiamNeural",
        "👨 Male 8": "en-GB-ThomasNeural",
        "👨 Male 9": "en-NZ-MitchellNeural",
        "👨 Male 10": "en-US-JasonNeural"
    }

    # 🎯 Voice select
    voice_label = st.selectbox("🎤 Voice ရွေးပါ", list(voices.keys()))
    voice = voices[voice_label]

    # 🔊 Generate button
    if st.button("🚀 Generate Voice"):

        final_text = text

        # 👉 SRT သုံးမယ်ဆိုရင်
        if uploaded_srt:
            srt_content = uploaded_srt.read().decode("utf-8")
            final_text = srt_to_text(srt_content)

        if final_text:
            st.info("Generating voice...")

            # 🔥 IMPORTANT (voice param ထည့်)
            async def generate_voice(text, voice):
                tts = edge_tts.Communicate(text, voice)
                await tts.save("voice.mp3")

            asyncio.run(generate_voice(final_text, voice))

            st.success("Done ✅")
            st.audio("voice.mp3")

        else:
            st.warning("စာသား သို့မဟုတ် SRT ထည့်ပါ ❗")

# ---------------- TRANSLATE ----------------
elif st.session_state.page == "translate":
    if st.button("⬅ Back"):
        st.session_state.page = "home"

    text = st.text_area("Enter Text")

    if st.button("Translate"):
        if text:
            result = model.generate_content(f"မြန်မာလို ဘာသာပြန်ပါ:\n{text}")
            st.write(result.text)

# ---------------- CONTENT ----------------
elif st.session_state.page == "content":
    if st.button("⬅ Back"):
        st.session_state.page = "home"

    topic = st.text_area("Topic")

    if st.button("Generate"):
        if topic:
            result = model.generate_content(f"{topic} social media script ရေးပါ")
            st.write(result.text)

# ---------------- VIDEO → SRT ----------------
elif st.session_state.page == "srt":
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
            start = format_time(seg["start"])
            end = format_time(seg["end"])
            srt += f"{i+1}\n{start} --> {end}\n{seg['text']}\n\n"

        st.text(srt)
        st.download_button("Download SRT", srt, "subtitles.srt")
        voice = st.selectbox(
    "🎤 Voice ရွေးပါ",
    ["my-MM-NilarNeural", "my-MM-ThihaNeural"]
)

# ---------------- YOUTUBE ----------------
elif st.session_state.page == "yt":
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

        st.info("Transcribing...")

        model_w = load_whisper()
        audio_file = glob.glob("audio.*")[0]
        result = model_w.transcribe(audio_file)

        transcript = result["text"]
        st.write(transcript)

        recap = model.generate_content(
            f"ဒီ video ကို Burmese recap style နဲ့ရေး:\n{transcript}"
        ).text

        st.write(recap)

        asyncio.run(generate_voice(recap))
        st.audio("voice.mp3")

        # SRT
        srt = ""
        for i, seg in enumerate(result["segments"]):
            start = format_time(seg["start"])
            end = format_time(seg["end"])
            srt += f"{i+1}\n{start} --> {end}\n{seg['text']}\n\n"

        st.download_button("Download SRT", srt, "youtube.srt")

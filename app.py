import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import whisper
import tempfile
import yt_dlp
import glob
import os

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Toolkit PRO MAX", layout="wide")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-pro")

# ---------------- PRO UI ----------------
st.markdown("""
<style>
body {
    background: #0b0f1a;
    color: white;
}

/* GRID */
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
}

/* CARD */
.card {
    background: linear-gradient(145deg, #111827, #0b0f1a);
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 0 20px rgba(0,255,255,0.05);
    transition: 0.3s;
}
.card:hover {
    transform: translateY(-6px);
    box-shadow: 0 0 30px rgba(0,255,255,0.25);
}

/* BUTTON */
div.stButton > button {
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    border-radius: 10px;
    height: 45px;
    font-weight: bold;
    color: white;
}

/* TITLE */
h1 {
    text-align: center;
    font-size: 40px;
    background: linear-gradient(90deg,#00c6ff,#0072ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>
""", unsafe_allow_html=True)

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

async def generate_voice(text, voice_data):
    try:
        if isinstance(voice_data, tuple):
            voice_name, rate = voice_data
        else:
            voice_name, rate = voice_data, "0%"

        tts = edge_tts.Communicate(text, voice_name, rate=rate)
        await tts.save("voice.mp3")

    except:
        voice_options = {
    "🇲🇲 Nilar (Normal)": "my-MM-NilarNeural",
    "🇲🇲 Nilar (Slow)": ("my-MM-NilarNeural", "-10%"),
    "🇲🇲 Nilar (Fast)": ("my-MM-NilarNeural", "+10%"),
    "🌏 Thai Female (Fallback)": "th-TH-PremwadeeNeural",
}

# ---------------- SESSION ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"

# ---------------- HOME ----------------
if st.session_state.page == "home":
    st.title("🚀 AI Toolkit PRO MAX")

    tools = [
        ("🎬 Recapper", "Video → Recap Script", "recap"),
        ("🔊 AI Voice", "Text to Speech", "voice"),
        ("🌍 Translate", "Multi-language", "translate"),
        ("✍️ Content Creator", "Social Scripts", "content"),
        ("📝 SRT Subtitle Tool", "Auto Subtitle Generator", "srt"),
        ("📺 YouTube AI", "Download + Transcribe + Recap", "yt"),
    ]

    cols = st.columns(3)

    for i, (name, desc, key) in enumerate(tools):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card">
                <h3>{name}</h3>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Launch {name}", key=key):
                st.session_state.page = key

# ---------------- RECAP ----------------
elif st.session_state.page == "recap":
    st.header("🎬 Recapper")
    if st.button("⬅ Back"):
        st.session_state.page = "home"

    text = st.text_area("Paste Transcript")

    if st.button("Generate Recap"):
        if text:
            res = model.generate_content(f"ဒီစာကို Burmese movie recap style နဲ့ရေး:\n{text}")
            recap = res.text
            st.success("Done!")
            st.write(recap)

            asyncio.run(generate_voice(recap))
            st.audio("voice.mp3")

            with open("voice.mp3", "rb") as f:
                st.download_button(
                    label="⬇️ Download Voice",
                    data=f,
                    file_name="recap_voice.mp3",
                    mime="audio/mpeg"
                )
    

# ---------------- VOICE ----------------
elif st.session_state.page == "voice":
    st.header("🔊 AI Voice")
    if st.button("⬅ Back"):
        st.session_state.page = "home"

    text = st.text_area("Enter Text")

    if st.button("Generate Voice"):
        if text:
            asyncio.run(generate_voice(text))
            st.audio("voice.mp3")

            with open("voice.mp3", "rb") as f:
                st.download_button(
                    "⬇️ Download Voice",
                    f,
                    "voice.mp3",
                    "audio/mpeg"
                )

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

# ---------------- CONTENT ----------------
elif st.session_state.page == "content":
    st.header("✍️ Content Creator")
    if st.button("⬅ Back"):
        st.session_state.page = "home"

    topic = st.text_area("Topic")

    if st.button("Generate"):
        if topic:
            res = model.generate_content(f"{topic} social media script ရေးပါ")
            st.write(res.text)

# ---------------- SRT ----------------
elif st.session_state.page == "srt":
    st.header("📝 SRT Generator")
    if st.button("⬅ Back"):
        st.session_state.page = "home"

    file = st.file_uploader("Upload Video")

    if file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.read())
            path = tmp.name

        st.info("Processing...")

        model_w = load_whisper()
        result = model_w.transcribe(path)

        srt = ""
        for i, seg in enumerate(result["segments"]):
            srt += f"{i+1}\n{format_time(seg['start'])} --> {format_time(seg['end'])}\n{seg['text']}\n\n"

        st.success("Done!")
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

        files = glob.glob("audio.*")
        if not files:
            st.error("Download failed")
        else:
            audio_file = files[0]

            st.info("Transcribing...")

            model_w = load_whisper()
            result = model_w.transcribe(audio_file)

            transcript = result["text"]
            st.write(transcript)

            recap = model.generate_content(
                f"ဒီ video ကို Burmese recap style နဲ့ရေး:\n{transcript}"
            ).text

            st.write(recap)

            asyncio.run(generate_voice(recap))
            st.audio("voice.mp3")

            srt = ""
            for i, seg in enumerate(result["segments"]):
                srt += f"{i+1}\n{format_time(seg['start'])} --> {format_time(seg['end'])}\n{seg['text']}\n\n"

            st.download_button("Download SRT", srt, "youtube.srt")

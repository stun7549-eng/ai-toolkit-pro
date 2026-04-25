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
st.set_page_config(page_title="AI Toolkit PRO MAX", layout="wide", page_icon="🚀")

# ✅ GEMINI API KEY
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    "AIzaSyA744LtWjhqq5-igWPanYTnLkmWpdrBm98"

else:
    st.error("Please set GEMINI_API_KEY in Streamlit Secrets!")

# ✅ MODEL SETUP
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
except:
    model = genai.GenerativeModel("gemini-1.5-flash-001")

# ---------------- CSS ----------------
st.markdown("""
<style>
    body {background-color: #0e1117; color: white;}
    .stButton > button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 10px;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #ff3333;
        border: 1px solid white;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- HELPERS ----------------
@st.cache_resource
def load_whisper():
    return whisper.load_model("tiny")

def format_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"

def srt_to_text(srt_content):
    lines = srt_content.split("\n")
    text = []
    for line in lines:
        if "-->" in line or line.strip().isdigit() or line.strip() == "":
            continue
        text.append(line)
    return " ".join(text)

async def generate_voice(text, voice, output_path="voice.mp3"):
    chunks = [text[i:i+2000] for i in range(0, len(text), 2000)]
    with open(output_path, "wb") as audio_file:
        for chunk in chunks:
            success = False
            for attempt in range(3):
                try:
                    tts = edge_tts.Communicate(chunk, voice)
                    async for stream in tts.stream():
                        if stream["type"] == "audio":
                            audio_file.write(stream["data"])
                    success = True
                    break
                except:
                    await asyncio.sleep(1)
            
            if not success:
                # Fallback to English
                tts = edge_tts.Communicate(chunk, "en-US-GuyNeural")
                async for stream in tts.stream():
                    if stream["type"] == "audio":
                        audio_file.write(stream["data"])

# ---------------- SESSION ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"

# ---------------- PAGE: HOME ----------------
if st.session_state.page == "home":
    st.title("🚀 Your Creative AI Toolkit")
    st.subheader("အလွယ်ကူဆုံး AI လက်ထောက်")
    
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
            if st.button(name, use_container_width=True):
                st.session_state.page = key

# ---------------- PAGE: RECAP ----------------
elif st.session_state.page == "recap":
    if st.button("⬅ Back"): st.session_state.page = "home"
    st.header("🎬 Movie/Video Recap Generator")
    
    text = st.text_area("Paste Transcript Here", height=200)
    voice_opt = st.selectbox("အသံရွေးပါ", ["my-MM-NilarNeural", "my-MM-ThihaNeural"])

    if st.button("Generate Recap & Voice"):
        if text.strip():
            with st.spinner("AI က စဉ်းစားနေပါတယ်..."):
                try:
                    response = model.generate_content(f"ဒီစာကို Burmese movie recap style နဲ့ စိတ်ဝင်စားစရာကောင်းအောင် ပြန်ရေးပေးပါ:\n{text}")
                    recap_text = response.text
                    st.success("Recap Generated!")
                    st.write(recap_text)
                    
                    asyncio.run(generate_voice(recap_text, voice_opt))
                    st.audio("voice.mp3")
                except Exception as e:
                    st.error(f"Error: {e}")

# ---------------- PAGE: VOICE ----------------
elif st.session_state.page == "voice":
    if st.button("⬅ Back"): st.session_state.page = "home"
    st.header("🔊 AI Voice Generator")
    
    input_text = st.text_area("စာသားထည့်ပါ (သို့မဟုတ် SRT upload လုပ်ပါ)")
    uploaded_srt = st.file_uploader("Upload SRT", type=["srt"])
    
    voices = {
        "👩 Female (Nilar)": "my-MM-NilarNeural",
        "👨 Male (Thiha)": "my-MM-ThihaNeural",
        "👩 US Female": "en-US-JennyNeural",
        "👨 US Male": "en-US-GuyNeural"
    }
    voice_label = st.selectbox("အသံရွေးချယ်ရန်", list(voices.keys()))

    if st.button("Generate Voice"):
        final_text = input_text
        if uploaded_srt:
            srt_content = uploaded_srt.read().decode("utf-8")
            final_text = srt_to_text(srt_content)
        
        if final_text:
            with st.spinner("အသံထုတ်လုပ်နေသည်..."):
                asyncio.run(generate_voice(final_text, voices[voice_label]))
                st.audio("voice.mp3")
        else:
            st.warning("စာသားထည့်သွင်းပေးပါ")

# ---------------- PAGE: TRANSLATE ----------------
elif st.session_state.page == "translate":
    if st.button("⬅ Back"): st.session_state.page = "home"
    st.header("🌍 Smart Translator")
    
    source_text = st.text_area("Translate text...", height=150)
    if st.button("Translate to Myanmar"):
        if source_text:
            res = model.generate_content(f"Translate this to natural Myanmar language:\n{source_text}")
            st.info(res.text)

# ---------------- PAGE: CONTENT ----------------
elif st.session_state.page == "content":
    if st.button("⬅ Back"): st.session_state.page = "home"
    st.header("✍️ Content Creator")
    
    topic = st.text_input("ဘာအကြောင်းရေးမလဲ?")
    if st.button("Generate Script"):
        if topic:
            res = model.generate_content(f"Write a social media video script about {topic} in Myanmar language.")
            st.write(res.text)

# ---------------- PAGE: SRT ----------------
elif st.session_state.page == "srt":
    if st.button("⬅ Back"): st.session_state.page = "home"
    st.header("📝 Video to SRT Subtitle")
    
    uploaded_video = st.file_uploader("ဗီဒီယိုတင်ပါ", type=["mp4", "mkv", "mov"])
    if uploaded_video:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(uploaded_video.read())
            path = tmp.name

        if st.button("Start Transcription"):
            with st.spinner("Whisper က နားထောင်ပြီး စာသားပြောင်းနေပါတယ်..."):
                model_w = load_whisper()
                result = model_w.transcribe(path)
                
                srt_output = ""
                for i, seg in enumerate(result["segments"]):
                    srt_output += f"{i+1}\n{format_time(seg['start'])} --> {format_time(seg['end'])}\n{seg['text']}\n\n"
                
                st.text_area("SRT Preview", srt_output, height=200)
                st.download_button("Download SRT File", srt_output, "subtitle.srt")

# ---------------- PAGE: YOUTUBE ----------------
elif st.session_state.page == "yt":
    if st.button("⬅ Back"): st.session_state.page = "home"
    st.header("📺 YouTube AI (Transcribe & Recap)")
    
    url = st.text_input("YouTube URL ကို ဒီမှာထည့်ပါ")
    voice_opt = st.selectbox("အသံရွေးပါ", ["my-MM-NilarNeural", "my-MM-ThihaNeural"])

    if st.button("Process Video"):
        if url:
            # Clean old files
            for f in glob.glob("audio.*"): os.remove(f)
            
            with st.spinner("Downloading Audio..."):
                ydl_opts = {'format': 'bestaudio/best', 'outtmpl': 'audio.%(ext)s', 'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            
            with st.spinner("Transcribing..."):
                model_w = load_whisper()
                audio_file = glob.glob("audio.*")[0]
                result = model_w.transcribe(audio_file)
                transcript = result["text"]
            
            with st.expander("Show Original Transcript"):
                st.write(transcript)

            with st.spinner("Generating Myanmar Recap..."):
                recap_res = model.generate_content(f"ဒီဗီဒီယိုအကြောင်းကို Burmese movie recap style နဲ့ ပြန်ပြောပြပါ:\n{transcript}")
                recap_text = recap_res.text
                st.success("Recap Done!")
                st.write(recap_text)
                
                asyncio.run(generate_voice(recap_text, voice_opt))
                st.audio("voice.mp3")

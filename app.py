import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Toolkit PRO", layout="wide")

genai.configure(api_key=st.secrets.get("GEMINI_API_KEY", ""))
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------- VOICE FUNCTION ----------------
async def generate_voice(text, voice):
    try:
        tts = edge_tts.Communicate(text, voice)
        await tts.save("voice.mp3")
    except:
        tts = edge_tts.Communicate(text, "th-TH-NiwatNeural")
        await tts.save("voice.mp3")

# ---------------- SESSION ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"

# ---------------- HOME ----------------
if st.session_state.page == "home":
    st.title("🚀 AI Toolkit PRO")

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

# ---------------- RECAP ----------------
elif st.session_state.page == "recap":
    st.header("🎬 Recapper")

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    text = st.text_area("Paste Transcript")

    if st.button("Generate Recap"):
        if text:
            try:
                res = model.generate_content(f"ဒီစာကို Burmese recap style နဲ့ရေး:\n{text}")
                recap = res.text
                st.write(recap)

                # voice (male style)
                asyncio.run(generate_voice(recap, "th-TH-NiwatNeural"))
                st.audio("voice.mp3")

                with open("voice.mp3", "rb") as f:
                    st.download_button("⬇️ Download Voice", f, "recap.mp3")

            except Exception as e:
                st.error(e)

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

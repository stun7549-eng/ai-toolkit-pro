import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AI Toolkit", layout="wide")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

st.title("🚀 AI Movie Recapper")

text = st.text_area("စာသားထည့်ပါ")

if st.button("Generate Recap"):
    if text:
        result = model.generate_content(
            f"ဒီစာကို Burmese movie recap style နဲ့ရေးပါ:\n{text}"
        )
        st.write(result.text)
    else:
        st.warning("စာသားထည့်ပါ")
import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts

st.set_page_config(page_title="AI Toolkit", layout="wide")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

st.title("🚀 AI Movie Recapper")

text = st.text_area("📄 စာသားထည့်ပါ")

# 🔊 Voice function
async def generate_voice(text):
    tts = edge_tts.Communicate(text, "my-MM-NilarNeural")
    await tts.save("voice.mp3")

if st.button("🎬 Generate Recap + Voice"):
    if text:
        result = model.generate_content(
            f"ဒီစာကို exciting Burmese movie recap style နဲ့ရေးပါ:\n{text}"
        )
        recap = result.text

        st.subheader("🎬 Recap Script")
        st.write(recap)

        # Generate voice
        asyncio.run(generate_voice(recap))

        # Play audio
        audio_file = open("voice.mp3", "rb")
        st.audio(audio_file.read())

    else:
        st.warning("စာသားထည့်ပါ")

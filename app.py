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

import streamlit as st

st.set_page_config(page_title="AI Toolkit", layout="wide")

st.title("🚀 Your Creative AI Toolkit")
st.write("Scripts, stories, translations, thumbnails & voices — all powered by AI")

tools = [
    "🎬 Recapper",
    "✍️ Content Creator",
    "📖 Story Creator",
    "🎨 Thumbnail",
    "🌍 Translate",
    "📝 SRT Sub",
    "📚 Novel Translator",
    "🔊 AI Voice"
]

cols = st.columns(4)

for i, tool in enumerate(tools):
    with cols[i % 4]:
        st.subheader(tool)
        if st.button("Launch →", key=tool):
            st.write(f"{tool} coming soon...")

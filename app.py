import os
import streamlit as st
from persona_defs import get_personas
from simulator import PersonaChatSession

st.set_page_config(page_title="TinyTroupe Feature Feedback Simulator", layout="wide")

OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
MODEL_NAME = st.secrets.get("MODEL_NAME", "gpt-4o-mini")

st.title("🎭 TinyTroupe Feature Feedback Simulator")
st.caption("Simulate persona-based conversations about your feature.")

feature = st.text_area(
    "🍀 Describe your feature",
    placeholder="E.g., A new 'Dark Mode' toggle with schedule and per-screen overrides…",
    height=140
)
persona_names = list(get_personas().keys())
selected = st.selectbox("🧍 Choose a persona", persona_names)

if "chat" not in st.session_state:
    st.session_state.chat = None

if st.button("Start / Reset Conversation", use_container_width=True):
    st.session_state.chat = PersonaChatSession(
        persona_name=selected,
        feature_description=feature.strip(),
        openai_api_key=OPENAI_API_KEY,
        model_name=MODEL_NAME
    )

if st.session_state.chat is None and feature.strip():
    st.session_state.chat = PersonaChatSession(
        persona_name=selected,
        feature_description=feature.strip(),
        openai_api_key=OPENAI_API_KEY,
        model_name=MODEL_NAME
    )

chat = st.session_state.chat

if chat:
    with st.container(border=True):
        meta = chat.persona_meta
        st.write(
            f"**Persona:** {meta['name']} ({meta['occupation']}, {meta['age']})  \n"
            f"**Traits:** {', '.join(meta['traits'])}  \n"
            f"**Interests:** {', '.join(meta['interests'])}"
        )
        if chat.feature_description:
            st.write(f"**Feature:** {chat.feature_description}")

    for role, content in chat.history:
        with st.chat_message("user" if role == "user" else "assistant"):
            st.markdown(content)

    prompt = st.chat_input("Ask the persona a follow-up…")
    if prompt:
        chat.add_user(prompt)
        with st.chat_message("user"):
            st.markdown(prompt)
        reply = chat.reply()
        with st.chat_message("assistant"):
            st.markdown(reply)
else:
    st.info("Enter a feature, choose a persona, then click **Start / Reset Conversation**.")

import os
import io
from datetime import datetime
import streamlit as st
import pandas as pd

from persona_defs import get_personas
from simulator import PersonaChatSession, simulate_once_for_persona

# ---------- Page setup ----------
st.set_page_config(page_title="TinyTroupe Feature Feedback Simulator", layout="wide")
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
MODEL_NAME = st.secrets.get("MODEL_NAME", "gpt-4o-mini")

st.title("🎭 TinyTroupe Feature Feedback Simulator")
st.caption("Simulate persona-based conversations and compare feedback across user types.")

# ---------- Inputs (shared) ----------
feature = st.text_area(
    "🍀 Describe your feature",
    placeholder="E.g., A new 'Dark Mode' toggle with schedule and per-screen overrides…",
    height=140
)

personas_dict = get_personas()
persona_names = list(personas_dict.keys())

# ---------- Tabs ----------
tab_chat, tab_compare = st.tabs(["💬 Chat with one persona", "🧪 Compare personas"])

# ==============================
# Tab 1: Chat (multi-turn)
# ==============================
with tab_chat:
    selected = st.selectbox("🧍 Choose a persona", persona_names, key="chat_persona")

    if "chat_session" not in st.session_state:
        st.session_state.chat_session = None

    cols = st.columns([1, 1])
    with cols[0]:
        if st.button("Start / Reset Conversation", use_container_width=True):
            st.session_state.chat_session = PersonaChatSession(
                persona_name=selected,
                feature_description=feature.strip(),
                openai_api_key=OPENAI_API_KEY,
                model_name=MODEL_NAME
            )
    with cols[1]:
        clear_only = st.button("Clear Messages (keep persona/feature)", use_container_width=True)

    if st.session_state.chat_session is None and feature.strip():
        # Auto-seed a session on first load if a feature exists
        st.session_state.chat_session = PersonaChatSession(
            persona_name=selected,
            feature_description=feature.strip(),
            openai_api_key=OPENAI_API_KEY,
            model_name=MODEL_NAME
        )

    chat = st.session_state.chat_session

    if clear_only and chat:
        # Recreate with same persona/feature
        st.session_state.chat_session = PersonaChatSession(
            persona_name=selected,
            feature_description=chat.feature_description,
            openai_api_key=OPENAI_API_KEY,
            model_name=MODEL_NAME
        )
        chat = st.session_state.chat_session

    if chat:
        # Persona header
        with st.container(border=True):
            meta = chat.persona_meta
            st.markdown(
                f"**Persona:** {meta['name']} ({meta['occupation']}, {meta['age']})  \n"
                f"**Traits:** {', '.join(meta['traits'])}  \n"
                f"**Interests:** {', '.join(meta['interests'])}"
            )
            if chat.feature_description:
                st.markdown(f"**Feature:** {chat.feature_description}")

        # History
        for role, content in chat.history:
            with st.chat_message("user" if role == "user" else "assistant"):
                st.markdown(content)

        # Input + reply
        user_msg = st.chat_input("Ask the persona a follow-up…")
        if user_msg:
            chat.add_user(user_msg)
            with st.chat_message("user"):
                st.markdown(user_msg)
            reply = chat.reply()
            with st.chat_message("assistant"):
                st.markdown(reply)

        # ---- Export conversation as .md
        def _conversation_markdown():
            lines = [
                f"# Persona: {chat.persona_meta['name']}",
                f"**Occupation/Age:** {chat.persona_meta['occupation']}, {chat.persona_meta['age']}",
                f"**Traits:** {', '.join(chat.persona_meta['traits'])}",
                f"**Interests:** {', '.join(chat.persona_meta['interests'])}",
                f"**Feature:** {chat.feature_description or '(none)'}",
                "",
                "## Conversation",
            ]
            for role, msg in chat.history:
                who = "User" if role == "user" else chat.persona_meta["name"]
                lines.append(f"**{who}:** {msg}")
                lines.append("")
            return "\n".join(lines)

        md_bytes = _conversation_markdown().encode("utf-8")
        file_name = f"{chat.persona_meta['name'].lower().replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
        st.download_button("💾 Download conversation (.md)", data=md_bytes, file_name=file_name, mime="text/markdown")

    else:
        st.info("Enter a feature, choose a persona, then click **Start / Reset Conversation**.")

# ==============================
# Tab 2: Compare Personas (one-shot)
# ==============================
with tab_compare:
    sel_many = st.multiselect("👥 Choose personas to compare", persona_names, default=persona_names)
    run = st.button("Run Comparison", type="primary")
    if run:
        results = []
        for p in sel_many:
            text = simulate_once_for_persona(
                feature_description=feature.strip(),
                persona_name=p,
            )
            results.append({"Persona": p, "Feedback": text})

        # Show each feedback in an expander
        for row in results:
            with st.expander(row["Persona"], expanded=False):
                st.markdown(row["Feedback"])

        # Optional: quick table + CSV download
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download comparison (.csv)", data=csv_bytes, file_name="persona_comparison.csv", mime="text/csv")

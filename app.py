import os, streamlit as st
from simulator import simulate_feedback
from personas import get_personas

st.set_page_config(page_title="TinyTroupe Feature Feedback", layout="wide")

OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
# (Later you’ll pass OPENAI_API_KEY into TinyTroupe/OpenAI client)

st.title("🎭 TinyTroupe Feature Feedback Simulator")
st.caption("Simulate persona-based feedback for product features.")

feature = st.text_area(
    "🧩 Describe your feature",
    placeholder="E.g., A new 'Dark Mode' toggle with schedule and per-screen overrides…",
    height=140
)
persona_names = list(get_personas().keys())
selected = st.selectbox("🧍 Choose a persona", persona_names)

col1, col2 = st.columns([1,1])
with col1:
    if st.button("Run Simulation", use_container_width=True):
        if not feature.strip():
            st.warning("Please enter a feature description.")
        else:
            with st.spinner(f"Simulating feedback from {selected}…"):
                out = simulate_feedback(feature, selected)
                st.markdown("### 💬 Persona Feedback")
                st.code(out)
with col2:
    st.info("Tips:\n- Add more personas in `personas.py`.\n- Store your keys in **Secrets**.")


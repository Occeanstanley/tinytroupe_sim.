# simulator.py
from personas import get_personas

# Try to import TinyTroupe, but allow a graceful fallback
try:
    from tinytroupe.agents import TinyAgent
    from tinytroupe.group import TinyGroup
    TINYTROUPE_AVAILABLE = True
except Exception:
    TINYTROUPE_AVAILABLE = False

def _placeholder_feedback(p, feature_description: str) -> str:
    return (
        f"Persona: {p.name} ({p.occupation}, {p.age})\n"
        f"Traits: {', '.join(p.traits)}\n\n"
        f"Feedback on feature:\n"
        f"- First impression: The idea seems useful for {p.interests[0]}.\n"
        f"- Concerns: onboarding clarity, cognitive load, and accessibility.\n"
        f"- Suggestion: Provide a quick tutorial and an undo option."
    )

def simulate_feedback(feature_description: str, selected_persona: str) -> str:
    personas = get_personas()
    p = personas[selected_persona]

    # Use TinyTroupe if installed; otherwise use placeholder
    if not TINYTROUPE_AVAILABLE:
        return _placeholder_feedback(p, feature_description)

    # --- TinyTroupe path ---
    tt_persona = {
        "name": p.name,
        "age": p.age,
        "occupation": p.occupation,
        "traits": p.traits,
        "interests": p.interests,
    }

    group = TinyGroup(personas=[tt_persona])
    agent = TinyAgent(tt_persona)

    prompt = (
        f"You are {p.name} ({p.occupation}, {p.age}).\n"
        f"Feature: {feature_description}\n\n"
        "Give concise feedback in 4 bullets: first impression, usability risks, "
        "accessibility concerns, and concrete suggestions."
    )

    try:
        response = agent.act(prompt)
        return response
    except Exception:
        # If TinyTroupe fails at runtime, still return something useful
        return _placeholder_feedback(p, feature_description)

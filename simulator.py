from tinytroupe.agents import TinyAgent
from tinytroupe.group import TinyGroup
from personas import get_personas

def simulate_feedback(feature_description: str, selected_persona: str) -> str:
    personas = get_personas()
    p = personas[selected_persona]

    # Build a TinyTroupe persona (map your PersonaSpec → TinyTroupe persona dict)
    tt_persona = {
        "name": p.name,
        "age": p.age,
        "occupation": p.occupation,
        "traits": p.traits,
        "interests": p.interests
    }

    group = TinyGroup(personas=[tt_persona])
    agent = TinyAgent(tt_persona)

    prompt = (
        f"You are {p.name} ({p.occupation}, {p.age}). "
        f"Here’s the new feature: {feature_description}\n\n"
        "Give feedback in 4 bullets: first impression, usability risks, accessibility concerns, and concrete suggestions."
    )

    response = agent.act(prompt)
    return response

from personas import get_personas

def simulate_feedback(feature_description: str, selected_persona: str) -> str:
    p = get_personas()[selected_persona]
    # TODO: replace with TinyTroupe agent calls; this is a placeholder shape
    return (
        f"Persona: {p.name} ({p.occupation}, {p.age})\n"
        f"Traits: {', '.join(p.traits)}\n\n"
        f"Feedback on feature:\n"
        f"- First impression: The idea seems useful for {p.interests[0]}.\n"
        f"- Concerns: onboarding clarity, cognitive load, and accessibility.\n"
        f"- Suggestion: Provide a quick tutorial and an undo option."
    )

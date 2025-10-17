from typing import List, Tuple
from persona_defs import get_personas

# Try TinyTroupe; if unavailable, the app still works with a conversational fallback
try:
    from tinytroupe.agents import TinyAgent
    from tinytroupe.group import TinyGroup
    TINYTROUPE_AVAILABLE = True
except Exception:
    TINYTROUPE_AVAILABLE = False


class PersonaChatSession:
    """
    Multi-turn conversation wrapper.
    Uses TinyTroupe when available; otherwise a lightweight heuristic bot.
    """
    def __init__(self, persona_name: str, feature_description: str, openai_api_key: str = None, model_name: str = None):
        personas = get_personas()
        self.persona = personas[persona_name]
        self.feature_description = feature_description
        self.history: List[Tuple[str, str]] = []
        self.persona_meta = {
            "name": self.persona.name,
            "age": self.persona.age,
            "occupation": self.persona.occupation,
            "traits": self.persona.traits,
            "interests": self.persona.interests,
        }

        self._agent = None
        if TINYTROUPE_AVAILABLE:
            tt_persona = {
                "name": self.persona.name,
                "age": self.persona.age,
                "occupation": self.persona.occupation,
                "traits": self.persona.traits,
                "interests": self.persona.interests,
            }
            self._group = TinyGroup(personas=[tt_persona])
            self._agent = TinyAgent(tt_persona)

        # Seed opening line
        opening = self._opening_line()
        self.history.append(("assistant", opening))

    # ----- conversation methods -----
    def add_user(self, msg: str):
        self.history.append(("user", msg))

    def reply(self) -> str:
        last_user = self.history[-1][1] if self.history and self.history[-1][0] == "user" else ""
        if TINYTROUPE_AVAILABLE and self._agent:
            prompt = self._build_prompt(last_user)
            try:
                resp = self._agent.act(prompt)
            except Exception:
                resp = self._fallback_reply(last_user)
        else:
            resp = self._fallback_reply(last_user)
        self.history.append(("assistant", resp))
        return resp

    # ----- helpers -----
    def _opening_line(self) -> str:
        p = self.persona
        if not self.feature_description:
            return f"Hi, I’m {p.name}, a {p.age}-year-old {p.occupation}. Tell me about your feature."
        return (f"Hi, I’m {p.name} ({p.occupation}). About this feature — *{self.feature_description}* — "
                "I’ll share reactions, questions, and concerns as we chat. What would you like me to try first?")

    def _build_prompt(self, user_msg: str) -> str:
        p = self.persona
        return (
            f"You are {p.name}, a {p.age}-year-old {p.occupation} with traits {p.traits} and interests {p.interests}. "
            f"Stay in character, speaking as a real user. The feature is: {self.feature_description}. "
            "Respond conversationally (2–6 sentences) and include:\n"
            "- emotional reaction\n- usability positives/risks\n- concrete suggestions\n"
            "- a confidence score (0–1) and one-line reasoning\n\n"
            f"User says: {user_msg}"
        )

    def _fallback_reply(self, user_msg: str) -> str:
        p = self.persona
        topic = user_msg or "this feature"
        return (
            f"As {p.name}: For {topic}, I’d try the most obvious path first. "
            "Potential friction: unclear labels, cognitive load, and accessibility. "
            "Suggestion: guided tips, sensible defaults, and an easy undo. Confidence: 0.6 (based on prior apps)."
        )


# -------- One-shot simulation for comparison tab --------
def simulate_once_for_persona(feature_description: str, persona_name: str) -> str:
    personas = get_personas()
    p = personas[persona_name]

    if TINYTROUPE_AVAILABLE:
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
            f"You are {p.name} ({p.occupation}, {p.age}). Feature: {feature_description}. "
            "Give structured feedback with bullets for: first impression, usability, accessibility, "
            "and 2 concrete suggestions. End with 'Confidence: <0-1>'."
        )
        try:
            return agent.act(prompt)
        except Exception:
            pass  # fall through to heuristic

    # Fallback text
    return (
        f"Persona: {p.name} ({p.occupation}, {p.age})\n"
        f"- First impression: Promising for {p.interests[0]}.\n"
        "- Usability: Might need clearer labels and defaults.\n"
        "- Accessibility: Ensure readable text and large tap targets.\n"
        "- Suggestions: Add a short tutorial and an undo/rollback.\n"
        "Confidence: 0.6"
    )

# simulator.py
from typing import List, Tuple
from personas import get_personas

# Try TinyTroupe; if not available, we still provide a conversational fallback.
try:
    from tinytroupe.agents import TinyAgent
    from tinytroupe.group import TinyGroup
    TINYTROUPE_AVAILABLE = True
except Exception:
    TINYTROUPE_AVAILABLE = False


class PersonaChatSession:
    """
    Wraps a persona-focused, multi-turn conversation.
    Uses TinyTroupe when available; otherwise a lightweight heuristic bot.
    """
    def __init__(self, persona_name: str, feature_description: str, openai_api_key: str = None, model_name: str = None):
        personas = get_personas()
        self.persona = personas[persona_name]
        self.feature_description = feature_description
        self.history: List[Tuple[str, str]] = []

        # Minimal metadata for display
        self.persona_meta = {
            "name": self.persona.name,
            "age": self.persona.age,
            "occupation": self.persona.occupation,
            "traits": self.persona.traits,
            "interests": self.persona.interests,
        }

        # Build TinyTroupe agent if possible
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

        # Seed conversation with an opening line from the persona about the feature
        opening = self._opening_line()
        self.history.append(("assistant", opening))

    # -------- Core conversation methods --------
    def add_user(self, msg: str):
        self.history.append(("user", msg))

    def reply(self) -> str:
        """
        Persona replies to the last user message.
        """
        user_msg = self.history[-1][1] if self.history and self.history[-1][0] == "user" else ""
        if TINYTROUPE_AVAILABLE and self._agent:
            prompt = self._build_prompt(user_msg)
            try:
                resp = self._agent.act(prompt)
                self.history.append(("assistant", resp))
                return resp
            except Exception:
                # Fall back if runtime error occurs
                resp = self._fallback_reply(user_msg)
                self.history.append(("assistant", resp))
                return resp
        else:
            resp = self._fallback_reply(user_msg)
            self.history.append(("assistant", resp))
            return resp

    # -------- Helpers --------
    def _opening_line(self) -> str:
        p = self.persona
        if not self.feature_description:
            return (f"Hi, I’m {p.name}, a {p.age}-year-old {p.occupation}. "
                    "Tell me about your feature and I’ll react as a typical user like me.")
        return (
            f"Hi, I’m {p.name} ({p.occupation}). About this feature — *{self.feature_description}* — "
            "I’ll share reactions, questions, and concerns as we chat. What would you like me to try first?"
        )

    def _build_prompt(self, user_msg: str) -> str:
        p = self.persona
        return (
            f"You are {p.name}, a {p.age}-year-old {p.occupation} with traits {p.traits} and interests {p.interests}. "
            f"Stay in character, speaking as a real user. The feature is: {self.feature_description}. "
            "Respond conversationally (2–6 sentences), covering:\n"
            "- how you'd attempt the task\n"
            "- any confusion, friction, or risks\n"
            "- concrete suggestions or follow-up questions\n\n"
            f"User says: {user_msg}"
        )

    def _fallback_reply(self, user_msg: str) -> str:
        # Simple heuristic conversation when TinyTroupe isn't available
        p = self.persona
        concerns = ["onboarding clarity", "cognitive load", "accessibility"]
        tip = "Maybe add a short guided tutorial and an undo/rollback."
        return (
            f"As {p.name}: I’d try to {('use that' if not user_msg else 'address: ' + user_msg)}. "
            f"My first concerns are {concerns[0]}, {concerns[1]}, and {concerns[2]}. "
            f"I’d appreciate clearer labels, defaults that match typical behavior, and better error recovery. {tip}"
        )

from typing import List, Tuple
from persona_defs import get_personas

try:
    from tinytroupe.agents import TinyAgent
    from tinytroupe.group import TinyGroup
    TINYTROUPE_AVAILABLE = True
except Exception:
    TINYTROUPE_AVAILABLE = False

class PersonaChatSession:
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

        opening = self._opening_line()
        self.history.append(("assistant", opening))

    def add_user(self, msg: str):
        self.history.append(("user", msg))

    def reply(self) -> str:
        user_msg = self.history[-1][1] if self.history and self.history[-1][0] == "user" else ""
        if TINYTROUPE_AVAILABLE and self._agent:
            prompt = self._build_prompt(user_msg)
            try:
                resp = self._agent.act(prompt)
            except Exception:
                resp = self._fallback_reply(user_msg)
        else:
            resp = self._fallback_reply(user_msg)
        self.history.append(("assistant", resp))
        return resp

    def _opening_line(self) -> str:
        p = self.persona
        if not self.feature_description:
            return f"Hi, I’m {p.name}, a {p.age}-year-old {p.occupation}. Tell me about your feature."
        return (f"Hi, I’m {p.name} ({p.occupation}). About this feature — *{self.feature_description}*. "
                "I’ll react as we chat. What would you like me to try first?")

    def _build_prompt(self, user_msg: str) -> str:
        p = self.persona
        return (
            f"You are {p.name}, a {p.age}-year-old {p.occupation} with traits {p.traits} and interests {p.interests}. "
            f"Stay in character. The feature is: {self.feature_description}. "
            "Reply in 2–6 sentences covering how you'd attempt the task, confusion/friction, and concrete suggestions.\n\n"
            f"User: {user_msg}"
        )

    def _fallback_reply(self, user_msg: str) -> str:
        p = self.persona
        return (f"As {p.name}: considering '{user_msg or 'the feature'}', I’d try the most obvious path first. "
                "Potential friction: unclear labels, cognitive load, and accessibility. "
                "Suggestion: guided tips, sensible defaults, and an undo option.")

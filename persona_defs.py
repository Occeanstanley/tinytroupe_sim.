# persona_defs.py
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class PersonaSpec:
    name: str
    age: int
    occupation: str
    traits: List[str]
    interests: List[str]

def get_personas() -> Dict[str, PersonaSpec]:
    return {
        "Tech-Savvy User": PersonaSpec(
            name="Alex", age=28, occupation="Software Engineer",
            traits=["Analytical", "Early Adopter", "Detail-Oriented"],
            interests=["UI design", "performance", "automation"]
        ),
        "Casual User": PersonaSpec(
            name="Jamie", age=35, occupation="Teacher",
            traits=["Practical", "Non-technical"],
            interests=["ease of use", "affordability"]
        ),
        "Elderly User": PersonaSpec(
            name="Helen", age=65, occupation="Retired Nurse",
            traits=["Cautious", "Patient"],
            interests=["Accessibility", "Clear instructions"]
        ),
    }

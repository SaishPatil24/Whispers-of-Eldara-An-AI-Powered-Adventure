# game_config.py
from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

class Mood(Enum):
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    HOSTILE = "hostile"

@dataclass
class Memory:
    interaction: str
    impact: int  # -1 to 1
    turn: int

@dataclass
class NPC:
    name: str
    base_personality: str
    current_mood: Mood
    memories: List[Memory]
    trust_level: int = 50

@dataclass
class Location:
    name: str
    description: str
    connected_locations: List[str]
    npcs: List[str]

# Initial game data
INITIAL_LOCATIONS = {
    "town_square": Location(
        "Town Square",
        "A bustling town square with a fountain in the center.",
        ["tavern", "market"],
        ["merchant", "guard"]
    ),
    "tavern": Location(
        "Tavern",
        "A cozy tavern with a warm fireplace.",
        ["town_square"],
        ["innkeeper"]
    ),
    "market": Location(
        "Market",
        "A busy market with various stalls.",
        ["town_square"],
        ["merchant"]
    )
}

INITIAL_NPCS = {
    "merchant": {
        "name": "Marcus",
        "personality": "A shrewd but fair merchant who values honest dealings",
        "initial_mood": Mood.NEUTRAL
    },
    "guard": {
        "name": "Elena",
        "personality": "A vigilant town guard with a strong sense of justice",
        "initial_mood": Mood.NEUTRAL
    },
    "innkeeper": {
        "name": "Old Tom",
        "personality": "A friendly innkeeper who loves sharing local gossip",
        "initial_mood": Mood.FRIENDLY
    }
}

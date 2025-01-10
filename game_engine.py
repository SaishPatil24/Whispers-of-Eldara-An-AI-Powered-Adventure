# game_engine.py
import os
from typing import List, Dict, Optional
import openai
from dotenv import load_dotenv
from game_config import *

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class GameState:
    def __init__(self):
        self.turn = 0
        self.current_location: str = "town_square"
        self.inventory: List[str] = []
        self.locations: Dict[str, Location] = INITIAL_LOCATIONS.copy()
        self.npcs: Dict[str, NPC] = self._init_npcs()
    
    def _init_npcs(self) -> Dict[str, NPC]:
        return {
            npc_id: NPC(
                name=data["name"],
                base_personality=data["personality"],
                current_mood=data["initial_mood"],
                memories=[],
                trust_level=50
            )
            for npc_id, data in INITIAL_NPCS.items()
        }

class Game:
    def __init__(self):
        self.state = GameState()
    
    async def get_npc_response(self, npc: NPC, player_input: str) -> str:
        # Construct context from NPC's memories and personality
        recent_memories = sorted(npc.memories, key=lambda m: m.turn, reverse=True)[:3]
        memory_context = "\n".join([m.interaction for m in recent_memories])
        
        prompt = f"""
        You are {npc.name}, {npc.base_personality}.
        Your current mood is {npc.current_mood.value}.
        
        Recent interactions:
        {memory_context}
        
        The player says: {player_input}
        
        Respond in character, considering your personality, mood, and past interactions.
        """
        
        try:
            response = await openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": player_input}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"{npc.name} seems unable to respond at the moment."
    
    def process_command(self, command: str) -> str:
        self.state.turn += 1
        
        if command == "look":
            return self._look()
        elif command == "inventory":
            return self._check_inventory()
        elif command.startswith("go to "):
            destination = command[6:]
            return self._move_to(destination)
        elif command.startswith("talk to "):
            npc_name = command[8:]
            return self._talk_to(npc_name)
        else:
            return "I don't understand that command."
    
    def _look(self) -> str:
        location = self.state.locations[self.state.current_location]
        npcs_here = [self.state.npcs[npc].name for npc in location.npcs]
        npc_text = f"\nPresent: {', '.join(npcs_here)}" if npcs_here else ""
        exits_text = f"\nExits: {', '.join(location.connected_locations)}"
        return f"{location.name}\n{location.description}{npc_text}{exits_text}"
    
    def _check_inventory(self) -> str:
        if not self.state.inventory:
            return "Your inventory is empty."
        return f"You are carrying: {', '.join(self.state.inventory)}"
    
    def _move_to(self, destination: str) -> str:
        current_location = self.state.locations[self.state.current_location]
        if destination not in current_location.connected_locations:
            return f"You can't go to {destination} from here."
        self.state.current_location = destination
        return self._look()
    
    async def _talk_to(self, npc_name: str) -> str:
        location = self.state.locations[self.state.current_location]
        if npc_name not in location.npcs:
            return f"{npc_name} is not here."
        
        npc = self.state.npcs[npc_name]
        player_input = input(f"What would you like to say to {npc.name}? ")
        
        response = await self.get_npc_response(npc, player_input)
        
        # Update NPC memory
        impact = 0.5  # This could be determined by sentiment analysis
        npc.memories.append(Memory(
            interaction=f"Player said: {player_input}",
            impact=impact,
            turn=self.state.turn
        ))
        
        return response

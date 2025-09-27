
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
import random

@dataclass
class Player:
    name: str
    age: int
    strength: int
    technique: int
    speed: int
    morale: int
    personality: str = "Neutro"
    isLegendary: bool = False

    def overall(self) -> int:
        return round((self.strength + self.technique + self.speed) / 3)

    def train(self, focus: str):
        delta = random.randint(1, 3)
        if focus == "strength": self.strength += delta
        elif focus == "technique": self.technique += delta
        elif focus == "speed": self.speed += delta
        elif focus == "morale": self.morale = min(100, self.morale + 1)

@dataclass
class Club:
    name: str
    state_abbr: str
    state_name: str
    budget: int
    squad: List[Player] = field(default_factory=list)
    youth: List[Player]  = field(default_factory=list)
    points: int = 0
    goals_for: int = 0
    goals_against: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0

    def rating(self) -> float:
        if not self.squad: return 50.0
        return sum(p.overall() for p in self.squad) / len(self.squad)

    def register_result(self, gf: int, ga: int):
        self.goals_for += gf
        self.goals_against += ga
        if gf > ga: 
            self.wins += 1; self.points += 3
        elif gf == ga:
            self.draws += 1; self.points += 1
        else:
            self.losses += 1

def make_player(d: Dict) -> Player:
    return Player(**d)

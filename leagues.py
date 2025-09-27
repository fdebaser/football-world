
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import random

from .models import Club

@dataclass
class Fixture:
    week: int
    home: str
    away: str

class StateLeague:
    """Campeonato estadual com turno e returno (round-robin duplo).
    Gera tabela de confrontos (fixtures) e aponta a semana atual.
    """
    def __init__(self, state_abbr: str, clubs: List[Club], seed: int = 42):
        # mantém apenas clubes do estado
        self.state_abbr = state_abbr
        self.clubs = [c for c in clubs if c.state_abbr == state_abbr]
        self.rng = random.Random(seed)
        self.fixtures: List[Fixture] = []
        self._build_double_round_robin()

        self.total_weeks = max((f.week for f in self.fixtures), default=0)
        self.current_week: int = 1

    def _build_double_round_robin(self):
        teams = [c.name for c in self.clubs]
        n = len(teams)
        if n % 2 == 1:
            teams.append("BYE")  # se ímpar, adiciona BYE
            n += 1
        # Algoritmo do círculo para round-robin
        left = teams[: n//2]
        right = teams[n//2:][::-1]

        week = 1
        rounds: List[List[Tuple[str, str]]] = []
        for _ in range(n-1):
            pairs = []
            for i in range(n//2):
                home, away = left[i], right[i]
                if "BYE" not in (home, away):
                    pairs.append((home, away))
            rounds.append(pairs)
            # rotaciona
            keep = left[0]
            left = [keep] + [right[0]] + left[1:-0 if len(left)>1 else None]
            right = right[1:] + [left[-1]]
            left = left[:-1]

        # turno (ida)
        for r in rounds:
            for h,a in r:
                self.fixtures.append(Fixture(week=week, home=h, away=a))
            week += 1
        # returno (volta) invertendo mandos
        for r in rounds:
            for h,a in r:
                self.fixtures.append(Fixture(week=week, home=a, away=h))
            week += 1

    def fixtures_of_week(self, week: int) -> List[Fixture]:
        return [f for f in self.fixtures if f.week == week]

    def advance_week(self):
        if self.current_week < self.total_weeks:
            self.current_week += 1

    def is_finished(self) -> bool:
        return self.current_week > self.total_weeks

    def serialize(self) -> Dict:
        return {
            "state_abbr": self.state_abbr,
            "current_week": self.current_week,
            "fixtures": [f.__dict__ for f in self.fixtures],
            "seed": self.rng.seed if hasattr(self.rng, "seed") else 42,
        }

    @staticmethod
    def deserialize(data: Dict, clubs: List[Club]) -> "StateLeague":
        lg = StateLeague(data["state_abbr"], clubs, seed=data.get("seed", 42))
        # overwrite generated fixtures with saved ones to preserve week mapping
        lg.fixtures = [Fixture(**f) for f in data["fixtures"]]
        lg.current_week = data["current_week"]
        lg.total_weeks = max((f.week for f in lg.fixtures), default=0)
        return lg

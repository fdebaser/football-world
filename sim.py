
from __future__ import annotations
from typing import List, Dict, Tuple
from dataclasses import dataclass
import random

from .models import Club, Player, make_player

EVENTS = [
    "Cartão amarelo",
    "Cartão vermelho",
    "Lesão leve",
    "Lesão grave",
    "Gol",
    "Impedimento",
    "Defesa espetacular",
]

@dataclass
class MatchEvent:
    minute: int
    club: str
    player: str
    kind: str

@dataclass
class MatchResult:
    home: str
    away: str
    goals_home: int
    goals_away: int
    timeline: List[MatchEvent]

class MatchEngine:
    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()

    def simulate(self, home: Club, away: Club) -> MatchResult:
        # força esperada baseada no rating
        hr = home.rating()
        ar = away.rating()
        base = (hr + ar) / 2.0
        # média de gols ~ Poisson via aproximação
        mean_home = max(0.4, (hr / (ar + 1e-6)) * 1.0)
        mean_away = max(0.4, (ar / (hr + 1e-6)) * 1.0)

        goals_home = self._poisson(mean_home)
        goals_away = self._poisson(mean_away)

        timeline: List[MatchEvent] = []
        minutes = list(range(1, 91))
        self.rng.shuffle(minutes)
        minutes = minutes[: self.rng.randint(6, 16)]  # 6 a 16 eventos

        def pick_player(club: Club) -> Player:
            return self.rng.choice(club.squad)

        # espalha eventos aleatórios e inclui os gols nos minutos
        for m in sorted(minutes):
            pick = self.rng.random()
            if pick < 0.15 and goals_home > 0:
                p = pick_player(home); goals_home -= 1
                timeline.append(MatchEvent(m, home.name, p.name, "Gol"))
            elif pick < 0.30 and goals_away > 0:
                p = pick_player(away); goals_away -= 1
                timeline.append(MatchEvent(m, away.name, p.name, "Gol"))
            else:
                # outro evento
                club = home if self.rng.random() < 0.5 else away
                p = pick_player(club)
                kind = self.rng.choice([e for e in EVENTS if e != "Gol"])
                timeline.append(MatchEvent(m, club.name, p.name, kind))

        # corrige se sobrou gol não registrado na timeline
        # adiciona nos minutos finais
        for _ in range(goals_home):
            p = pick_player(home); timeline.append(MatchEvent(self.rng.randint(80,90), home.name, p.name, "Gol"))
        for _ in range(goals_away):
            p = pick_player(away); timeline.append(MatchEvent(self.rng.randint(80,90), away.name, p.name, "Gol"))

        # contabiliza
        h_g = sum(1 for ev in timeline if ev.club == home.name and ev.kind == "Gol")
        a_g = sum(1 for ev in timeline if ev.club == away.name and ev.kind == "Gol")

        home.register_result(h_g, a_g)
        away.register_result(a_g, h_g)

        return MatchResult(home.name, away.name, h_g, a_g, sorted(timeline, key=lambda x: x.minute))

    def _poisson(self, lam: float) -> int:
        # Knuth
        L = pow(2.718281828, -lam)
        k = 0
        p = 1.0
        while p > L:
            k += 1
            p *= self.rng.random()
        return max(0, k - 1)

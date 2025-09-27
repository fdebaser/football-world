
from __future__ import annotations
from typing import Dict, Any, List
from dataclasses import asdict
import json, os

from .models import Club, Player, make_player
from .leagues import StateLeague

def save_game(filepath: str, clubs: List[Club], meta: Dict[str, Any], state_league: StateLeague | None = None) -> None:
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    data = {
        "meta": meta,
        "clubs": [
            {
                "name": c.name,
                "state_abbr": c.state_abbr,
                "state_name": c.state_name,
                "budget": c.budget,
                "points": c.points,
                "goals_for": c.goals_for,
                "goals_against": c.goals_against,
                "wins": c.wins,
                "draws": c.draws,
                "losses": c.losses,
                "squad": [asdict(p) for p in c.squad],
                "youth": [asdict(p) for p in c.youth],
            }
            for c in clubs
        ],
        "state_league": state_league.serialize() if state_league else None,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_game(filepath: str) -> tuple[list[Club], Dict[str, Any], StateLeague | None]:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    clubs = []
    for c in data["clubs"]:
        club = Club(
            name=c["name"],
            state_abbr=c["state_abbr"],
            state_name=c["state_name"],
            budget=c["budget"],
            squad=[make_player(p) for p in c["squad"]],
            youth=[make_player(p) for p in c["youth"]],
            points=c.get("points", 0),
            goals_for=c.get("goals_for", 0),
            goals_against=c.get("goals_against", 0),
            wins=c.get("wins", 0),
            draws=c.get("draws", 0),
            losses=c.get("losses", 0),
        )
        clubs.append(club)
    state_league = None
    if data.get("state_league"):
        from .leagues import StateLeague
        state_league = StateLeague.deserialize(data["state_league"], clubs)
    return clubs, data.get("meta", {}), state_league

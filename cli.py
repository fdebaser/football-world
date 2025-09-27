
from __future__ import annotations
import os, sys, json, random
from typing import List, Dict, Tuple
from dataclasses import dataclass

from .data import generate_club_rosters, BR_STATES
from .models import Player, Club, make_player
from .sim import MatchEngine
from .persistence import save_game, load_game

SAVE_FILE = "saves/career.save.json"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def press_enter():
    input("\nPressione Enter para continuar...")

def pick_state() -> tuple[str,str]:
    clear()
    print("Escolha seu estado de origem:\n")
    for i, (abbr, name) in enumerate(BR_STATES, start=1):
        print(f"{i:2d}. {name} ({abbr})")
    print()
    while True:
        try:
            idx = int(input("Número do estado: "))
            if 1 <= idx <= len(BR_STATES):
                return BR_STATES[idx-1]
        except ValueError:
            pass
        print("Entrada inválida.")

def pick_club(clubs: List[Club]) -> Club:
    clear()
    print("Escolha seu clube:\n")
    for i, club in enumerate(clubs, start=1):
        print(f"{i:2d}. {club.name} - {club.state_name}")
    while True:
        try:
            idx = int(input("\nNúmero do clube: "))
            if 1 <= idx <= len(clubs):
                return clubs[idx-1]
        except ValueError:
            pass
        print("Entrada inválida.")

def new_game():
    clear()
    print("=== NOVA CARREIRA ===\n")
    coach = input("Seu nome: ").strip() or "Treinador"
    abbr, state = pick_state()

    # gera universo
    seed = random.randint(1, 1_000_000)
    data = generate_club_rosters(clubs_per_state=6, seniors_per_club=28, youth_per_club=18, seed=seed)

    # cria objetos Club
    clubs: List[Club] = []
    for (s_abbr, s_name), club_list in data.items():
        for cd in club_list:
            c = Club(
                name=cd["name"],
                state_abbr=cd["state_abbr"],
                state_name=cd["state_name"],
                budget=cd["budget"],
                squad=[make_player(p) for p in cd["squad"]],
                youth=[make_player(p) for p in cd["youth"]],
            )
            clubs.append(c)

    # escolhe clube do estado
    my_clubs = [c for c in clubs if c.state_abbr == abbr]
    my_team = pick_club(my_clubs)

    meta = {
        "coach": coach,
        "seed": seed,
        "season": 1,
        "week": 1,
        "team": my_team.name,
        "state": state,
    }
    save_game(SAVE_FILE, clubs, meta)
    return clubs, meta

def load_or_new():
    if os.path.exists(SAVE_FILE):
        ans = input("Carregar carreira existente? [S/n] ").strip().lower()
        if ans in ("", "s", "sim", "y"):
            return load_game(SAVE_FILE)
    return new_game()

def show_team(club: Club):
    clear()
    print(f"{club.name} — {club.state_name} | Orçamento: R$ {club.budget:,}")
    print("=== PROFISSIONAL ({} jogadores) ===".format(len(club.squad)))
    for i,p in enumerate(club.squad, start=1):
        print(f"{i:2d}. {p.name:22s} {p.age:2d}a  OVR {p.overall():3d}  ({p.personality})")
    print("\n=== BASE ({} jogadores) ===".format(len(club.youth)))
    for i,p in enumerate(club.youth, start=1):
        print(f" -  {p.name:22s} {p.age:2d}a  OVR {p.overall():3d}  ({p.personality})")

def schedule_pairs(state_abbr: str, clubs: List[Club]) -> list[tuple[Club,Club]]:
    # só confrontos estaduais na 1a metade da temporada
    est = [c for c in clubs if c.state_abbr == state_abbr]
    rng = random.Random(42)
    rng.shuffle(est)
    pairs = []
    for i in range(0, len(est), 2):
        if i+1 < len(est):
            pairs.append((est[i], est[i+1]))
    return pairs

def play_week(clubs: List[Club], meta: Dict):
    rng = random.Random(meta["season"] * 10_000 + meta["week"])
    engine = MatchEngine(rng)
    # meu clube
    my = next(c for c in clubs if c.name == meta["team"])
    # gera confrontos estaduais nesta simples demonstração
    pairs = schedule_pairs(my.state_abbr, clubs)
    events_log = []
    for h, a in pairs:
        res = engine.simulate(h, a)
        events_log.append(res)
    meta["week"] += 1
    save_game(SAVE_FILE, clubs, meta)
    return events_log

def show_table(clubs: List[Club], state_abbr: str):
    clear()
    st = [c for c in clubs if c.state_abbr == state_abbr]
    st.sort(key=lambda c: (c.points, c.goals_for - c.goals_against, c.goals_for), reverse=True)
    print(f"TABELA — {st[0].state_name} ({state_abbr})")
    print("Pos Clube                               P  V  E  D  GP  GC  SG")
    for i,c in enumerate(st, start=1):
        sg = c.goals_for - c.goals_against
        print(f"{i:2d}  {c.name:33.33s} {c.points:2d} {c.wins:2d} {c.draws:2d} {c.losses:2d} {c.goals_for:2d} {c.goals_against:2d} {sg:2d}")

def main():
    clubs, meta = load_or_new()
    while True:
        clear()
        print(f"Treinador: {meta['coach']}   |  Temporada: {meta['season']}  Semana: {meta['week']}")
        print(f"Time: {meta['team']} ({meta['state']})\n")
        print("1) Ver meu time")
        print("2) Jogar esta semana (simular partidas e eventos)")
        print("3) Ver tabela estadual")
        print("4) Salvar")
        print("5) Sair")
        choice = input("\nEscolha: ").strip()
        if choice == "1":
            my = next(c for c in clubs if c.name == meta["team"])
            show_team(my); press_enter()
        elif choice == "2":
            results = play_week(clubs, meta)
            clear()
            print("RESULTADOS DA SEMANA\n")
            for r in results:
                print(f"{r.home} {r.goals_home} x {r.goals_away} {r.away}")
                # mostra timeline compacta
                tl = ", ".join([f"{ev.minute}' {ev.club}: {ev.kind} ({ev.player})" for ev in r.timeline[:6]])
                if tl: print(" - Eventos:", tl)
            press_enter()
        elif choice == "3":
            my = next(c for c in clubs if c.name == meta["team"])
            show_table(clubs, my.state_abbr); press_enter()
        elif choice == "4":
            save_game(SAVE_FILE, clubs, meta); print("Salvo."); press_enter()
        elif choice == "5":
            print("Até mais!"); break
        else:
            print("Opção inválida"); press_enter()

if __name__ == "__main__":
    main()


from __future__ import annotations
import os, sys, json, random
from typing import List, Dict, Tuple

from .data import generate_club_rosters, BR_STATES
from .models import Player, Club, make_player
from .sim import MatchEngine
from .leagues import StateLeague
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

def generate_universe(seed: int):
    data = generate_club_rosters(clubs_per_state=6, seniors_per_club=28, youth_per_club=18, seed=seed)
    clubs: List[Club] = []
    for (s_abbr, s_name), club_list in data.items():
        for cd in club_list:
            clubs.append(Club(
                name=cd["name"],
                state_abbr=cd["state_abbr"],
                state_name=cd["state_name"],
                budget=cd["budget"],
                squad=[make_player(p) for p in cd["squad"]],
                youth=[make_player(p) for p in cd["youth"]],
            ))
    return clubs

def new_game():
    clear()
    print("=== NOVA CARREIRA ===\n")
    coach = input("Seu nome: ").strip() or "Treinador"
    abbr, state = pick_state()

    seed = random.randint(1, 1_000_000)
    clubs = generate_universe(seed)
    my_clubs = [c for c in clubs if c.state_abbr == abbr]
    my_team = pick_club(my_clubs)

    # cria campeonato estadual completo
    st_league = StateLeague(abbr, clubs, seed=seed)

    meta = {
        "coach": coach,
        "seed": seed,
        "season": 1,
        "team": my_team.name,
        "state": state,
    }
    save_game(SAVE_FILE, clubs, meta, st_league)
    return clubs, meta, st_league

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

def train_team(club: Club):
    clear()
    print("Treino da semana")
    print("1) Força  2) Técnica  3) Velocidade  4) Moral")
    choice = input("Escolha o foco: ").strip()
    focus = {"1":"strength","2":"technique","3":"speed","4":"morale"}.get(choice, "strength")
    # treina 30% do elenco aleatoriamente
    pool = club.squad[:]
    random.shuffle(pool)
    train_n = max(1, len(pool)//3)
    for p in pool[:train_n]:
        p.train(focus)
    print(f"Treino concluído ({train_n} jogadores focados em {focus}).")

def show_table_state(clubs: List[Club], state_abbr: str):
    clear()
    st = [c for c in clubs if c.state_abbr == state_abbr]
    st.sort(key=lambda c: (c.points, c.goals_for - c.goals_against, c.goals_for), reverse=True)
    print(f"TABELA — {st[0].state_name} ({state_abbr})")
    print("Pos Clube                               P  V  E  D  GP  GC  SG")
    for i,c in enumerate(st, start=1):
        sg = c.goals_for - c.goals_against
        print(f"{i:2d}  {c.name:33.33s} {c.points:2d} {c.wins:2d} {c.draws:2d} {c.losses:2d} {c.goals_for:2d} {c.goals_against:2d} {sg:2d}")

def play_week(clubs: List[Club], meta: Dict, st_league: StateLeague):
    rng = random.Random(meta["season"] * 10_000 + st_league.current_week)
    engine = MatchEngine(rng)

    fixtures = st_league.fixtures_of_week(st_league.current_week)
    # dicionário rápido: nome -> objeto
    name_to_club = {c.name: c for c in clubs}

    results = []
    for fx in fixtures:
        h, a = name_to_club[fx.home], name_to_club[fx.away]
        res = engine.simulate(h, a)
        results.append(res)

    st_league.advance_week()
    save_game(SAVE_FILE, clubs, meta, st_league)
    return results

def main():
    clubs, meta, st_league = load_or_new()

    while True:
        my = next(c for c in clubs if c.name == meta["team"])
        clear()
        print(f"Treinador: {meta['coach']}   |  Temporada: {meta['season']}  Semana: {st_league.current_week}/{st_league.total_weeks}")
        print(f"Time: {meta['team']} ({meta['state']})\n")
        print("1) Ver meu time")
        print("2) Treinar (efeito no elenco)")
        print("3) Jogar esta semana (rodada do Estadual)")
        print("4) Ver tabela do Estadual")
        print("5) Salvar")
        print("6) Sair")
        choice = input("\nEscolha: ").strip()
        if choice == "1":
            show_team(my); press_enter()
        elif choice == "2":
            train_team(my); press_enter()
        elif choice == "3":
            if st_league.is_finished():
                print("O Estadual terminou! (Próximo passo: fase final/nacional em iteração futura)")
                press_enter()
            else:
                results = play_week(clubs, meta, st_league)
                clear()
                print(f"RESULTADOS — Semana {st_league.current_week - 1}\n")
                for r in results:
                    print(f"{r.home} {r.goals_home} x {r.goals_away} {r.away}")
                    tl = ", ".join([f"{ev.minute}' {ev.club}: {ev.kind} ({ev.player})" for ev in r.timeline[:8]])
                    if tl: print(" - Eventos:", tl)
                press_enter()
        elif choice == "4":
            show_table_state(clubs, my.state_abbr); press_enter()
        elif choice == "5":
            save_game(SAVE_FILE, clubs, meta, st_league); print("Salvo."); press_enter()
        elif choice == "6":
            print("Até mais!"); break
        else:
            print("Opção inválida"); press_enter()

if __name__ == "__main__":
    main()

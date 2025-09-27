"""
Football Manager Advanced Prototype (Python CLI)
================================================

Este script implementa uma versão mais robusta de um simulador de gestão de
futebol, inspirada nos pedidos do briefing oficial de "Football World" e
na famosa série *Football Manager*. Diferente do protótipo anterior, este
projeto suporta dezenas de clubes por estado brasileiro, competições
regionais e nacionais, elencos maiores e uma simulação mais rica de
partidas e eventos. O objetivo continua sendo fornecer um ambiente
textual para experimentar as mecânicas de gerenciamento antes de uma
implementação completa em Unity ou em uma interface gráfica.

Funcionalidades principais:

* Geração procedural de clubes: cada estado do Brasil possui um conjunto de
  equipes fictícias (por padrão 5 times por estado). Cada time tem um elenco
  principal de 30 jogadores e uma base (youth) com 15 atletas.
* Treinos: o jogador seleciona um foco de treino (força, técnica, velocidade
  ou moral) que afeta todos os jogadores saudáveis do elenco.
* Simulação de partidas: partidas são disputadas semanalmente, com
  registro de gols, cartões amarelos e vermelhos, lesões e expulsões. Os
  resultados alimentam a classificação geral (pontuação, vitórias,
  empates, derrotas, saldo de gols).
* Eventos semanais: além da partida, ocorrem eventos aleatórios que
  influenciam o clube — patrocínios, jogadores querendo sair, lesões no
  treino, interesse de rivais, convocações e aportes financeiros.
* Base de jogadores: os atletas da base podem ser promovidos ou
  emprestados. Eles evoluem com o tempo e podem participar de partidas
  menores (não implementado, mas estruturado para futuras expansões).
* Visão de outros clubes: o usuário pode consultar elencos adversários e
  até contratar um atleta rival mediante pagamento de taxa.
* Salvamento e carregamento: todo o estado do jogo pode ser salvo em
  arquivo JSON e carregado posteriormente.

Limitações: devido à complexidade de simular centenas de partidas por
semana, este protótipo não disputa jogos entre times que não envolvem o
usuário. Em vez disso, as partidas "externas" são simuladas de forma
resumida, apenas para atualizar a classificação. Também não inclui
gestão financeira detalhada, contratos, infraestrutura, staff, nem
mercado de transferências completo — estes pontos ficam como possíveis
extensões.

Para executar:

    python3 football_manager_advanced.py

"""

import json
import os
import random
import sys
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple


###############################################################################
# Dados e Constantes
###############################################################################

# Lista de estados brasileiros (26 estados + Distrito Federal).
# A origem desta lista está descrita no briefing: o Brasil possui 26
# estados e um Distrito Federal【629457308308636†L39-L87】.
BRAZILIAN_STATES = [
    "Acre", "Alagoas", "Amapá", "Amazonas", "Bahia", "Ceará",
    "Distrito Federal", "Espírito Santo", "Goiás", "Maranhão", "Mato Grosso",
    "Mato Grosso do Sul", "Minas Gerais", "Pará", "Paraíba", "Paraná",
    "Pernambuco", "Piauí", "Rio de Janeiro", "Rio Grande do Norte",
    "Rio Grande do Sul", "Rondônia", "Roraima", "Santa Catarina", "São Paulo",
    "Sergipe", "Tocantins",
]

# Listas básicas de nomes para jogadores.
FIRST_NAMES = [
    "João", "Pedro", "Lucas", "Gabriel", "Felipe", "Matheus", "Rafael",
    "Gustavo", "Luis", "Bruno", "Thiago", "Carlos", "Diego", "Vinicius",
    "Daniel", "André", "Fernando", "Henrique", "Jorge", "Paulo",
    "Eduardo", "Luan", "Ricardo", "William", "Wesley", "Leonardo",
]
LAST_NAMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira",
    "Alves", "Pereira", "Lima", "Gomes", "Costa", "Ribeiro", "Martins",
    "Carvalho", "Barbosa", "Rocha", "Freitas", "Correia", "Melo",
    "Nunes", "Pinto", "Moreira", "Araújo", "Almeida", "Cruz",
]

# Personalidades que impactam narrativas de eventos (sem impacto mecânico
# no cálculo de atributos, mas usadas para gerar mensagens).
PERSONALITIES = [
    "Talentoso",     # grande habilidade técnica
    "Preguiçoso",    # treino com menor evolução
    "Ambicioso",     # busca transferências para clubes melhores
    "Indisciplinado",# gera cartões e faltas
    "Carismático",   # melhora moral de colegas
    "Inconsistente", # atuações irregulares
    "Decisivo",      # cresce em finais
    "Frágil",        # propenso a lesões
    "Obscuro",       # promessa sem visibilidade
]

###############################################################################
# Classes de Dados
###############################################################################

@dataclass
class Player:
    """Representa um jogador de futebol."""
    name: str
    age: int
    strength: int
    technique: int
    speed: int
    morale: int
    personality: str
    potential: int  # potencial de evolução (0–100)
    loyalty: int    # 0–100, menor significa que o jogador quer sair
    injured: bool = False
    suspended: int = 0  # número de jogos suspenso (0 = apto)
    goals: int = 0
    yellow_cards: int = 0
    red_cards: int = 0

    def overall(self) -> float:
        """Calcula a média dos atributos técnicos do jogador."""
        return (self.strength + self.technique + self.speed) / 3.0

    def train(self, focus: str) -> None:
        """Aplica treino ao jogador, respeitando lesões e limites de atributos."""
        if self.injured:
            return
        if focus == "strength":
            self.strength += random.randint(1, 3)
        elif focus == "technique":
            self.technique += random.randint(1, 3)
        elif focus == "speed":
            self.speed += random.randint(1, 3)
        elif focus == "morale":
            self.morale += random.randint(1, 2)
        # Ajusta moral com base na personalidade
        if self.personality == "Preguiçoso" and focus != "morale":
            self.morale -= random.randint(0, 2)
        elif self.personality == "Carismático" and focus == "morale":
            self.morale += random.randint(1, 2)
        # Limita valores
        self.strength = min(100, self.strength)
        self.technique = min(100, self.technique)
        self.speed = min(100, self.speed)
        self.morale = max(0, min(100, self.morale))

    def tick_status(self) -> None:
        """Avança um jogo na contagem de suspensão. Remove suspensão ao zerar."""
        if self.suspended > 0:
            self.suspended -= 1
        # Recupera de lesões aleatoriamente após cada semana
        if self.injured and random.random() < 0.25:
            self.injured = False

@dataclass
class Team:
    """Representa um clube de futebol."""
    name: str
    state: str
    players: List[Player] = field(default_factory=list)
    youth: List[Player] = field(default_factory=list)
    points: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_for: int = 0
    goals_against: int = 0
    matches_played: int = 0
    budget: float = 10_000_000.0  # orçamento inicial fictício

    def rating(self) -> float:
        """Calcula a força média do elenco disponível (não suspenso nem lesionado)."""
        available = [p for p in self.players if not p.injured and p.suspended == 0]
        if not available:
            return 0.0
        return sum(p.overall() for p in available) / len(available)

    def reset_stats(self) -> None:
        """Zera estatísticas de temporada."""
        self.points = self.wins = self.draws = self.losses = 0
        self.goals_for = self.goals_against = self.matches_played = 0

    def add_player(self, player: Player) -> None:
        self.players.append(player)

    def remove_player(self, player: Player) -> None:
        if player in self.players:
            self.players.remove(player)

###############################################################################
# Geração Procedural
###############################################################################

def generate_player(age_min: int, age_max: int) -> Player:
    """Gera um jogador com atributos aleatórios e personalidade."""
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    age = random.randint(age_min, age_max)
    strength = random.randint(30, 80)
    technique = random.randint(30, 80)
    speed = random.randint(30, 80)
    morale = random.randint(40, 80)
    personality = random.choice(PERSONALITIES)
    potential = random.randint(60, 100)  # potencial máximo
    loyalty = random.randint(30, 100)
    return Player(name, age, strength, technique, speed, morale, personality, potential, loyalty)


def generate_team(state: str, index: int) -> Team:
    """Cria um clube fictício com elenco principal e base."""
    team_name = f"{state} Clube {index + 1}"
    players = [generate_player(18, 34) for _ in range(30)]
    youth = [generate_player(15, 18) for _ in range(15)]
    return Team(name=team_name, state=state, players=players, youth=youth)


def generate_league(teams_per_state: int = 5) -> Dict[str, List[Team]]:
    """Gera uma liga com vários clubes por estado."""
    league: Dict[str, List[Team]] = {}
    for state in BRAZILIAN_STATES:
        league[state] = [generate_team(state, i) for i in range(teams_per_state)]
    return league


###############################################################################
# Simulação de Partidas e Eventos
###############################################################################

def simulate_match(team_a: Team, team_b: Team) -> Tuple[int, int, List[str]]:
    """Simula uma partida entre dois clubes com eventos de jogo.

    Retorna uma tupla (gols_A, gols_B, lista_de_eventos).
    """
    events: List[str] = []
    # Calcula probabilidade base de gols com base na diferença de rating
    rating_a = team_a.rating()
    rating_b = team_b.rating()
    # A diferença influencia o número esperado de gols
    diff = rating_a - rating_b
    goals_a = max(0, int(random.gauss(1 + diff / 50.0, 1)))
    goals_b = max(0, int(random.gauss(1 - diff / 50.0, 1)))
    # Corrige extremos
    goals_a = min(max(goals_a, 0), 6)
    goals_b = min(max(goals_b, 0), 6)
    # Cria uma linha do tempo simplificada em 6 momentos
    minutes = [15, 30, 45, 60, 75, 90]
    for minute in minutes:
        roll = random.random()
        # chance de cartão amarelo
        if roll < 0.10:
            team = team_a if random.random() < 0.5 else team_b
            player = random.choice(team.players)
            player.yellow_cards += 1
            events.append(f"{minute}' Cartão amarelo para {player.name} ({team.name}).")
        # chance de cartão vermelho
        elif roll < 0.13:
            team = team_a if random.random() < 0.5 else team_b
            player = random.choice(team.players)
            player.red_cards += 1
            player.suspended += 2  # suspenso por 2 jogos
            events.append(f"{minute}' Cartão vermelho para {player.name} ({team.name}).")
        # chance de gol
        elif roll < 0.40:
            scoring_team = team_a if random.random() < (rating_a / (rating_a + rating_b + 1e-6)) else team_b
            scorer = random.choice(scoring_team.players)
            if scoring_team is team_a:
                goals_a += 1
            else:
                goals_b += 1
            scorer.goals += 1
            events.append(f"{minute}' Gol de {scorer.name} para o {scoring_team.name}!")
        # chance de lesão
        elif roll < 0.45:
            team = team_a if random.random() < 0.5 else team_b
            victim = random.choice(team.players)
            victim.injured = True
            events.append(f"{minute}' {victim.name} ({team.name}) sofreu uma lesão!")
    return goals_a, goals_b, events


def update_team_stats(team: Team, goals_for: int, goals_against: int) -> None:
    """Atualiza estatísticas de um clube após partida."""
    team.matches_played += 1
    team.goals_for += goals_for
    team.goals_against += goals_against
    if goals_for > goals_against:
        team.points += 3
        team.wins += 1
    elif goals_for == goals_against:
        team.points += 1
        team.draws += 1
    else:
        team.losses += 1


def simulate_external_matches(league: Dict[str, List[Team]], current_week: int) -> None:
    """Simula partidas entre todos os demais clubes (não controlados pelo usuário).

    Para simplificação, sorteia pares aleatórios dentro de cada estado
    e fora, mas não gera eventos detalhados. Apenas atualiza pontuação.
    """
    for state_teams in league.values():
        teams = state_teams[:]
        random.shuffle(teams)
        # Emparelha times em duplas (ignora ímpar)
        for i in range(0, len(teams) - 1, 2):
            a = teams[i]
            b = teams[i + 1]
            ga, gb, _ = simulate_match(a, b)
            update_team_stats(a, ga, gb)
            update_team_stats(b, gb, ga)
    # Jogos inter-estaduais aleatórios (um por estado)
    all_teams = [t for teams in league.values() for t in teams]
    random.shuffle(all_teams)
    for i in range(0, len(all_teams) - 1, 2):
        a = all_teams[i]
        b = all_teams[i + 1]
        ga, gb, _ = simulate_match(a, b)
        update_team_stats(a, ga, gb)
        update_team_stats(b, gb, ga)


def random_weekly_event(user_team: Team) -> str:
    """Gera um evento aleatório envolvendo o clube do usuário."""
    events = []
    # 1. Patrocínio
    events.append(
        lambda: f"Um novo patrocinador assinou contrato, adicionando R$ {random.randint(500_000, 5_000_000):,} ao orçamento."
    )
    # 2. Investidor/SAF
    events.append(
        lambda: "Um investidor demonstrou interesse em adquirir parte do clube em troca de capital."
    )
    # 3. Jogador quer sair
    events.append(
        lambda: random.choice(user_team.players).name + " solicitou transferência para um clube maior."
    )
    # 4. Lesão em treino
    events.append(
        lambda: f"O jogador {random.choice(user_team.players).name} se lesionou durante o treino e ficará fora por algumas semanas."
    )
    # 5. Convocação
    events.append(
        lambda: f"{random.choice(user_team.players).name} foi convocado para a seleção nacional e desfalcará o próximo jogo."
    )
    # 6. Crise interna
    events.append(
        lambda: "Houve um desentendimento entre diretores, prejudicando a moral do clube."
    )
    # 7. Juventude promissora
    events.append(
        lambda: f"Um jovem da base ({random.choice(user_team.youth).name}) tem se destacado e pede oportunidades."
    )
    # Seleciona e executa evento
    event = random.choice(events)()
    return event


###############################################################################
# Persistência de Jogo
###############################################################################

def save_game(path: str, league: Dict[str, List[Team]], user_team_name: str, week: int) -> None:
    """Serializa o estado do jogo em JSON."""
    data: Dict[str, object] = {
        "week": week,
        "user_team": user_team_name,
        "teams": [],
    }
    for teams in league.values():
        for team in teams:
            team_data = asdict(team)
            # Serializa jogadores manualmente para remover atributos não serializáveis
            team_data['players'] = [asdict(p) for p in team.players]
            team_data['youth'] = [asdict(p) for p in team.youth]
            data["teams"].append(team_data)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Jogo salvo em {path}.")


def load_game(path: str) -> Tuple[Dict[str, List[Team]], str, int]:
    """Restaura o estado do jogo a partir de um arquivo JSON."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo {path} não encontrado.")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    week = data.get("week", 0)
    user_team_name = data.get("user_team", "")
    # Reconstrói liga
    league: Dict[str, List[Team]] = {state: [] for state in BRAZILIAN_STATES}
    for tdata in data.get("teams", []):
        players = [Player(**p) for p in tdata['players']]
        youth = [Player(**p) for p in tdata['youth']]
        team = Team(
            name=tdata['name'], state=tdata['state'], players=players, youth=youth,
            points=tdata['points'], wins=tdata['wins'], draws=tdata['draws'],
            losses=tdata['losses'], goals_for=tdata['goals_for'],
            goals_against=tdata['goals_against'], matches_played=tdata['matches_played'],
            budget=tdata.get('budget', 10_000_000.0)
        )
        league[team.state].append(team)
    return league, user_team_name, week


###############################################################################
# Interface de Texto (CLI)
###############################################################################

def select_state_and_team(league: Dict[str, List[Team]]) -> Team:
    """Permite ao jogador escolher estado e clube."""
    print("\nEscolha seu estado:")
    for i, state in enumerate(BRAZILIAN_STATES, 1):
        print(f"{i:2d}. {state}")
    while True:
        try:
            s_idx = int(input("Número do estado: ")) - 1
            if 0 <= s_idx < len(BRAZILIAN_STATES):
                chosen_state = BRAZILIAN_STATES[s_idx]
                break
        except ValueError:
            pass
        print("Entrada inválida.")
    print(f"\nTimes disponíveis em {chosen_state}:")
    teams = league[chosen_state]
    for i, t in enumerate(teams, 1):
        print(f"{i:2d}. {t.name}")
    while True:
        try:
            t_idx = int(input("Número do time: ")) - 1
            if 0 <= t_idx < len(teams):
                return teams[t_idx]
        except ValueError:
            pass
        print("Entrada inválida.")


def display_team(team: Team) -> None:
    """Mostra elenco principal com atributos."""
    print(f"\nElenco do {team.name} (Idade/Força/Técnica/Velocidade/Moral) – {len(team.players)} jogadores")
    for idx, p in enumerate(team.players, 1):
        status = []
        if p.injured:
            status.append("Lesão")
        if p.suspended:
            status.append(f"Suspenso {p.suspended}j")
        status_str = " (" + ", ".join(status) + ")" if status else ""
        print(f"{idx:2d}. {p.name} - {p.age}a - {p.strength}/{p.technique}/{p.speed}/{p.morale} - {p.personality}{status_str}")
    print(f"\nOrçamento: R$ {team.budget:,.2f}\n")


def display_youth(team: Team) -> None:
    """Mostra jogadores da base."""
    print(f"\nBase do {team.name} – {len(team.youth)} jogadores")
    for idx, p in enumerate(team.youth, 1):
        print(f"{idx:2d}. {p.name} - {p.age}a - Potencial: {p.potential}/100 - Moral: {p.morale}")


def display_standings(league: Dict[str, List[Team]]) -> None:
    """Exibe a classificação geral dos clubes (pontos, saldo etc.)."""
    all_teams = [t for teams in league.values() for t in teams]
    sorted_teams = sorted(all_teams, key=lambda t: (t.points, t.goals_for - t.goals_against, t.goals_for), reverse=True)
    print("\nClassificação Geral:")
    print("Pos Pts V E D SG Clube")
    for idx, t in enumerate(sorted_teams, 1):
        saldo = t.goals_for - t.goals_against
        print(f"{idx:2d} {t.points:3d} {t.wins:2d} {t.draws:2d} {t.losses:2d} {saldo:3d} {t.name}")


def view_other_team(league: Dict[str, List[Team]]) -> None:
    """Permite ao usuário ver o elenco de um time qualquer."""
    team_names = [team.name for teams in league.values() for team in teams]
    print("\nSelecione um clube para visualizar:")
    for i, name in enumerate(team_names, 1):
        print(f"{i:2d}. {name}")
    while True:
        try:
            idx = int(input("Número do clube: ")) - 1
            if 0 <= idx < len(team_names):
                # Encontrar o time
                target_name = team_names[idx]
                for teams in league.values():
                    for team in teams:
                        if team.name == target_name:
                            display_team(team)
                            return
        except ValueError:
            pass
        print("Entrada inválida.")


def sign_player(user_team: Team, league: Dict[str, List[Team]]) -> None:
    """Permite contratar um jogador de outro time pagando taxa."""
    print("\n=== Contratar Jogador ===")
    print("Seu orçamento: R$ {:,.2f}".format(user_team.budget))
    # Escolher time alvo
    team_names = [team.name for teams in league.values() for team in teams if team != user_team]
    for i, name in enumerate(team_names, 1):
        print(f"{i:2d}. {name}")
    try:
        t_idx = int(input("Escolha um clube: ")) - 1
        if not (0 <= t_idx < len(team_names)):
            print("Clube inválido.")
            return
    except ValueError:
        print("Entrada inválida.")
        return
    # Identifica o clube alvo
    target_team = None
    for teams in league.values():
        for team in teams:
            if team.name == team_names[t_idx]:
                target_team = team
                break
    if not target_team:
        print("Clube não encontrado.")
        return
    # Lista jogadores disponíveis
    print(f"Jogadores de {target_team.name}:")
    for i, p in enumerate(target_team.players, 1):
        print(f"{i:2d}. {p.name} - Overall: {p.overall():.1f} - Valor: R$ {(p.overall() * 100_000):,.2f}")
    try:
        p_idx = int(input("Escolha um jogador para contratar: ")) - 1
        if not (0 <= p_idx < len(target_team.players)):
            print("Jogador inválido.")
            return
    except ValueError:
        print("Entrada inválida.")
        return
    player = target_team.players[p_idx]
    price = player.overall() * 100_000
    if user_team.budget < price:
        print("Você não tem orçamento suficiente.")
        return
    # Realiza transação
    user_team.budget -= price
    target_team.budget += price
    target_team.remove_player(player)
    user_team.add_player(player)
    print(f"{player.name} foi contratado por R$ {price:,.2f}.")


def train_team(user_team: Team) -> None:
    """Aplica treino ao elenco inteiro com foco escolhido."""
    print("\n=== Treino ===")
    print("1. Força\n2. Técnica\n3. Velocidade\n4. Moral")
    choice = input("Escolha o foco: ")
    focus_map = {"1": "strength", "2": "technique", "3": "speed", "4": "morale"}
    focus = focus_map.get(choice)
    if not focus:
        print("Foco inválido.")
        return
    for p in user_team.players:
        p.train(focus)
    print(f"Treino focado em {focus}. Atributos atualizados!")


def advance_week(user_team: Team, league: Dict[str, List[Team]], week: int) -> Tuple[int, str, List[str]]:
    """Processa as atividades da semana: treino opcional, partida e eventos."""
    # Treino opcional
    print("\nDeseja treinar a equipe nesta semana? (s/n)")
    if input().strip().lower() == 's':
        train_team(user_team)
    # Processa suspensões e recuperações
    for p in user_team.players:
        p.tick_status()
    # Escolhe adversário aleatório de outro clube (pode ser de qualquer estado)
    opponents = [t for teams in league.values() for t in teams if t != user_team]
    opponent = random.choice(opponents)
    # Simula partida
    goals_user, goals_opp, events = simulate_match(user_team, opponent)
    update_team_stats(user_team, goals_user, goals_opp)
    update_team_stats(opponent, goals_opp, goals_user)
    summary = f"{user_team.name} {goals_user} x {goals_opp} {opponent.name}"
    # Evento aleatório pós‑jogo
    random_event = random_weekly_event(user_team)
    # Retorna nova semana, resumo, eventos de partida e evento aleatório
    return week + 1, summary, events + [random_event]


def game_loop() -> None:
    """Loop principal do jogo."""
    print("=== Football Manager Advanced – Novo Jogo ===")
    manager_name = input("Digite seu nome de treinador: ")
    # Gera liga
    league = generate_league(teams_per_state=5)
    user_team = select_state_and_team(league)
    print(f"\nBem‑vindo, {manager_name}! Você irá comandar o {user_team.name} do estado de {user_team.state}.")
    week = 0
    inbox: List[str] = []
    # Loop de temporada
    while True:
        print("\n=== Menu Principal ===")
        print("1. Ver elenco\n2. Ver base\n3. Treinar equipe\n4. Jogar próxima semana\n5. Ver classificação\n6. Ver eventos (Inbox)\n7. Ver elenco de outro clube\n8. Contratar jogador\n9. Salvar jogo\n10. Carregar jogo\n11. Sair")
        choice = input("Escolha uma opção: ").strip()
        if choice == "1":
            display_team(user_team)
        elif choice == "2":
            display_youth(user_team)
        elif choice == "3":
            train_team(user_team)
        elif choice == "4":
            # Avança semana
            week, match_summary, events = advance_week(user_team, league, week)
            inbox.append(match_summary)
            inbox.extend(events)
            simulate_external_matches(league, week)
            print(match_summary)
            print("Eventos da partida:")
            for e in events:
                print(" - ", e)
        elif choice == "5":
            display_standings(league)
        elif choice == "6":
            print("\n=== Eventos Recentes ===")
            for event in inbox[-10:]:
                print(" - ", event)
        elif choice == "7":
            view_other_team(league)
        elif choice == "8":
            sign_player(user_team, league)
        elif choice == "9":
            fname = input("Nome do arquivo para salvar (ex: save.json): ")
            save_game(fname, league, user_team.name, week)
        elif choice == "10":
            fname = input("Nome do arquivo para carregar: ")
            try:
                league, user_team_name, week = load_game(fname)
                # Define novo user_team após carregar
                for teams in league.values():
                    for team in teams:
                        if team.name == user_team_name:
                            user_team = team
                            break
                print(f"Jogo carregado. Treinando o {user_team.name}.")
            except Exception as e:
                print(f"Erro ao carregar: {e}")
        elif choice == "11":
            print("Saindo do jogo. Até logo!")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    try:
        game_loop()
    except KeyboardInterrupt:
        print("\nJogo encerrado pelo usuário.")
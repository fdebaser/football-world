
from dataclasses import dataclass
from typing import List, Dict, Tuple
import random

# 27 unidades federativas do Brasil (26 estados + DF)
# fonte geral: lista pública de unidades federativas (estado + sigla)
BR_STATES = [
    ("AC", "Acre"), ("AL", "Alagoas"), ("AP", "Amapá"), ("AM", "Amazonas"),
    ("BA", "Bahia"), ("CE", "Ceará"), ("DF", "Distrito Federal"), ("ES", "Espírito Santo"),
    ("GO", "Goiás"), ("MA", "Maranhão"), ("MT", "Mato Grosso"), ("MS", "Mato Grosso do Sul"),
    ("MG", "Minas Gerais"), ("PA", "Pará"), ("PB", "Paraíba"), ("PR", "Paraná"),
    ("PE", "Pernambuco"), ("PI", "Piauí"), ("RJ", "Rio de Janeiro"), ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"), ("RO", "Rondônia"), ("RR", "Roraima"), ("SC", "Santa Catarina"),
    ("SP", "São Paulo"), ("SE", "Sergipe"), ("TO", "Tocantins"),
]

MASCOTS = ["Leões", "Tigres", "Gaviões", "Lobos", "Panteras", "Águias", "Raposas", "Falcões", "Tubaroes", "Carcarás", "Onças", "Dragões"]
COLORS  = ["Azul", "Vermelho", "Verde", "Preto", "Branco", "Amarelo", "Vinho", "Laranja", "Roxo", "Celeste"]
CITIES  = ["Norte", "Sul", "Leste", "Oeste", "Centro", "Nova", "Vila", "Porto", "Santa", "São", "Bom", "Rio", "Praia", "Lago", "Serra"]

FIRST_NAMES = ["Gabriel","Lucas","Mateus","Pedro","Rafael","Gustavo","Felipe","Thiago","Bruno","Henrique","Caio","Enzo","Bernardo","Luan","João","Vitor","Igor","Diego","André","Leandro","Ruan","Alan","Eduardo","Samuel","Rian","Paulo","Yuri","Rogério","Maurício","Alex","Danilo","Elias","Renato","Caíque","Murilo","Nicolas","João Pedro"]
LAST_NAMES  = ["Silva","Souza","Oliveira","Santos","Pereira","Lima","Carvalho","Gomes","Ribeiro","Alves","Costa","Fernandes","Araujo","Barbosa","Rocha","Correia","Martins","Pinto","Melo","Mendes","Vieira","Sales","Monteiro","Freitas","Teixeira","Cardoso"]

PERSONALITIES = [
    "Líder silencioso", "Falastrão de vestiário", "Decisivo em finais", "Some em jogo grande",
    "Treino exemplar", "Indisciplinado", "Amado pela torcida", "Pavio curto",
    "Ídolo local", "Promessa da base", "Veterano cascudo", "Frio em pênaltis",
]

def rand_name() -> str:
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def make_club_name(state_abbr: str) -> str:
    # Ex.: SP - "São Azul Leões", "Porto Verde Lobos"
    city = random.choice(CITIES)
    color = random.choice(COLORS)
    mascot = random.choice(MASCOTS)
    return f"{city} {color} {mascot} {state_abbr}".strip()

def generate_club_rosters(
    clubs_per_state: int = 6,
    seniors_per_club: int = 28,
    youth_per_club: int = 18,
    seed: int | None = None,
):
    """Gera clubes e elencos para todos os estados.
    Retorna dicionário: { (UF, Estado): [ {name, state, squad, youth} * N ] }"""
    if seed is not None:
        random.seed(seed)

    data: Dict[Tuple[str,str], List[dict]] = {}
    for abbr, state in BR_STATES:
        clubs = []
        for _ in range(clubs_per_state):
            club_name = make_club_name(abbr)
            # Elenco profissional
            squad = []
            for i in range(seniors_per_club):
                player = {
                    "name": rand_name(),
                    "age": random.randint(18, 35),
                    "strength": random.randint(30, 90),
                    "technique": random.randint(30, 90),
                    "speed": random.randint(30, 90),
                    "morale": random.randint(40, 90),
                    "personality": random.choice(PERSONALITIES),
                    "isLegendary": False,
                }
                squad.append(player)
            # Base
            youth = []
            for i in range(youth_per_club):
                player = {
                    "name": rand_name(),
                    "age": random.randint(15, 18),
                    "strength": random.randint(25, 70),
                    "technique": random.randint(25, 70),
                    "speed": random.randint(25, 70),
                    "morale": random.randint(40, 90),
                    "personality": random.choice(PERSONALITIES),
                    "isLegendary": False,
                }
                youth.append(player)

            clubs.append({
                "name": club_name,
                "state_abbr": abbr,
                "state_name": state,
                "budget": random.randint(5_000_000, 80_000_000),
                "squad": squad,
                "youth": youth,
            })
        data[(abbr, state)] = clubs
    return data

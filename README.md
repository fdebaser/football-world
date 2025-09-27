
# Football World (Starter)

Protótipo modular para um jogo de gestão de futebol **estilo Football Manager**, com foco em Brasil, centenas de clubes e milhares de jogadores gerados proceduralmente. Inclui:

- Geração de clubes por **todos os 26 estados + DF** (quantidade de clubes/jogadores configurável).
- **Elencos profissionais e base** com atributos, personalidades e potenciais.
- **Simulador de partidas** com linha do tempo de eventos (gols, cartões, lesões, etc.).
- **Tabela estadual** e fluxo semanal simples.
- **Save/Load** em JSON.

> Este é um “esqueleto” modular para evoluirmos rápido. O objetivo é que você suba esta estrutura no GitHub e eu vá expandindo os módulos.

## Como rodar

```bash
# 1) entre na pasta
cd football-world-starter

# 2) rode o CLI
python -m football_world.cli
# ou
python football_world/cli.py
```

Os saves ficam em `saves/career.save.json`.

## Estrutura

```
football-world-starter/
├─ football_world/
│  ├─ __init__.py
│  ├─ data.py          # geração de estados, clubes e elencos
│  ├─ models.py        # classes de domínio (Player, Club)
│  ├─ sim.py           # motor de partidas com eventos
│  └─ persistence.py   # save/load em JSON
├─ README.md
├─ requirements.txt
└─ .gitignore
```

## Roadmap curto (próximos passos)

- Competição **estadual completa** (turno e returno + fase final) e **nacional** na segunda metade.
- Agenda semanal com **treinos**, **staff**, **patrocínio/SAF**, moral e finanças.
- Tela/relatório por jogo com **eventos minuto a minuto** e destaques.
- Ferramentas de **transferência** com cláusulas, empréstimos e negociações.
- Exportar para **Unity/Web** mantendo a mesma lógica do simulador.

## Licença

MIT (à sua escolha; podemos alterar depois).

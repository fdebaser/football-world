
# Milestone 01 — Campeonato Estadual + Treinos

Esta atualização adiciona:

- **Campeonato Estadual completo (turno e returno)** usando `football_world/leagues.py`.
- **Calendário semanal**: cada semana corresponde a uma rodada do estadual.
- **Simulação de partidas** com timeline (gols, cartões, lesões) usando `sim.py`.
- **Treinos semanais** que aumentam atributos de ~30% do elenco profissional.
- **Persistência do estado da liga** (save inclui liga/semana/fixtures).

## Como aplicar no seu repositório

1. Copie/cole estes arquivos no seu repositório `football-world` substituindo os existentes (mantenha a estrutura de pastas):
   - `football_world/leagues.py` (novo)
   - `football_world/cli.py` (atualizado)
   - `football_world/persistence.py` (atualizado)
2. Faça commit com uma mensagem, por exemplo:
   ```bash
   git add football_world/leagues.py football_world/cli.py football_world/persistence.py
   git commit -m "feat(league): estadual completo + treinos + save da liga"
   git push
   ```

## Como rodar

```bash
python -m football_world.cli
```

> Próximas milestones: fase final (mata‑mata) do estadual, **Copa Nacional** após os estaduais, staff/patrocínio/SAF, janela de transferências.

# Football World – Design Avançado

## Introdução

Este documento serve como uma evolução do briefing oficial do jogo *Football World*. O objetivo é aproximar a experiência do jogo de gestão de futebol clássico (*Football Manager*), mantendo uma pegada simplificada e visual minimalista inspirada em *Hundred Days*. As principais demandas incluem: grande número de clubes e jogadores, divisões por estados e competição nacional, simulação rica de partidas com eventos, histórias de bastidores, base forte e possibilidade de criar ou customizar clubes.

## Estados e Clubes

- O Brasil possui 26 estados e um Distrito Federal【629457308308636†L39-L87】. Cada estado abriga vários clubes fictícios (no protótipo: 5 clubes por estado, totalizando 135 times). Em implementações completas, esse número pode ser ampliado para dezenas de equipes por estado.
- Clubes possuem nome, escudo (customizável em versões gráficas), localidade, orçamento inicial e dois elencos: principal (cerca de 30 jogadores) e base (15 jogadores). Os clubes podem participar de campeonatos estaduais e de uma liga nacional.
- Jogadores têm atributos técnicos (força, técnica, velocidade), moral, personalidade (talentoso, preguiçoso, ambicioso, indisciplinado, etc.) e potencial. Há também mecanismos de lesão, suspensão, cartões e vontade de sair do clube.

## Competições

1. **Campeonatos Estaduais:** todos os clubes de um estado disputam uma liga ou mata‑mata entre si. Os melhores se classificam para divisões superiores. Os estaduais acontecem no início da temporada. (No protótipo, a liga é global para simplificar; mas o design prevê estaduais completos.)
2. **Campeonato Nacional:** após os estaduais, clubes classificados (ou todos, dependendo do modo) disputam uma liga nacional de pontos corridos. Promoções e rebaixamentos acontecem entre divisões (Série A, B, C...).
3. **Competições adicionais:** copas regionais e torneios internacionais podem ser adicionados em futuras versões.

## Mecânicas de Jogo

- **Treino:** o usuário escolhe um foco (força, técnica, velocidade ou moral) e todo o elenco treina naquela área. Personalidades influenciam resultados: jogadores preguiçosos evoluem menos, carismáticos aumentam moral, etc.
- **Partidas:** os confrontos são simulados com placar, gols, cartões amarelos e vermelhos, lesões e expulsões. Os atributos dos jogadores e a força média do time determinam as chances de vitória. Eventos são registrados no *Inbox* com descrição detalhada.
- **Eventos Aleatórios:** entre jogos surgem notícias e problemas: patrocínios, investidores, jogadores querendo sair, crises internas, convocações para seleções e destaque de jogadores da base. Esses eventos afetam o orçamento, moral e elenco.
- **Base:** jogadores jovens evoluem com o tempo e podem ser promovidos ao elenco principal ou emprestados. No futuro, a base pode disputar competições menores.
- **Transferências:** o usuário pode contratar jogadores de qualquer outro clube, pagando um valor proporcional ao desempenho. O orçamento do time é limitado, e as vendas também geram receita. Futuramente, cláusulas, empréstimos e SAF serão incluídos.
- **Salvamento/Carregamento:** todo o progresso (liga, times, jogadores, semana atual) pode ser salvo em um arquivo JSON e retomado mais tarde.
- **Gestão de Clube:** embora o protótipo não implemente staff, infraestrutura e finanças detalhadas, o design prevê contratação de preparadores, médicos, olheiros; expansão de estádios; negociação com investidores; e criação de SAF.

## Jogadores Lendários

Personagens lendários como Coalhada, Carlos Kaiser, Carlinhos Bala, Caça‑Rato e Kuki serão incluídos com estatísticas e comportamentos únicos. Eles podem aparecer aleatoriamente no mercado ou como eventos especiais. Além disso, o “efeito Pata do Macaco” cria situações onde uma contratação muito poderosa traz consequências negativas ocultas.

## Interface e Experiência

O jogo final deve ter telas minimalistas em 2D: menu principal, base, treino, transferências, partidas, inbox, estádio e configurações. Cada tela apresenta as informações em cartões e tabelas claras. Os escudos dos clubes e avatares dos jogadores são coloridos e estilizados. Na ausência de gráficos, o protótipo CLI imprime textos descritivos e listas ordenadas.

## Protótipo Python (football_manager_advanced.py)

Para demonstrar as novas mecânicas, foi desenvolvido um script CLI (arquivo `football_manager_advanced.py`). Principais características:

- **Geração Procedural:** cria 5 times em cada um dos 27 entes federativos. Cada time tem 30 jogadores profissionais e 15 jovens com nomes, atributos e personalidades aleatórias.
- **Treino Coletivo:** o treinador escolhe o foco semanal; atributos são atualizados com base na personalidade dos atletas.
- **Partida Simulada:** cada semana, o time do usuário enfrenta um adversário aleatório de qualquer estado. Gols, cartões amarelos/vermelhos e lesões são sorteados em uma linha do tempo de 6 intervalos. Após a partida, as estatísticas gerais (pontos, vitórias, empates, derrotas, saldo de gols) são atualizadas.
- **Eventos Semanais:** após o jogo, um evento aleatório ocorre: novo patrocinador, investidor SAF, jogador pedindo transferência, lesão em treino, convocação para seleção, crise interna ou destaque de atleta da base.
- **Mercado Simplificado:** o usuário pode contratar jogadores de outros clubes, pagando um valor proporcional ao seu “overall”; o orçamento do clube é ajustado automaticamente.
- **Classificação Global:** a função `display_standings` mostra a tabela de pontos de todos os clubes (estado e nacional combinados). Em versões futuras, será possível separar por estado e divisão.
- **Salvar/Carregar:** comandos de menu permitem gravar e ler o progresso em arquivos JSON.

Este protótipo ilustra como os elementos do briefing podem ser combinados em um jogo jogável em linha de comando. Ele serve como base para implementar uma versão gráfica no Unity ou em web, respeitando a complexidade e o humor esperados.

## Expansões Futuras

- **Separação de Estaduais e Nacional:** criar calendários distintos com fases de grupos e mata‑mata, qualificando clubes para divisões superiores.
- **Gestão de Staff:** contratar técnicos, preparadores, médicos e diretores, influenciando treinos, recuperação e negociações.
- **Economia Detalhada:** implementar receitas (ingressos, merchandising, direitos de TV), despesas (salários, manutenção, viagens) e balanço financeiro. Possibilidade de SAF com investidores que exigem resultados.
- **Modo Carreira Completo:** permitir que o jogador seja treinador, diretor ou presidente, inclusive fundar novos clubes, desenhar escudos e combinar cores.
- **Histórias Dinâmicas:** personalizar trajetórias de jogadores (indisciplina, superação, falhas em finais), com consequências narrativas que aproximem a experiência do *Football Manager*.
- **Multiplayer Online:** suportar partidas contra amigos ou torneios em rede.

---

Este design avançado e o protótipo fornecido formam a base para desenvolvimento futuro de *Football World*. Ele mostra que é possível manter a essência de gestão e progressão de carreira de um simulador completo, ao mesmo tempo em que se adapta a um projeto mais enxuto e acessível.
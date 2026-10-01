# 🌳 IA para Jovens Curiosos — Achando a Maior Árvore do Brasil (Google Colab)

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ia-para-jovens-curiosos/achando_a_maior_arvore_do_brasil_colab/blob/main/arvrona.ipynb)
[![GitHub Repo](https://img.shields.io/badge/GitHub-ia--para--jovens--curiosos%2Fachando__a__maior__arvore__do__brasil__colab-blue?logo=github)](https://github.com/ia-para-jovens-curiosos/achando_a_maior_arvore_do_brasil_colab)

Um projeto para crianças descobrirem, passo a passo, como um algoritmo encontra a maior árvore do Brasil dentro de uma nuvem de pontos gerada por um laser (LiDAR) voando de avião sobre a floresta.

Esta é a versão para o **Google Colab**: não precisa instalar nada no computador, só ter um navegador e uma conta Google. A versão para Jupyter/PyCharm está em [achando_a_maior_arvore_do_brasil](https://github.com/ia-para-jovens-curiosos/achando_a_maior_arvore_do_brasil).

## Como abrir

Clique no botão **Abrir no Colab** acima. No Colab, execute as células de cima para baixo, com `Shift + Enter` ou com o botão ▶️ ao lado de cada célula.

A primeira célula de código (Passo 0) baixa este repositório para dentro do Colab e instala o `laspy`, que lê os arquivos de LiDAR. Depois disso, o notebook guia você por três passos:

1. **Carregar a nuvem** — ler o arquivo `.laz` com mais de 1 milhão de pontos
2. **Buscar a árvore campeã** — ver a busca acontecendo, gráfico a gráfico
3. **Mostrar o resultado** — ver a árvore campeã destacada na nuvem inteira

No fim, a seção **Para pensar** tem uma célula onde você muda o tamanho do hemisfério e o número mínimo de pontos e roda a busca de novo.

## Como funciona o algoritmo

A busca começa pelo **ponto mais alto** de toda a nuvem. Ao redor desse ponto, o algoritmo imagina um **hemisfério** (uma "meia bola") de **50 metros de diâmetro** (25 m de raio), virado para baixo, com a borda centrada exatamente no ponto escolhido — e conta quantos pontos existem dentro dele.

Uma árvore de verdade tem uma copa cheia de galhos e folhas por baixo do topo, então deve haver **pelo menos 300 pontos** ali dentro:

- ✅ Se houver 300 pontos ou mais, o ponto é aceito como a árvore.
- ❌ Se houver menos, o ponto é descartado (pode ser, por exemplo, um passarinho ou um eco estranho do laser) e o algoritmo tenta o **próximo ponto mais alto**, repetindo o teste até a condição ser satisfeita.

Esse é o mesmo tipo de verificação usada no algoritmo original que encontrou a maior árvore do Brasil nessa nuvem de pontos.

## Como funciona por baixo dos panos

Todo o `laspy`, `scipy` e `matplotlib` ficam escondidos dentro do arquivo `achando_a_maior_arvore.py`, que oferece só três funções simples em português:

- `carregar_nuvem(caminho=None)`
- `buscar_maior_arvore(nuvem)`
- `mostrar_resultado(nuvem, campea)`

## Dados

O arquivo `data/nuvem_de_pontos_aula.laz` é uma faixa de ~100 m de largura (alargada para ~550 m só no trecho com os pontos "ruidosos") seguindo a linha de voo real do LiDAR, com cerca de 10,5 km de comprimento, cobrindo tanto a árvore campeã quanto os pontos ruidosos (passarinhos, ecos estranhos do laser) que o algoritmo testa e descarta antes de chegar lá. Esse recorte preserva exatamente os mesmos 151 passos de busca da nuvem completa (225 MB, ~40 milhões de pontos), só que num arquivo bem menor. Sistema de referência: SIRGAS 2000 / UTM zona 20S (EPSG:31980), alturas já normalizadas (altura acima do solo).

## Rodando no seu computador

O notebook também funciona fora do Colab. Este projeto usa **Python 3.12**. Para criar o ambiente virtual:

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

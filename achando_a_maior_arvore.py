"""
Camada em português que esconde o laspy, o numpy e o matplotlib por trás de
funções simples: carregar_nuvem(), buscar_maior_arvore() e mostrar_resultado().

Quem for usar este módulo não precisa entender de "nuvem de pontos", "KD-tree"
ou "arrays" — só precisa chamar essas três funções, nessa ordem, dentro do
notebook.
"""

import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import laspy
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import cKDTree

PASTA_DADOS = "data"
ARQUIVO_PADRAO_DA_NUVEM = os.path.join(PASTA_DADOS, "nuvem_de_pontos_aula.laz")

# O hemisfério tem 50 m de diâmetro, ou seja, 25 m de raio.
RAIO_DO_HEMISFERIO_METROS = 25.0

# Uma árvore de verdade tem uma copa cheia de pontos por baixo do topo.
# Se houver menos pontos que isso, o ponto escolhido é descartado.
MINIMO_DE_PONTOS_NO_HEMISFERIO = 300

PASSOS_MAXIMOS_DA_BUSCA = 2000


# ---------------------------------------------------------------------------
# Funções que as crianças usam no notebook
# ---------------------------------------------------------------------------

def carregar_nuvem(caminho=ARQUIVO_PADRAO_DA_NUVEM):
    """Lê o arquivo .laz com a nuvem de pontos do LiDAR.

    Devolve uma tabela com as coordenadas X, Y, Z de cada ponto (em metros).
    """
    print(f"📥 Lendo {caminho} ...")
    with laspy.open(caminho) as arquivo:
        las = arquivo.read()
    nuvem = np.column_stack((las.x, las.y, las.z)).astype(np.float64)

    quantidade = f"{len(nuvem):,}".replace(",", ".")
    print(f"✅ {quantidade} pontos carregados.")
    print(f"   Altura mínima: {nuvem[:, 2].min():.2f} m   |   Altura máxima: {nuvem[:, 2].max():.2f} m")
    return nuvem


def buscar_maior_arvore(nuvem, mostrar_passos=True, pontos_para_desenhar=40000):
    """Procura, passo a passo, o ponto mais alto que realmente pertence a uma árvore.

    A busca começa pelo ponto mais alto da nuvem inteira. Ao redor dele,
    imaginamos um hemisfério (uma "meia bola") de 25 m de raio, virado para
    baixo, com a borda centrada exatamente naquele ponto. Contamos quantos
    pontos existem dentro desse hemisfério.

    Uma árvore de verdade tem uma copa cheia de galhos e folhas por baixo do
    topo, então deve haver pelo menos 300 pontos ali dentro. Se houver menos
    que isso, o ponto escolhido provavelmente não é uma árvore de verdade
    (pode ser, por exemplo, um passarinho ou um eco estranho do laser), e a
    busca continua com o próximo ponto mais alto — até a condição ser
    satisfeita.
    """
    ordem_do_mais_alto_para_o_mais_baixo = np.argsort(nuvem[:, 2])[::-1]
    arvore_espacial = cKDTree(nuvem)
    indices_da_amostra = _amostra_para_desenho(nuvem, pontos_para_desenhar)

    passos_a_testar = min(PASSOS_MAXIMOS_DA_BUSCA, len(nuvem))
    for passo, indice in enumerate(ordem_do_mais_alto_para_o_mais_baixo[:passos_a_testar], start=1):
        candidato = nuvem[indice]
        quantidade = _contar_pontos_no_hemisferio(nuvem, arvore_espacial, candidato)
        aceito = quantidade >= MINIMO_DE_PONTOS_NO_HEMISFERIO

        resultado = "✅ aceito, é uma árvore!" if aceito else "❌ rejeitado, poucos pontos por baixo"
        print(
            f"Passo {passo}: ponto em (X={candidato[0]:.1f}, Y={candidato[1]:.1f}), "
            f"altura {candidato[2]:.2f} m → {quantidade} pontos no hemisfério → {resultado}"
        )

        if mostrar_passos:
            _desenhar_passo(nuvem, indices_da_amostra, arvore_espacial, candidato, quantidade, aceito, passo)

        if aceito:
            print(f"\n🏆 Árvore encontrada! Altura: {candidato[2]:.2f} metros, em {passo} passo(s).")
            return candidato

    print("😕 Nenhum ponto passou no teste do hemisfério.")
    return None


def mostrar_resultado(nuvem, campea, margem_metros=20.0):
    """Mostra o perfil da floresta cortado pela largura do hemisfério testado
    (mais uma margem para os lados), destacando a árvore campeã.
    """
    if campea is None:
        print("Não há árvore campeã para mostrar.")
        return

    meia_largura = RAIO_DO_HEMISFERIO_METROS + margem_metros
    dentro_do_corte = np.abs(nuvem[:, 0] - campea[0]) <= meia_largura
    pontos_do_corte = nuvem[dentro_do_corte]

    largura_da_base = 2 * meia_largura
    altura_dos_dados = pontos_do_corte[:, 2].max() - pontos_do_corte[:, 2].min()
    largura_da_figura = 7.0
    altura_da_figura = largura_da_figura * (altura_dos_dados / largura_da_base)

    plt.figure(figsize=(largura_da_figura, altura_da_figura))
    plt.scatter(pontos_do_corte[:, 0], pontos_do_corte[:, 2], s=2, color="yellowgreen", alpha=0.5)
    plt.scatter(
        campea[0], campea[2], color="gold", edgecolor="black",
        marker="*", s=500, zorder=5,
    )
    plt.gca().set_aspect("equal")
    plt.xlabel("posição ao longo da faixa (m)")
    plt.ylabel("altura acima do solo (m)")
    plt.title("A maior arvore encontrada na faixa")
    plt.tight_layout()
    plt.show()

    print(
        f"A árvore campeã está em X={campea[0]:.2f}, Y={campea[1]:.2f}, "
        f"e tem {campea[2]:.2f} metros de altura!"
    )


# ---------------------------------------------------------------------------
# Funções internas (o "por baixo dos panos")
# ---------------------------------------------------------------------------

def _contar_pontos_no_hemisferio(nuvem, arvore_espacial, candidato):
    vizinhos = arvore_espacial.query_ball_point(candidato, r=RAIO_DO_HEMISFERIO_METROS)
    alturas_dos_vizinhos = nuvem[vizinhos, 2]
    abaixo_ou_na_altura_do_candidato = alturas_dos_vizinhos <= candidato[2]
    return int(np.count_nonzero(abaixo_ou_na_altura_do_candidato))


def _amostra_para_desenho(nuvem, quantidade):
    if len(nuvem) <= quantidade:
        return np.arange(len(nuvem))
    gerador_aleatorio = np.random.default_rng(42)
    return gerador_aleatorio.choice(len(nuvem), size=quantidade, replace=False)


def _desenhar_passo(nuvem, indices_da_amostra, arvore_espacial, candidato, quantidade, aceito, passo):
    amostra = nuvem[indices_da_amostra]
    cor = "darkgreen" if aceito else "crimson"

    # A faixa toda tem quilômetros de comprimento, então sem um zoom na
    # vizinhança do candidato o hemisfério (25 m de raio) fica microscópico
    # e o círculo desaparece no gráfico da vista de cima.
    janela = RAIO_DO_HEMISFERIO_METROS * 1.6
    indices_locais = arvore_espacial.query_ball_point(candidato, r=janela)
    pontos_locais = nuvem[indices_locais]

    figura, (perfil, topo) = plt.subplots(1, 2, figsize=(11, 4.5))
    figura.suptitle(f"Passo {passo} — altura testada: {candidato[2]:.2f} m   |   pontos no hemisfério: {quantidade}")

    # Perfil lateral da floresta (visto de lado): posição X por altura Z,
    # com a nuvem inteira, para mostrar onde o candidato está na faixa toda.
    perfil.scatter(amostra[:, 0], amostra[:, 2], s=1, color="yellowgreen", alpha=0.4)
    perfil.scatter(candidato[0], candidato[2], color=cor, marker="*", s=250, zorder=5)
    perfil.set_xlabel("posição ao longo da faixa (m)")
    perfil.set_ylabel("altura (m)")
    perfil.set_title("Perfil lateral da floresta")

    # Vista de cima: posição X por posição Y, com o círculo do hemisfério.
    topo.scatter(pontos_locais[:, 0], pontos_locais[:, 1], s=4, color="yellowgreen", alpha=0.6)
    topo.scatter(candidato[0], candidato[1], color=cor, marker="*", s=250, zorder=5)
    circulo = plt.Circle(
        (candidato[0], candidato[1]), RAIO_DO_HEMISFERIO_METROS,
        fill=False, linestyle="--", color=cor,
    )
    topo.add_patch(circulo)
    topo.set_xlim(candidato[0] - janela, candidato[0] + janela)
    topo.set_ylim(candidato[1] - janela, candidato[1] + janela)
    topo.set_aspect("equal")
    topo.set_xlabel("X (m)")
    topo.set_ylabel("Y (m)")
    topo.set_title("Vista de cima (zoom)")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    nuvem = carregar_nuvem()
    campea = buscar_maior_arvore(nuvem, mostrar_passos=True)
    mostrar_resultado(nuvem, campea)

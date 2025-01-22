# Classes de objetos:
from classes import Fonte
from classes import Resistor
from classes import No

# Bibliotecas importadas:
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk

from percorre import gerar_caminhos, gerar_equacoes

def criar_grafo_a_partir_de_txt(caminho_txt):
    grafo = nx.DiGraph()
    id_intermediario = 1000  # ID inicial para nós intermediários (números altos para evitar conflitos)
    
    # Lê o arquivo linha por linha
    with open(caminho_txt, 'r') as arquivo:
        for linha in arquivo:
            try:
                partes = linha.strip().split(', ')
                id_objeto = int(partes[0])  # ID do objeto
                tipo_objeto = partes[1]     # Tipo do objeto (F ou R)
                valor = float(partes[2])    # Tensão (para F) ou resistência (para R)
                id_destinos = list(map(int, partes[3].split(';')))  # IDs para onde o nó aponta

                # Cria um objeto da classe No
                no = No(id_objeto, tipo_objeto, valor, id_destinos)

                # Adiciona o nó ao grafo com seus atributos
                atributos = {'tipo': no.tipo}
                if no.tipo == 'F':
                    atributos['tensao'] = no.valor
                elif no.tipo == 'R':
                    atributos['resistencia'] = no.valor
                
                grafo.add_node(no.id, **atributos)

                # Se houver múltiplos destinos, cria um nó intermediário
                if len(no.destinos) > 1:
                    # Adiciona o nó intermediário
                    grafo.add_node(id_intermediario, tipo='Nó')
                    grafo.add_edge(no.id, id_intermediario)

                    # Conecta o nó intermediário aos destinos
                    for destino in no.destinos:
                        grafo.add_edge(id_intermediario, destino)
                    
                    # Incrementa o ID do nó intermediário para o próximo
                    id_intermediario += 1
                else:
                    # Se houver apenas um destino, conecta diretamente
                    for destino in no.destinos:
                        grafo.add_edge(no.id, destino)
            except Exception as e:
                print(f"Erro ao processar a linha: {linha}. Detalhes do erro: {e}")
                
    return grafo


def plotar_grafo(grafo):
    plt.figure(figsize=(12, 9))  # Define o tamanho da figura
    
    # Gera uma posição para os nós
    pos = nx.spring_layout(grafo, seed=42, k=0.5)  # Usa o spring layout para posicionamento
    
    # Desenha os nós com cores distintas para cada tipo
    cores_nos = [
        'orange' if grafo.nodes[n]['tipo'] == 'F' else 
        'lightblue' if grafo.nodes[n]['tipo'] == 'R' else 'gray'
        for n in grafo.nodes()
    ]
    nx.draw_networkx_nodes(
        grafo, pos, node_color=cores_nos, node_size=2000, edgecolors='black'
    )
    
    # Desenha as arestas com curvas suaves para melhor visibilidade
    nx.draw_networkx_edges(
        grafo, pos,
        edgelist=grafo.edges(),
        edge_color='gray',
        width=2,
        arrowstyle='->',
        arrowsize=30,
        connectionstyle='arc3,rad=0.2'
    )
    
    # Adiciona rótulos dos IDs dos nós
    nx.draw_networkx_labels(
        grafo, pos, labels={n: n for n in grafo.nodes()},
        font_size=12, font_color='black', font_weight='bold'
    )
    
    # Adiciona rótulos adicionais (valores de tensão ou resistência)
    for no, (x, y) in pos.items():
        tipo = grafo.nodes[no]['tipo']
        if tipo == 'F':  # Se for uma fonte, mostra a tensão
            atributo_texto = f"Tensão: {grafo.nodes[no]['tensao']}V"
            plt.text(x, y + 0.1, atributo_texto, fontsize=10, color='darkred', ha='center', va='center')
        elif tipo == 'R':  # Se for um resistor, mostra a resistência
            atributo_texto = f"R: {grafo.nodes[no]['resistencia']}Ω"
            plt.text(x, y + 0.1, atributo_texto, fontsize=10, color='darkblue', ha='center', va='center')
        elif tipo == 'intermediario':  # Para nós intermediários, apenas identifica
            plt.text(x, y + 0.1, "Intermediário", fontsize=10, color='gray', ha='center', va='center')

    plt.title("Visualização do Grafo do Circuito", fontsize=16)
    plt.axis('off')  # Remove os eixos
    plt.tight_layout()  # Ajusta os espaços para evitar corte
    plt.show()


if __name__ == "__main__":
    caminho = 'circuito.txt'
    grafo = criar_grafo_a_partir_de_txt(caminho)
    malhas = gerar_caminhos(grafo)

    # Exibe os nós e as arestas do grafo
    print("Nós do grafo:")
    for no, atributos in grafo.nodes(data=True):
        print(f"Nó {no}: {atributos}")

    print("\nArestas do grafo:")
    for aresta in grafo.edges(data=True):
        print(f"Aresta {aresta}")
        
    
    # teste das equaçoes
        
    print("\n\nEquações do circuito: \n")
     
    equacoes, correntes = gerar_equacoes(grafo, malhas)

    for i, eq in enumerate(equacoes, 1):
        print(f"Equação da Malha {i}: {eq}")

    # Plota o grafo
    plotar_grafo(grafo)
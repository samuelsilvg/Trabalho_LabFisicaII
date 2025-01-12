# Classes de objetos:
from classes import Fonte
from classes import Resistor

# Bibliotecas importadas:
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk

def criar_grafo_a_partir_de_txt(caminho_txt):
    grafo = nx.DiGraph() 
    
    # Lê o arquivo linha por linha
    with open(caminho_txt, 'r') as arquivo:
        for linha in arquivo:

            partes = linha.strip().split(', ')
            id_objeto = int(partes[0])  # ID do objeto
            tipo_objeto = partes[1]     # Tipo do objeto (F ou R)
            valor = float(partes[2])    # Tensão (para F) ou resistência (para R)
            id_destino = int(partes[3]) # ID para onde o nó aponta
            
            # Cria um dicionário de atributos
            atributos = {'tipo': tipo_objeto}
            if tipo_objeto == 'F':
                atributos['tensao'] = valor
            elif tipo_objeto == 'R':
                atributos['resistencia'] = valor
            
            grafo.add_node(id_objeto, **atributos)
            grafo.add_edge(id_objeto, id_destino)

    return grafo

def plotar_grafo(grafo):
    plt.figure(figsize=(8, 6))  # Define o tamanho da figura
    
    # Gera uma posição para os nós
    pos = nx.spring_layout(grafo, seed=42)  # Layout do grafo
    
    # Desenha os nós
    nx.draw_networkx_nodes(grafo, pos, node_color='lightblue', node_size=1000)
    
    # Desenha as arestas de forma paralela para visualização clara
    nx.draw_networkx_edges(
        grafo, 
        pos, 
        edgelist=grafo.edges(), 
        edge_color='gray', 
        arrowstyle='->', 
        arrowsize=20, 
        connectionstyle='arc3,rad=0.2'  # Curva as arestas para que fiquem visíveis
    )
    
    # Adiciona rótulos de ID dos nós
    nx.draw_networkx_labels(grafo, pos, labels={n: n for n in grafo.nodes()}, font_size=12, font_color='black')
    
    # Adiciona rótulos para os atributos dos nós
    atributos_labels = {
        no: f"{grafo.nodes[no]['tipo']} ({grafo.nodes[no].get('tensao', grafo.nodes[no].get('resistencia', ''))})"
        for no in grafo.nodes()
    }
    nx.draw_networkx_labels(grafo, pos, labels=atributos_labels, font_size=10, font_color='darkred', verticalalignment='bottom')

    plt.title("Visualização do Grafo do Circuito")
    plt.axis('off')  # Remove os eixos
    plt.show()


# MAIN
caminho = 'circuito.txt'
grafo = criar_grafo_a_partir_de_txt(caminho)

# Exibe os nós e as arestas do grafo
print("Nós do grafo:")
for no, atributos in grafo.nodes(data=True):
    print(f"Nó {no}: {atributos}")

print("\nArestas do grafo:")
for aresta in grafo.edges(data=True):
    print(f"Aresta {aresta}")

# Plota o grafo
plotar_grafo(grafo)
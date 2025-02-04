# Classes de objetos:
from classes import Fonte
from classes import Resistor
from classes import No

# Bibliotecas importadas:
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import messagebox
from sympy import symbols, Eq, solve, sympify
import re

# Funcoes importadas de outros arquivos .py:
from percorre import gerar_caminhos, gerar_equacoes, normalizar_equacoes, simplificar_correntes, normalizar_incognitas, remover_indices_desnecessarios, resolver_equacoes

#==========================================================================#
# FUNÇÕES DE GERAÇÃO:

def criar_grafo_a_partir_de_txt(caminho_txt):
    grafo = nx.DiGraph()
    id_intermediario = 1000  # ID inicial para nós intermediários (evitar conflitos)
    destinos_compartilhados = {}  # Mapeia destinos compartilhados para identificar intermediários

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

                # Caso o nó tenha múltiplos destinos, cria um nó intermediário
                if len(no.destinos) > 1:
                    grafo.add_node(id_intermediario, tipo='Nó')
                    grafo.add_edge(no.id, id_intermediario)

                    for destino in no.destinos:
                        grafo.add_edge(id_intermediario, destino)
                    
                    # Incrementa o ID do nó intermediário
                    id_intermediario += 1
                else:
                    # Caso contrário, conecta diretamente ao único destino
                    for destino in no.destinos:
                        grafo.add_edge(no.id, destino)

                # Atualiza os destinos compartilhados
                for destino in no.destinos:
                    if destino not in destinos_compartilhados:
                        destinos_compartilhados[destino] = []  # Inicializa lista de fontes para o destino
                    destinos_compartilhados[destino].append(no.id)

            except Exception as e:
                print(f"Erro ao processar a linha: {linha}. Detalhes do erro: {e}")

    # Verifica destinos compartilhados e cria nós intermediários adicionais, se necessário
    for destino, fontes in destinos_compartilhados.items():
        if len(fontes) > 1:
            # Cria um nó intermediário para as conexões compartilhadas
            grafo.add_node(id_intermediario, tipo='Nó')

            # Conecta os nós que apontavam diretamente para o destino ao nó intermediário
            for fonte in fontes:
                # Remove a aresta direta antes de criar a intermediária
                if grafo.has_edge(fonte, destino):
                    grafo.remove_edge(fonte, destino)
                grafo.add_edge(fonte, id_intermediario)

            # Conecta o nó intermediário ao destino
            grafo.add_edge(id_intermediario, destino)
            id_intermediario += 1

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

def rotina_geradora():
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
    #print("\n\nEquações do circuito: \n")
     
    equacoes, correntes = gerar_equacoes(grafo, malhas)
    equacoes = normalizar_equacoes(equacoes)

    # Simplifica correntes equivalentes
    substituicoes = simplificar_correntes(grafo, correntes)

    # Aplica as substituições às equações
    equacoes_simplificadas = []
    for equacao in equacoes:
        for antiga, nova in substituicoes.items():
            equacao = equacao.replace(antiga, nova)
        equacoes_simplificadas.append(equacao)

    # Exibe as equações simplificadas e salva em txt
    with open("equacoes.txt", "w") as file:
        #print("\nEquações Simplificadas:")
        for i, eq in enumerate(equacoes_simplificadas, 1):
            #print(f"Equação da Malha {i}: {eq}")
            file.write(f"Equação da Malha {i}: {eq}\n")

    equacoes_normalizadas = [normalizar_incognitas(eq) for eq in equacoes_simplificadas]
    equacoes_simplificadas = [remover_indices_desnecessarios(eq) for eq in equacoes_normalizadas]
    solucoes = resolver_equacoes(equacoes_simplificadas[:3])
    
    with open("texts/solucoes.txt", "w") as file:
        for var, valor in solucoes.items():
            file.write(f"{var} = {valor.evalf():.4f} A\n")
    return equacoes_simplificadas

#==========================================================================#
# FUNÇÕES DE INTERFACE:

def iniciar_interface():
   
    def gerar_titulo():
        with open("texts/titulo.txt", "r") as file:
            conteudo = file.read()
            titulo = tk.Label(janela, text=conteudo, font=("Consolas", 11, "normal"), justify="center")
            return titulo
        
    def gerar_janela2():

        def salvar_arquivo():
            with open("texts/circuito.txt", "w") as file:
                novo_txt = ed_txt.get("1.0", tk.END).strip()
                file.write(novo_txt)
                messagebox.showinfo("Sucesso", "Arquivo salvo com sucesso!")
                file.close()


        # Janela 2
        janela2 = tk.Toplevel()
        janela2.title("Editar TXT")
        janela2.geometry("600x600")

        ed_txt = tk.Text(janela2)
        ed_txt.pack(fill="both", expand=True)

        with open("texts/circuito.txt", "r") as file:
            texto = file.read()
            ed_txt.insert(tk.END, texto)

        btn_salvar = tk.Button(janela2, text = 'Salvar no arquivo', command=salvar_arquivo, font=("Consolas", 11), justify="center")
        btn_salvar.pack(pady=10)

        btn_voltar = tk.Button(janela2, text = 'Fechar', command=janela2.destroy, font=("Consolas", 11), justify="center")
        btn_voltar.pack(pady=5)

    def gerar_janela3():
        
        # Janela 3
        janela3 = tk.Toplevel()
        janela3.title("Resolução do Circuito")
        janela3.geometry("600x600")

        eq_txt = tk.Text(janela3)
        eq_txt.pack(fill="both", expand=True)

        rotina_geradora() # Atualiza as equações

        with open("texts/equacoes.txt", "r") as file:
            eqs = file.read()
            eq_txt.insert(tk.END, eqs)

        btn_voltar = tk.Button(janela3, text = 'Fechar', command=janela3.destroy, font=("Consolas", 11), justify="center")
        btn_voltar.pack(pady=5)
    
    def gerar_janela4():
        
        #Janela 4
        janela4= tk.Toplevel()
        janela4.title("Solução das Correntes")
        janela4.geometry("600x600")
        
        eq_txt = tk.Text(janela4)
        eq_txt.pack(fill="both", expand=True)
        
        with open("texts/solucoes.txt", "r") as file:
            respostas = file.read()
            eq_txt.insert(tk.END, respostas)
            
        btn_voltar = tk.Button(janela4, text = 'Fechar', command=janela4.destroy, font=("Consolas", 11), justify="center")
        btn_voltar.pack(pady=5)
        
    # Criação da janela
    janela = tk.Tk()
    janela.title("Simulador de Circuitos com Grafo")
    janela.geometry("1200x600")

    label_titulo = gerar_titulo()
    label_titulo.pack(pady=20, expand=True)


    # Botões
    btn_editar = tk.Button(janela, text="Editar Arquivo TXT", command=gerar_janela2, font=("Consolas", 11), justify="center")
    btn_editar.pack(pady=10)

    btn_carregar = tk.Button(janela, text="Carregar Arquivo e Processar", command=gerar_janela3, font=("Consolas", 11), justify="center")
    btn_carregar.pack(pady=10)
    
    btn_carregar = tk.Button(janela, text = "Solução das Correntes", command=gerar_janela4, font=("Consolas", 11), justify="center")
    btn_carregar.pack(pady=10)
    
    btn_sair = tk.Button(janela, text="Sair", command=janela.destroy, font=("Consolas", 11))
    btn_sair.pack(pady=10)


    janela.mainloop()

#==========================================================================#
# MAIN:

rotina_geradora()
iniciar_interface()

#==========================================================================#
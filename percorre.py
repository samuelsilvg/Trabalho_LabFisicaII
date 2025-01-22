import networkx as nx
import re

def gerar_caminhos(grafo):
    caminhos = list(nx.simple_cycles(grafo))
    
    return caminhos

def gerar_equacoes(grafo, malhas):
    equacoes = []
    correntes = {} 

    # Itera sobre cada malha
    for i, malha in enumerate(malhas):
        equacao = []
        for j, no in enumerate(malha):
            #próximo nó na malha 
            proximo_no = malha[(j + 1) % len(malha)]
            
            if grafo.has_edge(no, proximo_no):
                tipo = grafo.nodes[no].get('tipo')
                
                # Fonte
                if tipo == 'F':
                    tensao = grafo.nodes[no].get('tensao')
                    if tensao:
                        equacao.append(f"+ {tensao}")
                
                # Resistor
                elif tipo == 'R':
                    resistencia = grafo.nodes[no].get('resistencia')
                    if resistencia:
                        # Variável de corrente única para cada resistor
                        corrente = f"I_{no}_{proximo_no}"
                        correntes[(no, proximo_no)] = corrente
                        equacao.append(f"- {resistencia}*{corrente}")
        
        equacoes.append(" + ".join(equacao) + " = 0")
    
    return equacoes, correntes

def normalizar_equacoes(equacoes):
    equacoes_normalizadas = []

    for equacao in equacoes:
        # Substitui "++"  por "+"
        equacao = re.sub(r'\+\s*\+', '+', equacao)

        # Substitui "+-" ou "-+" por "-"
        equacao = re.sub(r'\+\s*-\s*|\-\s*\+\s*', '-', equacao)

        # Substitui "--" por "-"
        equacao = re.sub(r'-\s*-', '-', equacao)

        # Remover sinais de "+" no início da equação
        equacao = re.sub(r'^\s*\+', '', equacao)

        equacoes_normalizadas.append(equacao)

    return equacoes_normalizadas
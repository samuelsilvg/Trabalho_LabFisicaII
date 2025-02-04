import networkx as nx
import re
import sympy as sp


def gerar_caminhos(grafo):
    caminhos = list(nx.simple_cycles(grafo))
    
    return caminhos

def gerar_equacoes(grafo, malhas):
    equacoes_malha = []  # Lista de equações de malha
    equacoes_nos = []  # Lista de equações para os nós (LNK)
    correntes = {}  # Mapeamento de corrente para cada aresta

    # Identificar variáveis de corrente para cada aresta
    for u, v in grafo.edges():
        corrente = f"I_{u}_{v}"  # Nome da corrente baseado nos nós
        correntes[(u, v)] = corrente

    # 1. Equações de malha (LMK)
    for malha in malhas:
        equacao = []
        for i, no in enumerate(malha):
            proximo_no = malha[(i + 1) % len(malha)]  # Próximo nó na malha
            
            if grafo.has_edge(no, proximo_no):
                tipo = grafo.nodes[no].get('tipo')
                
                # Fonte de tensão
                if tipo == 'F':
                    tensao = grafo.nodes[no].get('tensao', 0)
                    equacao.append(f"+ {tensao}")
                
                # Resistor
                elif tipo == 'R':
                    resistencia = grafo.nodes[no].get('resistencia', 0)
                    corrente = correntes[(no, proximo_no)]  # Corrente associada à aresta
                    equacao.append(f"- {resistencia}*{corrente}")
        
        # Adiciona a equação de malha
        equacoes_malha.append(" + ".join(equacao) + " = 0")

    # 2. Equações dos nós intermediários (LNK)
    for no in grafo.nodes:
        if grafo.nodes[no].get('tipo') == 'Nó':  # Verifica se é um nó intermediário
            entradas = [correntes[(u, no)] for u in grafo.predecessors(no)]  # Correntes que entram no nó
            saidas = [correntes[(no, v)] for v in grafo.successors(no)]  # Correntes que saem do nó

            # Soma das correntes que entram = Soma das correntes que saem
            equacao_no = " + ".join(entradas) + " - (" + " + ".join(saidas) + ") = 0"
            equacoes_nos.append(equacao_no)

    # Retorna as equações de malha e de nós
    return equacoes_malha + equacoes_nos, correntes


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


def simplificar_correntes(grafo, correntes):
    #Rastreia os nós para tentar minimizar duplicatas
    substituicoes = {}  # Mapeamento de correntes a serem substituídas

    for no in grafo.nodes:
        # Verifica se o nó é intermediário
        if grafo.nodes[no].get('tipo') == 'Nó':
            sucessores = list(grafo.successors(no))  # Nós para onde o nó aponta
            predecessores = list(grafo.predecessors(no))  # Nós que apontam para o nó

            # Caso especial: só um sucessor e um predecessor
            if len(sucessores) == 1 and len(predecessores) == 1:
                corrente_entrada = correntes[(predecessores[0], no)]
                corrente_saida = correntes[(no, sucessores[0])]
                substituicoes[corrente_saida] = corrente_entrada  # Substitui a saída pela entrada

    return substituicoes

def normalizar_incognitas(equacao):
    # Função para reformatar cada variável encontrada
    def ordenar_variavel(match):
        x, y = sorted(match.groups(), key=int)
        return f"I_{x}_{y}"

    # Substituir todas as ocorrências de I_x_y pela forma ordenada
    equacao_normalizada = re.sub(r'I_(\d+)_(\d+)', ordenar_variavel, equacao)
    return equacao_normalizada


def remover_indices_desnecessarios(equacao):
    # Substituir todas as ocorrências de _1000 ou _1001 por uma string vazia
    equacao_simplificada = re.sub(r'(_1000|_1001)', '', equacao)
    return equacao_simplificada

def resolver_equacoes(equacoes):
    variaveis = set()
    equacoes_sympy = []

    for eq in equacoes:
        # Extrair variáveis da equação usando regex
        variaveis_encontradas = re.findall(r'I_\d+', eq)
        variaveis.update(variaveis_encontradas)

        # Converter a equação para uma expressão sympy
        eq_sympy = sp.sympify(eq.replace('=', '-(') + ')')  # Transforma "a = b" em "a - (b) = 0"
        equacoes_sympy.append(eq_sympy)

    # Definir as variáveis simbólicas no SymPy
    variaveis_sympy = sp.symbols(' '.join(variaveis))

    # Resolver o sistema de equações
    solucoes = sp.solve(equacoes_sympy, variaveis_sympy)
    return solucoes
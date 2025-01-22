from main import nx, np, plt, criar_grafo_a_partir_de_txt

caminho = 'circuito.txt'
grafo = criar_grafo_a_partir_de_txt(caminho)

caminhos = list(nx.simple_cycles(grafo))

print(caminhos)

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

# ---------- teste

malhas = caminhos
equacoes, correntes = gerar_equacoes(grafo, malhas)

for i, eq in enumerate(equacoes, 1):
    print(f"Equação da Malha {i}: {eq}")

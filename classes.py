class Fonte:

    def __init__(self, tensao):
        self.tensao = tensao
        
    def __str__(self):
        return f'{self.tensao}'
    
class Resistor:

    def __init__(self, resistencia, corrente):
        self.resistencia = resistencia
        self.corrente = corrente
        
    def __str__(self):
        return f'{self.resistencia} | {self.corrente}'
    
class No:
    
    def __init__(self, id_objeto, tipo_objeto, valor, destinos):
        self.id = id_objeto
        self.tipo = tipo_objeto 
        self.valor = valor  
        self.destinos = destinos

    def __str__(self):
        return f"No(ID={self.id}, Tipo={self.tipo}, Valor={self.valor}, Destinos={self.destinos})"
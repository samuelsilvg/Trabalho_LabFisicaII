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
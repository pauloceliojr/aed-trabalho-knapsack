# Main greedy function to solve problem

class GreedyKnapsack:

    def __init__(self, capacidade, itens, fractional=False):
        self.capacidade = capacidade
        self.itens = itens.sort_values(by="valor_por_peso", ascending=False)
        self.fractional = fractional

    def max(self):

        # Result(value in Knapsack)
        valor_maximo = 0
        peso_maximo = 0
        # itens_selecionados = []
        capacidade_restante = self.capacidade

        # Looping through all Items
        for indice, item in self.itens.iterrows():
            # If adding Item won't overflow, add it completely
            if item.peso <= capacidade_restante:
                capacidade_restante -= item.peso
                valor_maximo += item.valor
                peso_maximo += item.peso
                # itens_selecionados.append(str(int(linha.valor)))
            # If we can't add current Item, add fractional part
            # of it
            else:
                if self.fractional:
                    valor_maximo += capacidade_restante * item.valor_por_peso #multiplica a capacidade restante pelo razão valor/peso para encontrar o valor proporcional e somar ao valor máximo já encontrado
                    peso_maximo += item.peso * (capacidade_restante / self.capacidade)
                    # itens_selecionados.append(f"{int(linha.valor)} ({int(capacidade - lista.iloc[index - 1].peso)}/{int(linha.peso)})")
                    break

        # Returning final value
        # return valor_maximo, itens_selecionados
        return valor_maximo, peso_maximo




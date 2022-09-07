import pandas


class BruteForceKnapsack:

    def __init__(self, capacidade, itens):
        self.capacidade = capacidade
        self.itens = itens

    def _weight(self, item):
        return item[0]

    def _value(self, item):
        return item[1]

    def _powerset(self, items):
        res = [[]]
        for item in items:
            newset = [r+[item] for r in res]
            res.extend(newset)
        return res

    def max(self):
        knapsack = []
        best_weight = 0
        best_value = 0
        for item_set in self._powerset(self.itens.filter(["peso", "valor"]).values.tolist()):
            set_weight = sum(map(self._weight, item_set))
            set_value = sum(map(self._value, item_set))
            if set_value > best_value and set_weight <= self.capacidade:
                best_weight = set_weight
                best_value = set_value
                knapsack = item_set
        # return knapsack, best_weight, best_value
        return best_value, best_weight


# A Dynamic Programming based Python
# Program for 0-1 Knapsack problem
# Returns the maximum valor that can
# be put in a knapsack of capacity capacidade
class DynamicProgrammingKnapsack:

    def __init__(self, capacidade, itens):
        self.capacidade = capacidade
        self.itens = itens

    def _print_selected_elements(self, dp, profits, weights, capacity):
        print("Selected weights are: ", end='\n')
        n = len(dp)
        delta = len(dp) - len(weights)

        totalProfit = dp[n - 1][capacity]
        for i in range(n - 1, 0, -1):
            if totalProfit != dp[i - 1][capacity]:
                print(str(weights[i - delta]) + " ", end='')
                # print(self.itens.iloc[0])
                capacity -= weights[i - delta]
                totalProfit -= profits[i - delta]

        if totalProfit != 0:
            print(str(weights[0]) + " ", end='')
            # print(self.itens.iloc[0])
        # print()

    def _knapsack_topdown(self, dp, profits, weights, capacity, currentIndex):

        # base checks
        if capacity == 0 or currentIndex == 0:
            return 0

        # if we have already solved a similar problem, return the result from memory
        if dp[currentIndex - 1][capacity] != -1:
            return dp[currentIndex - 1][capacity]

        # recursive call after choosing the element at the currentIndex
        # if the weight of the element at currentIndex exceeds the capacity, we
        # shouldn't process this
        if weights[currentIndex - 1] > capacity:
            dp[currentIndex - 1][capacity] = self._knapsack_topdown(
                dp, profits, weights, capacity, currentIndex - 1)
        else:
            # recursive call after excluding the element at the currentIndex
            dp[currentIndex - 1][capacity] = max(self._knapsack_topdown(
                dp, profits, weights, capacity, currentIndex - 1), profits[currentIndex - 1] + self._knapsack_topdown(
                dp, profits, weights, capacity - weights[currentIndex - 1], currentIndex - 1))

        return dp[currentIndex - 1][capacity]

    # code
    # A Dynamic Programming based Python
    # Program for 0-1 Knapsack problem
    # Returns the maximum value that can
    # be put in a knapsack of capacity W
    def _knapsack_bottomup(self):
        wt = self.itens.peso.tolist()
        val = self.itens.valor.tolist()
        W = self.capacidade
        n = len(val)

        K = [[0 for x in range(W + 1)] for x in range(n + 1)]

        # Build table K[][] in bottom up manner
        for i in range(n + 1):
            for w in range(W + 1):
                if i == 0 or w == 0:
                    K[i][w] = 0
                elif wt[i-1] <= w:
                    K[i][w] = max(val[i-1]
                                  + K[i-1][w-wt[i-1]],
                                  K[i-1][w])
                else:
                    K[i][w] = K[i-1][w]

        self._print_selected_elements(K, val, wt, W)

        return K[n][W]

    def max(self, bottomup=True):
        if bottomup:
            result = self._knapsack_bottomup()
        else:
            # create a two dimensional array for Memoization, each element is initialized to '-1'
            dp = [[-1 for x in range(self.capacidade + 1)] for y in range(len(self.itens))]
            result = self._knapsack_topdown(dp, self.itens.valor.tolist(), self.itens.peso.tolist(), self.capacidade, len(self.itens))
            self._print_selected_elements(dp, self.itens.valor.tolist(), self.itens.peso.tolist(), self.capacidade)
        return result


#     0-1 Knapsack Problem using best first branch and limitante_dual method
#     Returns limitante_primal with list storing the index position of the items in the best solution.
#     The valor is maximized while staying under the peso limit.
#     This program uses a priority queue to store the nodes ordered by best limitante_dual,
#     the node with the highest limitante_dual valor is returned when removing from the priority queue.
#     The best first approach arrives at an optimal solition faster than breadth first search.
class BranchAndBoundKnapsack:
    def __init__(self, capacidade, itens):
        self.capacidade = capacidade
        self.itens = itens.sort_values(by="valor_por_peso", ascending=False) # pressupõe a ordenação decrescente

    class PriorityQueue:
        def __init__(self):
            self.pqueue = []
            self.tamanho = 0

        def inserir(self, node):
            # Caso seja informado algum nó e o peso dos itens que o compõem esteja acima da capacidade máxima,
            # o nó não será adicionado na fila de prioridade (poda por inviabilidade)
            if node is not None and not node.peso_acima_da_capacidade:
                i = 0
                # Ordenação em ordem crescente da fila de acordo com limitante dual
                while i < len(self.pqueue):
                    if self.pqueue[i].limitante_dual > node.limitante_dual:
                        break
                    i += 1
                self.pqueue.insert(i, node)
                self.tamanho += 1

        def remover(self):
            try:
                # será retornado o último nó que correponde àquele com maior limitante dual encontrado
                node = self.pqueue.pop()
                self.tamanho -= 1
            except:
                print("Não foi possível remover node da fila: fila de prioridade vazia.")
            else:
                return node

    class Node:
        def __init__(self, capacidade, itens):
            self.capacidade = capacidade
            self.itens = itens
            self.indice_fracionado = -1
            self.caminho = {}
            self._limitante_dual = -1
            self._valor = 0
            self._peso = 0
            self._retorno = 0

        @property
        def limitante_dual(self):
            if self._limitante_dual == -1:
                self._limitante_dual = 0
                capacidade_restante = self.capacidade
                itens = self.itens.copy()
                itens["obrigatorio"] = 0
                if len(self.caminho) > 0:
                    indices_mantidos = itens.index.values.tolist()
                    indices_excluidos = []
                    for chave, valor in self.caminho.items():
                        if valor <= 0:
                            indices_excluidos.append(chave)
                        elif valor >= 1:
                            itens.at[chave, "obrigatorio"] = 1
                            indices_mantidos.insert(0, indices_mantidos.pop(indices_mantidos.index(chave)))
                    itens = itens.reindex(indices_mantidos)
                    itens = itens.drop(indices_excluidos)

                # Aqui serão calculados: limitante dual, valor e peso
                for indice, item in itens.iterrows():
                    # Adiciona os itens até antes de estourar a capacidade restante
                    if item.peso <= capacidade_restante or item.obrigatorio:
                        capacidade_restante -= item.peso
                        self._valor += item.valor
                        self._peso += item.peso
                        self._retorno += item.retorno
                    # Se não pudar o item inteiro, adiciona a fração do peso
                    else:
                        if capacidade_restante > 0:
                            # Marcação de qual o índice do item fracionário para ramificação dos filhos
                            self.indice_fracionado = indice
                            self._limitante_dual = capacidade_restante * item.valor_por_peso
                        break

                self._limitante_dual += self._valor
            return self._limitante_dual

        @property
        def retorno(self):
            _ = self.limitante_dual

            return self._retorno

        @property
        def valor(self):
            _ = self.limitante_dual

            return self._valor

        @property
        def peso(self):
            _ = self.limitante_dual

            return self._peso

        @property
        def peso_acima_da_capacidade(self):
            return self.peso > self.capacidade

        def ramificar(self):
            # Se existir índice de item com valor fracionado
            if self.indice_fracionado >= 0:
                # definindo ramo xi <= 0
                filho1 = BranchAndBoundKnapsack.Node(self.capacidade, self.itens)
                filho1.caminho[self.indice_fracionado] = 0  # xi <= 0
                filho1.caminho.update(self.caminho)

                # definindo ramo xi >= 1
                filho2 = BranchAndBoundKnapsack.Node(self.capacidade, self.itens)
                filho2.caminho[self.indice_fracionado] = 1  # xi >= 1
                filho2.caminho.update(self.caminho)

                return filho1, filho2

            return None, None

    def max(self):
        pq = self.PriorityQueue()

        node = self.Node(self.capacidade, self.itens)
        limitante_primal = 0  # Solução ótima encontrada. Neste caso, começa com zero.

        if node.limitante_dual > 0:
            pq.inserir(node)

            while pq.tamanho != 0:
                node = pq.remover()  # remove node with best limitante_dual

                # Antes de ramificar, verifica se existe elemento com limitante dual composto por valor fracionado.
                # Se existir e ele for maior que o limitante primal (solução ótima já encontrada), o nó é descartado
                # (poda por limitante)
                if node.indice_fracionado > -1 and node.limitante_dual > limitante_primal:
                    filho1, filho2 = node.ramificar()

                    pq.inserir(filho1)
                    pq.inserir(filho2)
                elif node.valor > limitante_primal:
                    limitante_primal = node.valor
                    retorno_maximo = node.retorno
                    peso_maximo = node.peso

        return retorno_maximo\
            , peso_maximo


if __name__ == "__main__":
    from datetime import datetime
    import pandas as pd

    dados = {"valor": [60, 100, 120, 50],
             "peso": [10, 20, 30, 50]}
    capacidade = 50

    # dados = {"valor": [10, 21, 50, 51],
    #          "peso": [2, 3, 5, 6]}
    # capacidade = 7

    itens = pd.DataFrame(dados)

    # capacidade = 6200000 * 100
    # itens = pd.read_excel("proposicoes_STI_2023.xlsx", sheet_name="Tratado")
    # itens = itens.filter(["Ação", "GUT", "Unidade Total"]).rename(columns={"Ação": "acao", "GUT": "valor",
    #                                                                        "Unidade Total": "peso_original"})
    # itens["peso"] = itens.peso_original * 100
    itens["valor_por_peso"] = itens.valor / itens.peso

    inicio_processamento = datetime.now()
    knapsack = DynamicProgrammingKnapsack(capacidade, itens)
    print(f"Valor máximo que obtemos = {knapsack.max(bottomup=False)}")
    fim_processamento = datetime.now()
    print("Tempo de processamento:", fim_processamento - inicio_processamento)
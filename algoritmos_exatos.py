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
        return best_value


# A Dynamic Programming based Python
# Program for 0-1 Knapsack problem
# Returns the maximum valor that can
# be put in a knapsack of capacity capacidade
class DynamicProgrammingKnapsack:

    def __init__(self, capacidade, itens):
        self.capacidade = capacidade
        self.itens = itens

    def print_selected_elements(self, dp, weights, profits, capacity):
        print("Selected weights are: ", end='')
        n = len(weights)
        totalProfit = dp[n-1][capacity]
        for i in range(n-1, 0, -1):
            if totalProfit != dp[i - 1][capacity]:
                print(str(weights[i]) + " ", end='')
                capacity -= weights[i]
                totalProfit -= profits[i]

        if totalProfit != 0:
            print(str(weights[0]) + " ", end='')
        print()

    def knapsack_recursive(self, dp, profits, weights, capacity, currentIndex):

        # base checks
        if capacity <= 0 or currentIndex >= len(profits):
            return 0

        # if we have already solved a similar problem, return the result from memory
        if dp[currentIndex][capacity] != -1:
            return dp[currentIndex][capacity]

        # recursive call after choosing the element at the currentIndex
        # if the weight of the element at currentIndex exceeds the capacity, we
        # shouldn't process this
        profit1 = 0
        if weights[currentIndex] <= capacity:
            profit1 = profits[currentIndex] + self.knapsack_recursive(
                dp, profits, weights, capacity - weights[currentIndex], currentIndex + 1)

        # recursive call after excluding the element at the currentIndex
        profit2 = self.knapsack_recursive(
            dp, profits, weights, capacity, currentIndex + 1)

        dp[currentIndex][capacity] = max(profit1, profit2)

        return dp[currentIndex][capacity]

    def max(self):
        # create a two dimensional array for Memoization, each element is initialized to '-1'
        dp = [[-1 for x in range(self.capacidade + 1)] for y in range(len(self.itens))]
        result = self.knapsack_recursive(dp, self.itens.valor.tolist(), self.itens.peso.tolist(), self.capacidade, 0)
        print(self.print_selected_elements(dp, self.itens.valor.tolist(), self.itens.peso.tolist(), self.capacidade))
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

        return limitante_primal

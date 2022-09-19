"""Classes base para os algoritmos exatos."""

# Author: Paulo Célio Júnior <pauloceliojr@gmail.com>

import numpy as np
import pandas as pd


class BruteForceKnapsack:
    """
    Classe que implementa a solução de um Problema de Mochila Binária (0-1 Knapsack Problem) utilizando algoritmo
    de força bruta.
    """

    def __init__(self, valor_disponivel, itens):
        self.valor_disponivel = valor_disponivel
        self.itens = itens

    def _peso(self, item):
        return item[0]

    def _valor(self, item):
        return item[1]

    def _powerset(self, items):
        res = [[]]
        for item in items:
            novoset = [r + [item] for r in res]
            res.extend(novoset)
        return res

    def solucionar(self):
        knapsack = []
        melhor_valor = 0
        melhor_importancia = 0
        for item_set in self._powerset(self.itens.filter(["valor", "importancia"]).values.tolist()):
            set_valor = sum(map(self._peso, item_set))
            set_importancia = sum(map(self._valor, item_set))
            if set_importancia > melhor_importancia and set_valor <= self.valor_disponivel:
                melhor_valor = set_valor
                melhor_importancia = set_importancia
                knapsack = item_set
        print(knapsack)
        return melhor_importancia, melhor_valor


class DynamicProgrammingKnapsack:
    """
    Classe que implementa a solução de um Problema de Mochila Binária (0-1 Knapsack Problem) usando algoritmos de Programação
    Dinâmica.
    """

    def __init__(self, valor_disponivel, itens):
        self.valor_disponivel = valor_disponivel
        self.itens = itens

    def _get_elementos_selecionados(self, dp, importancia, valor, capacidade):
        n = len(dp)
        delta = len(dp) - len(valor)

        importancia_maxima = dp[n - 1][capacidade]
        for i in range(n - 1, 0, -1):
            if importancia_maxima != dp[i - 1][capacidade]:
                print(str(valor[i - delta]) + " ", end='')
                capacidade -= valor[i - delta]
                importancia_maxima -= importancia[i - delta]

        if importancia_maxima != 0:
            print(str(valor[0]) + " ", end='')

    # def _dp_topdown(self, dp, importancia, peso, capacidade, indice=0):
    #     capacidade = int(capacidade)
    #     # Caso base
    #     if capacidade <= 0 or indice >= len(importancia):
    #         return 0
    #
    #     # Se um problema similar já foi resolvido, retorna o resultado da tabela memoização
    #     if dp[indice][capacidade] != -1:
    #         return dp[indice][capacidade]
    #
    #     # Chamada recursiva depois de se escolher o elemento no índice corrente
    #     # Se o valor do elemento no índice atual excede a capacidade, não é processado
    #     importancia1 = 0
    #     if peso[indice] <= capacidade:
    #         importancia1 = importancia[indice] + self._dp_topdown(dp, importancia, peso, capacidade - peso[indice], indice + 1)
    #
    #     # Chamada recursiva depois de se excluir o elemento no índice corrente
    #     importancia2 = self._dp_topdown(dp, importancia, peso, capacidade, indice + 1)
    #
    #     dp[indice][capacidade] = max(importancia1, importancia2)
    #
    #     return dp[indice][capacidade]

    def _dp_topdown_pandas(self, dp, importancia, peso, capacidade, indice=0):
        # Caso base
        if capacidade <= 0 or indice >= len(importancia):
            return 0
        elif f"{capacidade:0.2f}" not in dp.columns:
            dp = pd.concat([dp, pd.DataFrame(np.repeat(-1, len(importancia)), index=[i for i in range(len(self.itens))],
                                             columns=[f"{capacidade:0.2f}"])], axis=1)

        # Se um problema similar já foi resolvido, retorna o resultado da tabela memoização
        if dp.iloc[indice][f"{capacidade:0.2f}"] != -1:
            return dp.iloc[indice][f"{capacidade:0.2f}"]

        # Chamada recursiva depois de se escolher o elemento no índice corrente
        # Se o valor do elemento no índice atual excede a capacidade, não é processado
        importancia1 = 0
        if peso[indice] <= capacidade:
            importancia1 = importancia[indice] + self._dp_topdown_pandas(dp, importancia, peso,
                                                                         capacidade - peso[indice], indice + 1)

        # Chamada recursiva depois de se excluir o elemento no índice corrente
        importancia2 = self._dp_topdown_pandas(dp, importancia, peso, capacidade, indice + 1)

        dp.at[indice, f"{capacidade:0.2f}"] = max(importancia1, importancia2)

        return dp.iloc[indice][f"{capacidade:0.2f}"]

    # def _dp_bottomup(self):
    #     valor = self.itens.valor.tolist()
    #     importancia = self.itens.importancia.tolist()
    #     n = len(importancia)
    #
    #     # Cria um array bi-dimensional para memoização, cada elemento inicializado com o valor "0"
    #     K = [[0 for x in range(int(self.valor_disponivel) + 1)] for x in range(n + 1)]
    #
    #     # Constroi a tabela K[][]
    #     for i in range(n + 1):
    #         for w in range(int(self.valor_disponivel) + 1):
    #             if i == 0 or w == 0:
    #                 K[i][w] = 0
    #             elif valor[i - 1] <= w:
    #                 K[i][w] = max(importancia[i - 1] + K[i - 1][w - int(valor[i - 1])], K[i - 1][w])
    #             else:
    #                 K[i][w] = K[i - 1][w]
    #
    #     # self._get_elementos_selecionados(K, importancia, valor, self.valor_disponivel)
    #
    #     # Retorna a última célula da tabela K
    #     return K[n][self.valor_disponivel]

    def _dp_bottomup_pandas(self):
        # Cria um array bi-dimensional para memoização, cada elemento inicializado com o valor "0"
        K = pd.DataFrame(np.repeat(0, len(self.itens + 1)), index=[i for i in range(len(self.itens + 1))],
                         columns=[str(self.valor_disponivel)])

        return "NaN"

    def solucionar(self, bottom_up=True):
        if bottom_up:
            retorno = self._dp_bottomup_pandas()
        else:
            # Cria um array bi-dimensional para Memoização, cada elemento inicializado com o valor "-1"
            # dp = [[-1 for x in range(self.valor_disponivel + 1)] for y in range(len(self.itens))]
            dp = pd.DataFrame(np.repeat(-1, len(self.itens)), index=[i for i in range(len(self.itens))],
                              columns=[f"{self.valor_disponivel:0.2f}"])
            retorno = self._dp_topdown_pandas(dp, self.itens.importancia.tolist(), self.itens.valor.tolist(),
                                              self.valor_disponivel)
            # self._get_elementos_selecionados(dp, self.itens.importancia.tolist(), self.itens.valor.tolist(), self.valor_disponivel)
        return retorno


class BranchAndBoundKnapsack:
    """
    Classe que implementa a solução de um Problema de Mochila Binária (0-1 Knapsack Problem) utilizando algoritmo
    Branch and Bound.
    """

    def __init__(self, valor_disponivel, itens):
        self.valor_disponivel = valor_disponivel
        # Pressupõe a ordenação decrescente da razão importância/valor
        # self.itens = itens.sort_values(by="importancia_por_valor", ascending=False)
        self.itens = itens

    def __str__(self):
        return "Branch and Bound"

    class PriorityQueue:
        def __init__(self):
            self.pqueue = []
            self.tamanho = 0

        def enqueue(self, node):
            # Caso seja informado algum nó e o peso dos itens que o compõem esteja acima da capacidade máxima,
            # o nó não será adicionado na fila de prioridade (poda por inviabilidade)
            if node is not None and not node.valor_acima_do_disponivel:
                i = 0
                # Ordenação em ordem crescente da fila de acordo com limitante dual
                while i < len(self.pqueue):
                    if self.pqueue[i].limitante_dual > node.limitante_dual:
                        break
                    i += 1
                self.pqueue.insert(i, node)
                self.tamanho += 1

        def dequeue(self):
            try:
                # Será retornado o último nó que correponde àquele com maior limitante dual encontrado
                node = self.pqueue.pop()
                self.tamanho -= 1
            except:
                print("Não foi possível remover node da fila: fila de prioridade vazia.")
            else:
                return node

    class Node:
        def __init__(self, valor_disponivel, itens):
            self.valor_disponivel = valor_disponivel
            self.itens = itens
            self.indice_fracionado = -1
            self.caminho = {}
            self._limitante_dual = -1
            self._importancia = 0
            self._valor = 0
            self._itens_selecionados = []

        @property
        def limitante_dual(self):
            """
            Função objetivo da solução representada pelo nó.
            """
            if self._limitante_dual == -1:
                self._limitante_dual = 0
                valor_disponivel_restante = self.valor_disponivel
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
                    if item.valor <= valor_disponivel_restante or item.obrigatorio:
                        valor_disponivel_restante -= item.valor
                        self._importancia += item.importancia
                        self._valor += item.valor
                        self._itens_selecionados.append(indice)
                    # Se não pudar o item inteiro, adiciona a fração do peso
                    else:
                        if valor_disponivel_restante > 0:
                            # Marcação de qual o índice do item fracionário para ramificação dos filhos
                            self.indice_fracionado = indice
                            self._limitante_dual = valor_disponivel_restante * item.importancia_por_valor
                        break

                self._limitante_dual += self._importancia
            return self._limitante_dual

        @property
        def importancia(self):
            _ = self.limitante_dual

            return self._importancia

        @property
        def valor(self):
            _ = self.limitante_dual

            return self._valor

        @property
        def itens_selecionados(self):
            _ = self.limitante_dual

            return self._itens_selecionados

        @property
        def valor_acima_do_disponivel(self):
            return self.valor > self.valor_disponivel

        def ramificar(self):
            # Se existir índice de item com valor fracionado
            if self.indice_fracionado >= 0:
                # definindo ramo xi <= 0
                filho1 = BranchAndBoundKnapsack.Node(self.valor_disponivel, self.itens)
                filho1.caminho[self.indice_fracionado] = 0  # xi <= 0
                filho1.caminho.update(self.caminho)

                # definindo ramo xi >= 1
                filho2 = BranchAndBoundKnapsack.Node(self.valor_disponivel, self.itens)
                filho2.caminho[self.indice_fracionado] = 1  # xi >= 1
                filho2.caminho.update(self.caminho)

                return filho1, filho2

            return None, None

    def _get_solucao(self, itens_selecionados=[]):
        solucao = np.repeat(0, len(self.itens))

        if len(itens_selecionados) > 0:
            for indice in itens_selecionados:
                solucao[indice] = 1

        return solucao

    def solucionar(self):
        pq = self.PriorityQueue()

        node = self.Node(self.valor_disponivel, self.itens)
        limitante_primal = 0  # Solução ótima encontrada. Neste caso, começa com zero.
        itens_selecionados = []
        if node.limitante_dual > 0:
            pq.enqueue(node)

            while pq.tamanho != 0:
                node = pq.dequeue()  # remove node with best limitante_dual

                # Antes de ramificar, verifica se existe elemento com limitante dual composto por valor fracionado.
                # Se existir e ele for maior que o limitante primal (solução ótima já encontrada), o nó é descartado
                # (poda por limitante)
                if node.indice_fracionado > -1 and node.limitante_dual > limitante_primal:
                    filho1, filho2 = node.ramificar()

                    pq.enqueue(filho1)
                    pq.enqueue(filho2)
                elif node.importancia > limitante_primal:
                    limitante_primal = node.importancia
                    itens_selecionados = node.itens_selecionados

        solucao = self._get_solucao(itens_selecionados)
        self.itens["proporcao"] = pd.Series(solucao)

        return self.itens


if __name__ == "__main__":
    from datetime import datetime

    # dados = {"importancia": [60, 100, 120, 50],
    #          "valor": [10., 20., 30., 50.]}
    # valor_disponivel = 50.

    # dados = {"importancia": [10, 21, 50, 51],
    #          "valor": [2., 3., 5., 6.]}
    # valor_disponivel = 7.

    dados = {"importancia": [360, 83, 59, 130, 431, 67, 230, 52, 93, 125, 670, 892, 600, 38, 48, 147,
                             78, 256, 63, 17, 120, 164, 432, 35, 92, 110, 22, 42, 50, 323, 514, 28,
                             87, 73, 78, 15, 26, 78, 210, 36, 85, 189, 274, 43, 33, 10, 19, 389, 276,
                             312],
             "valor": [7, 0, 30, 22, 80, 94, 11, 81, 70, 64, 59, 18, 0, 36, 3, 8, 15, 42, 9, 0,
                       42, 47, 52, 32, 26, 48, 55, 6, 29, 84, 2, 4, 18, 56, 7, 29, 93, 44, 71,
                       3, 86, 66, 31, 65, 0, 79, 20, 65, 52, 13]}
    valor_disponivel = 850

itens = pd.DataFrame(dados)

# valor_disponivel = 6200000.
# itens = pd.read_excel("proposicoes_STI_2023.xlsx", sheet_name="Tratado")
# itens = itens.filter(["Ação", "GUT", "Unidade Total"]).rename(columns={"Ação": "acao", "GUT": "importancia",
#"Unidade Total": "valor"})

itens["importancia_por_valor"] = itens.importancia / itens.valor
itens["proporcao"] = 0

inicio_processamento = datetime.now()
print("Início do processamento:", inicio_processamento)

# knapsack = BruteForceKnapsack(valor_disponivel, itens)
# knapsack.solucionar()
# knapsack = DynamicProgrammingKnapsack(valor_disponivel, itens)
# print(knapsack.solucionar(bottom_up=False))
knapsack = BranchAndBoundKnapsack(valor_disponivel, itens)
itens1 = knapsack.solucionar()

fim_processamento = datetime.now()
print("Fim do processamento:", fim_processamento)
print("Tempo de processamento:", fim_processamento - inicio_processamento, end="\n\n")

print("Algoritmo utilizado:", knapsack)
print(f"Importância máxima obtida: {itens1.query('proporcao == 1').importancia.sum()}")
print(f"Valor máximo obtido: {itens1.query('proporcao == 1').valor.sum()}", end="\n\n")

print("Itens escolhidos:")
print(itens1.query("proporcao == 1"), end="\n\n")
print("Itens rejeitados:")
print(itens1.query("proporcao == 0"))

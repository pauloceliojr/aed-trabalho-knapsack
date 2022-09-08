"""Classes base para os algoritmos aproximados."""

import numpy as np
import pandas as pd

class GreedyKnapsack:

    def __init__(self, valor_disponivel, itens, fracional=False):
        self.valor_disponivel = valor_disponivel  # Equivalente à capacidade total da mochila
        self.itens = itens.sort_values(by="importancia_por_valor", ascending=False)  # Itens com possibilidade de escolha
        self.fracional = fracional  # Indica se o método guloso admite fracionamento para escolher os itens

    def __str__(self):
        return "Algoritmo Guloso"

    def solucionar(self):
        # importancia_maxima = 0
        # valor_maximo = 0
        valor_disponivel_restante = self.valor_disponivel

        # Looping through all Items
        for indice, item in self.itens.iterrows():
            # If adding Item won't overflow, add it completely
            if item.valor <= valor_disponivel_restante:
                valor_disponivel_restante -= item.valor
                # importancia_maxima += item.importancia
                # valor_maximo += item.valor
                self.itens.at[indice, "proporcao"] = 1

            else:
                if self.fracional:
                    # importancia_maxima += valor_disponivel_restante * item.importancia_por_valor #multiplica a capacidade restante pelo razão valor/peso para encontrar o valor proporcional e somar ao valor máximo já encontrado
                    # valor_maximo += item.valor * (valor_disponivel_restante / item.valor)
                    self.itens.at[indice, "proporcao"] = valor_disponivel_restante / item.valor
                    break

        # Returning final value
        # return importancia_maxima, valor_maximo, self.itens
        return self.itens


class TabuSearchKnapsack:
    def __init__(self, valor_disponivel, itens):
        self.valor_disponivel = valor_disponivel
        self.itens = itens

    def __str__(self):
        return "Busca Tabu"

    def _get_solucao(self, itens_selecionados=[]):
        solucao = np.repeat(0, len(self.itens))

        if len(itens_selecionados) > 0:
            for indice in itens_selecionados:
                solucao[round(indice)] = 1

        return solucao

    def _fitness(self, solucao):
        """
        Função objetivo de determinada solução.

        :params: solucao : list
        :params: item : list

        :returns:
        importancia_maxima : int
        """
        importancia_maxima = 0
        valor_maximo = 0
        for indice, item in self.itens.iterrows():
            if solucao[indice] == 1 and self.valor_disponivel - valor_maximo >= 0:
                importancia_maxima += item.importancia
                valor_maximo += item.valor

        if self.valor_disponivel - valor_maximo < 0:
            importancia_maxima = -1

        return importancia_maxima

    def _busca_tabu(self, solucao_inicial, iteracoes_sem_melhora=10):
        # Inicialização de variáveis do método
        lista_tabu = []  # Lista que guardará os índices Tabu
        iteracao = 0  # Iteração corrente
        melhor_iteracao = 0  # Iteração onde foi encontrada a melhor solução
        melhor_solucao = solucao_inicial.copy()  # Lista contendo a melhor solução a ser incluída na mochila
        solucao_corrente = solucao_inicial.copy()  # Melhor solução dentro de uma iteração

        importancia_maxima = self._fitness(melhor_solucao)
        while iteracao - melhor_iteracao < iteracoes_sem_melhora:
            iteracao += 1
            solucao_parcial = solucao_corrente.copy()
            importancia_iteracao = -1
            indice_tabu = -1
            for indice in range(len(self.itens)):
                if solucao_parcial[indice] == 1:
                    solucao_parcial[indice] = 0
                else:
                    solucao_parcial[indice] = 1

                importancia_parcial = self._fitness(solucao_parcial)
                if importancia_parcial > importancia_iteracao:
                    importancia_iteracao = importancia_parcial
                    if indice not in lista_tabu:
                        solucao_corrente = solucao_parcial.copy()
                        indice_tabu = indice
                        if importancia_parcial > importancia_maxima:
                            melhor_solucao = solucao_corrente.copy()
                            melhor_iteracao = iteracao
                            importancia_maxima = self._fitness(melhor_solucao)

                if solucao_parcial[indice] == 1:
                    solucao_parcial[indice] = 0
                else:
                    solucao_parcial[indice] = 1

            # Adiciona o índice com a melhor solução da iteração à lista Tabu
            if indice_tabu > -1:
                if len(lista_tabu) == 3: # prazo tabu = 3
                    lista_tabu.pop(0)
                lista_tabu.append(indice_tabu)

        self.itens["proporcao"] = pd.Series(melhor_solucao)

        return self.itens

    def solucionar(self):
        greedy_knapsack = GreedyKnapsack(self.valor_disponivel, self.itens)
        itens = greedy_knapsack.solucionar()
        solucao_inicial = self._get_solucao(itens.query("proporcao == 1").index.tolist())
        itens = self._busca_tabu(solucao_inicial)
        return itens


if __name__ == "__main__":
    from datetime import datetime

    # dados = {"importancia": [60, 100, 120, 50],
    #          "valor": [10., 20., 30., 50.]}
    # valor_disponivel = 50

    # dados = {"importancia": [10, 21, 50, 51],
    #          "valor": [2., 3., 5., 6.]}
    # valor_disponivel = 7

    # itens = pd.DataFrame(dados)

    valor_disponivel = 6200000
    itens = pd.read_excel("proposicoes_STI_2023.xlsx", sheet_name="Tratado")
    itens = itens.filter(["Ação", "GUT", "Unidade Total"]).rename(columns={"Ação": "acao", "GUT": "importancia",
                                                                           "Unidade Total": "valor"})
    itens["importancia_por_valor"] = itens.importancia / itens.valor
    itens["proporcao"] = 0

    inicio_processamento = datetime.now()
    print("Início do processamento:", inicio_processamento)

    # knapsack = GreedyKnapsack(valor_disponivel, itens)
    knapsack = TabuSearchKnapsack(valor_disponivel, itens)
    itens1 = knapsack.solucionar()
    itens1["importancia_atualizada"] = itens1.importancia * itens1.proporcao
    itens1["valor_atualizado"] = itens1.valor * itens1.proporcao

    fim_processamento = datetime.now()
    print("Fim do processamento:", fim_processamento)
    print("Tempo de processamento:", fim_processamento - inicio_processamento, end="\n\n")

    print("Algoritmo utilizado:", knapsack)
    print(f"Importância máxima obtida: {itens1.query('proporcao > 0').importancia_atualizada.sum()}")
    print(f"Valor máximo obtido: {itens1.query('proporcao > 0').valor_atualizado.sum()}", end="\n\n")

    print("Itens escolhidos:")
    print(itens1.query("proporcao > 0"), end="\n\n")
    print("Itens rejeitados:")
    print(itens1.query("proporcao == 0"))

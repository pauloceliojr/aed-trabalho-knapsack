"""Classes base para os algoritmos aproximados."""

import time
from datetime import datetime

import pandas as pd

from abstract_knapsack import AbstractKnapsackSolver


class GreedyKnapsackSolver(AbstractKnapsackSolver):
    """
    Classe que implementa a solução de um Problema da Mochila Binária (0-1 Knapsack Problem) usando algoritmo guloso,
    uma heurística construtiva.
    """

    # Sobrescrita do método construtor para que haja a ordenação dos itens orçamentários.
    def __init__(self, valor_disponivel, itens):
        """
        Método construtor.

        :param valor_disponivel: Valor do orçamento disponível para distribuição (capacidade da mochila).
        :param itens: Itens que serão avaliados para compor o orçamento.
        """
        super().__init__(valor_disponivel, itens)
        # O algoritmo guloso pressupõe a ordenação decrescente da razão importância/valor.
        self.itens = itens.sort_values(by="importancia_por_valor", ascending=False)

    def __str__(self):
        return "Algoritmo Guloso"

    def solucionar(self, fracional=False) -> pd.DataFrame:
        """
        Implementa o algoritmo que soluciona o Problema da Mochila Binária (0-1 Knapsack Problem).

        :param fracional: Indica se deverá incluir fração para o item, que se somado, seu valor extrapolará o valor
         disponível.
        :return: itens: DataFrame do Pandas contendo os itens marcados ou não para compor o orçamento.
        """
        valor_disponivel_restante = self.valor_disponivel

        # Interação sobre todos os itens orçamentários.
        for indice, item in self.itens.iterrows():
            # Se o valor (peso) do item não ultrapassar o valor disponível restante (capacidade da mochila restante)
            # marca o item como selecionado (proporção = 1).
            if item.valor <= valor_disponivel_restante:
                valor_disponivel_restante -= item.valor
                self.itens.at[indice, "proporcao"] = 1
            else:
                # Se o algoritmo guloso admitir fracionamento, adiciona a proporção do primeiro item cujo valor (peso)
                # ultrapassar o valor disponível (capacidade) do orçamento (mochila).
                if fracional:
                    self.itens.at[indice, "proporcao"] = valor_disponivel_restante / item.valor
                    break

        # Reordena o dataset para a ordem original.
        self.itens.sort_index(inplace=True)

        return self.itens


class TabuSearchKnapsackSolver(AbstractKnapsackSolver):
    """
    Classe que implementa a solução de um Problema da Mochila Binária (0-1 Knapsack Problem) usando algoritmo de Busca
    Tabu, uma metaheurística.
    """

    def __str__(self):
        return "Busca Tabu"

    def _fitness(self, solucao: list) -> int:
        """
        Método que implementa a função objetivo de determinada solução.

        :param solucao: Lista contendo os itens de determinada solução. Os itens escolhidos estão marcados como 1 e os
            não escolhidos como 0.
        :return: O valor da importância máxima obtida pelo somatório das importâncias da solução. Caso o valor da
            solução ultrapasse o valor orçamentário disponível, retorna -1.
        """
        importancia_maxima = 0
        valor_maximo = 0
        # Para cada item, verifica se está marcado como selecionado (igual a 1) e se cabe dentro do limite de valor
        # disponível. Se couber, atualiza a importância máxima e o valor máximo da solução em análise.
        for indice, item in self.itens.iterrows():
            if solucao[indice] == 1 and self.valor_disponivel - valor_maximo >= 0:
                importancia_maxima += item.importancia
                valor_maximo += item.valor

        # Se, ao fim do loop, o valor máximo for maior que o valor disponível, retorna -1 indicando que a solução não
        # é viável e deve ser ignorada.
        if self.valor_disponivel - valor_maximo < 0:
            importancia_maxima = -1

        return importancia_maxima

    def _busca_tabu(self, solucao_inicial: list, timeout: int, prazo_tabu: int, verbose: bool) -> pd.DataFrame:
        """
        Método que implementa o algoritmo de Busca Tabu a partir de uma solução inicial.

        :param solucao_inicial: Solução inicial que se quer melhorar com o algoritmo de Busca Tabu.
        :param timeout: Tempo de processamento que será gasto na busca de solução melhor em relação à inicial.
            Medido em segundos.
        :param prazo_tabu: Tamanho da lista Tabu a ser utilizada na execução do algoritmo de Busca Tabu.
        :param verbose: Indica se deverá imprimir informações sobre as iterações em que as melhores soluções foram
            encontradas. Imprime o número da iteração e o timestamp.
        :return: DataFrame do Pandas contendo os itens marcados ou não para compor o orçamento.
        """
        # Lista que guardará os índices Tabu, aqueles que não poderão figurar em possíveis soluções durante sua
        # permanência na lista.
        lista_tabu = []
        # Iteração corrente.
        iteracao = 0
        # Iteração onde foi encontrada a melhor solução.
        melhor_iteracao = 0
        # Lista contendo a melhor solução de distribuição do orçamento pelos itens.
        melhor_solucao = solucao_inicial.copy()
        # Lista contendo a melhor solução dentro de uma iteração.
        solucao_corrente = solucao_inicial.copy()
        # Importância máxima obtida da melhor solução até o momento.
        importancia_maxima = self._fitness(melhor_solucao)
        tempo_inicio = time.time()
        # Executa a busca enquanto o delta desde início for menor que o tempo configurado para o timeout.
        while time.time() - tempo_inicio < timeout:
            # A iteração acaba após serem testadas todas as soluções com índices invertidos das soluções parciais.
            iteracao += 1
            # Inicia a lista da solução parcial com a melhor solução corrente.
            solucao_parcial = solucao_corrente.copy()
            importancia_iteracao = -1
            indice_tabu = -1
            for indice in range(len(self.itens)):
                # A solução parcial é a solução a ser testada e terá seus índices percorridos e invertidos (se era 1
                # vira 0 e vice-versa).
                if solucao_parcial[indice] == 1:
                    solucao_parcial[indice] = 0
                else:
                    solucao_parcial[indice] = 1

                # Calcula-se o valor da importância máxima obtida da solução parcial.
                importancia_parcial = self._fitness(solucao_parcial)

                # Se a importância da solução parcial for maior do que a maior importância obtida na iteração e
                # se o índice trocado na solução parcial não estiver na lista Tabu, atualiza a solução corrente com a
                # solução parcial e marca o índice trocado para inserção na lista Tabu.
                if importancia_parcial > importancia_iteracao:
                    importancia_iteracao = importancia_parcial
                    if indice not in lista_tabu:
                        solucao_corrente = solucao_parcial.copy()
                        indice_tabu = indice
                        # Se a importância da solução parcial for maior do que a melhor importância obtida até o
                        # momento, adota e solução parcial como nova melhor solução e calcula a nova importância máxima.
                        if importancia_parcial > importancia_maxima:
                            melhor_solucao = solucao_parcial.copy()
                            melhor_iteracao = iteracao
                            if verbose:
                                print("Melhor iteração:", melhor_iteracao)
                                print("Data/Hora:", datetime.now())
                            importancia_maxima = importancia_parcial

                # Inverte a solução parcial ao estado anterior para análise do índice seguinte.
                if solucao_parcial[indice] == 1:
                    solucao_parcial[indice] = 0
                else:
                    solucao_parcial[indice] = 1

            # Adiciona o índice com a melhor solução da iteração à lista Tabu.
            if indice_tabu > -1:
                # O prazo Tabu (Tabu tenure) está ajustado para o valor passado pelo parâmetro prazo_tabu. Após o
                # tamanho máximo da lista Tabu, definido pelo prazo Tabu, ser atingido, o índice mais antigo
                # (primeira posição) é retirado da lista.
                if len(lista_tabu) == prazo_tabu:
                    lista_tabu.pop(0)
                # Insere o índice que compôs a melhor solução corrente na lista Tabu.
                lista_tabu.append(indice_tabu)

        # Atualiza o dataframe de itens para indicar os itens que foram selecionados (proporção = 1).
        self.itens["proporcao"] = pd.Series(melhor_solucao)

        return self.itens

    def solucionar(self, timeout: int = 60, prazo_tabu: int = 3, utilizar_solucao_algoritmo_guloso: bool = True,
                   verbose: bool = False) -> pd.DataFrame:
        """
        Implementa o algoritmo que soluciona o Problema da Mochila Binária (0-1 Knapsack Problem).

        :param timeout: Tempo de execução total do algoritmo em segundos. Padrão de 60 segundos.
        :param prazo_tabu: Tamanho da lista Tabu a ser utilizada na execução do algoritmo de Busca Tabu.
        :param utilizar_solucao_algoritmo_guloso: Indica se o algoritmo de Busca Tabu deverá utilizar a solução
            encontrada com a execução prévia do algoritmo guloso.
        :param verbose: Indica se deverá imprimir informações sobre as iterações em que as melhores soluções foram
            encotradas. Imprime o número da iteração e o timestamp.
        :return: DataFrame do Pandas contendo os itens marcados ou não para compor o orçamento.
        """
        if utilizar_solucao_algoritmo_guloso:
            greedy_knapsack = GreedyKnapsackSolver(self.valor_disponivel, self.itens)
            self.itens = greedy_knapsack.solucionar()

        solucao_inicial = self.itens.proporcao.tolist()
        self.itens = self._busca_tabu(solucao_inicial, timeout, prazo_tabu, verbose)

        return self.itens

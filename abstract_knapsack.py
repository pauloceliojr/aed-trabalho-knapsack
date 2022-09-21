from abc import ABCMeta, abstractmethod

import pandas as pd


class AbstractKnapsackSolver(metaclass=ABCMeta):
    """
    Classe abstrata que descreve um algoritmo *solver* para o Problema da Mochila Binária (0-1 Knapsack Problem).
    """

    def __init__(self, valor_disponivel: float, itens: pd.DataFrame):
        """
        Método construtor.

        :param valor_disponivel: Valor do orçamento disponível para distribuição (capacidade da mochila).
        :param itens: Itens que serão avaliados para compor o orçamento.
        """
        self.valor_disponivel = valor_disponivel
        self.itens = itens.copy()

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def solucionar(self) -> pd.DataFrame:
        """
        Implementa o algoritmo que soluciona o Problema da Mochila Binária (0-1 Knapsack Problem).

        :return: DataFrame do Pandas contendo os itens marcados ou não para compor o orçamento.
        """
        pass

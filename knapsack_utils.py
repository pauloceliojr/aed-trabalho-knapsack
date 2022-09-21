import pandas as pd

from algoritmos_aproximados import GreedyKnapsackSolver, TabuSearchKnapsackSolver
from algoritmos_exatos import DynamicProgrammingKnapsackSolver, BranchAndBoundKnapsackSolver


class KnapsackSolverFactory:
    """
    Classe que implementa uma *factory* (*design pattern Factory Method*) para obtenção de *solvers* do Problema da
    Mochila Binária (0-1 Knapsack Problem).
    """

    DYNAMIC_PROGRAMMING_KNAPSACK_SOLVER = 0
    """
    Abordagem baseada no algoritmo de Programação Dinâmica. O tempo de execução do *solver* varia quanto maior for o 
    tamanho do dataset.
    """
    BRANCH_AND_BOUND_KNAPSACK_SOLVER = 1
    """
    Abordagem baseada no algoritmo Branch and Bound. Este *solver* pode lidar com número grande of itens.
    """
    GREEDY_KNAPSACK_SOLVER = 2
    """
    Abordagem baseada na heurística construtiva gulosa.
    """
    TABU_SEARCH_KNAPSACK_SOLVER = 3
    """
    Abordagem baseada na metaheurística de Busca Tabu.
    """

    @staticmethod
    def get_solver(tipo: int, valor_disponivel: float, itens: pd.DataFrame):
        """
        Método estático de criação de *knapsack solvers*.

        :param tipo: Tipo de _solver_ que se deseja criar.
        :param valor_disponivel: Valor do orçamento disponível para distribuição (capacidade da mochila).
        :param itens: Itens que serão avaliados para compor o orçamento.
        :return: Instância do tipo de solver selecionado.
        :raises AssertionError: Se for passado um tipo não existente de solver, dispara um AssertionError.
        """
        if tipo == KnapsackSolverFactory.DYNAMIC_PROGRAMMING_KNAPSACK_SOLVER:
            return DynamicProgrammingKnapsackSolver(valor_disponivel, itens)
        elif tipo == KnapsackSolverFactory.BRANCH_AND_BOUND_KNAPSACK_SOLVER:
            return BranchAndBoundKnapsackSolver(valor_disponivel, itens)
        elif tipo == KnapsackSolverFactory.GREEDY_KNAPSACK_SOLVER:
            return GreedyKnapsackSolver(valor_disponivel, itens)
        elif tipo == KnapsackSolverFactory.TABU_SEARCH_KNAPSACK_SOLVER:
            return TabuSearchKnapsackSolver(valor_disponivel, itens)
        raise AssertionError("Tipo de Knapsack Solver inválido.")

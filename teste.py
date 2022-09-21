"""Classes base para os algoritmos aproximados."""

from datetime import datetime

import pandas as pd

from knapsack_utils import KnapsackSolverFactory

if __name__ == "__main__":
    # dados = {"importancia": [60, 100, 120, 50],
    #          "valor": [10., 20., 30., 50.]}
    # valor_disponivel = 50

    # dados = {"importancia": [10, 21, 50, 51],
    #          "valor": [2., 3., 5., 6.]}
    # valor_disponivel = 7

    # dados = {"importancia": [360, 83, 59, 130, 431, 67, 230, 52, 93, 125, 670, 892, 600, 38, 48, 147,
    #                          78, 256, 63, 17, 120, 164, 432, 35, 92, 110, 22, 42, 50, 323, 514, 28,
    #                          87, 73, 78, 15, 26, 78, 210, 36, 85, 189, 274, 43, 33, 10, 19, 389, 276,
    #                          312],
    #          "valor": [7., 0., 30., 22., 80., 94., 11., 81., 70., 64., 59., 18., 0., 36., 3., 8., 15., 42., 9., 0.,
    #                    42., 47., 52., 32., 26., 48., 55., 6., 29., 84., 2., 4., 18., 56., 7., 29., 93., 44., 71.,
    #                    3., 86., 66., 31., 65., 0., 79., 20., 65., 52., 13.]}
    # valor_disponivel = 850.
    #
    # itens = pd.DataFrame(dados)

    valor_disponivel = 6200000
    itens = pd.read_excel("proposicoes_STI_2023.xlsx", sheet_name="Tratado")
    itens = itens.filter(["Ação", "GUT", "Unidade Total"]).rename(
        columns={"Ação": "acao", "GUT": "importancia", "Unidade Total": "valor"})

    itens["importancia_por_valor"] = itens.importancia / itens.valor
    itens["proporcao"] = 0

    inicio_processamento = datetime.now()
    print("Início do processamento:", inicio_processamento)

    # knapsack = KnapsackSolverFactory.get_solver(KnapsackSolverFactory.GREEDY_KNAPSACK_SOLVER, valor_disponivel, itens)
    # itens1 = knapsack.solucionar()

    knapsack = KnapsackSolverFactory.get_solver(KnapsackSolverFactory.TABU_SEARCH_KNAPSACK_SOLVER, valor_disponivel, itens)
    itens1 = knapsack.solucionar(timeout=30, prazo_tabu=7, verbose=True)

    fim_processamento = datetime.now()
    print("Fim do processamento:", fim_processamento)
    print("Tempo de processamento:", fim_processamento - inicio_processamento, end="\n\n")

    print("Algoritmo utilizado:", knapsack)
    print(f"Importância máxima obtida: {itens1.query('proporcao > 0').importancia.sum()}")
    print(f"Valor máximo obtido: {itens1.query('proporcao > 0').valor.sum()}", end="\n\n")

    print("Itens escolhidos:")
    print(itens1.query("proporcao > 0"), end="\n\n")
    print("Itens rejeitados:")
    print(itens1.query("proporcao == 0"))

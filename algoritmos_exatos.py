"""Classes base para os algoritmos exatos."""

import pandas as pd
from ortools.algorithms import pywrapknapsack_solver

from abstract_knapsack import AbstractKnapsackSolver


class DynamicProgrammingKnapsackSolver(AbstractKnapsackSolver):
    """
    Classe que implementa a solução de um Problema da Mochila Binária (0-1 Knapsack Problem) usando algoritmos de Programação
    Dinâmica. Essa classe encapsula o solver da biblioteca OR-Tools do Google (https://developers.google.com/optimization), que,
    para os propósitos do trabalho, apresentou desempenho melhor do que a implementação própria.
    """

    def __str__(self):
        return "Programação Dinâmica"

    def solucionar(self):
        # Cria uma cópia dos itens orçamentários para manipulação interna do método.
        itens = self.itens.copy()

        # Cria o solver com o parâmetro para programação dinâmica.
        or_tools_solver = pywrapknapsack_solver.KnapsackSolver(
            pywrapknapsack_solver.KnapsackSolver.
            KNAPSACK_DYNAMIC_PROGRAMMING_SOLVER, 'KnapsackExample')

        # Para que solver do OR-Tools funcione, é necessário que sejam passados valores sem casas decimais.
        # Assim sendo, para incorporar os centavos aos cálculos, multiplicou-se o valor por 100.
        itens["valor_multiplicado"] = itens.valor * 100

        # Variáveis com os parametros aceitos pelo solver do OR-Tools
        importancias = itens.importancia.tolist()  # Equivalente ao valor no problema da mochila.
        valores = [itens.valor_multiplicado.tolist()]  # Equivalente ao peso no problema da mochila.

        # O solver do OR-Tools implementa solução para o problema das mochilas múltiplas.
        # Desta maneira, faz-se necessário passar uma lista de capacidades de mochilas que, para o estudo de caso,
        # é apenas uma (valor de orçamento disponível para distribuição).
        # Da mesma forma que os valores individuais foram multiplicados por 100, o valor disponível (capacidade) também
        # precisa ser.
        valores_disponiveis = [int(self.valor_disponivel * 100)]

        # Inicia o solver com os parâmetros do problema e o executa. O método Solve retorna a solução ótima que não será
        # utilizada aqui dado que serão retornados os itens selecionados e suas importâncias e valores somados pelo
        # chamador do método.
        or_tools_solver.Init(importancias, valores, valores_disponiveis)
        or_tools_solver.Solve()

        # Verifica quais os índices selecionados e marca no dataset de retorno.
        for i in range(len(importancias)):
            if or_tools_solver.BestSolutionContains(i):
                self.itens.at[i, "proporcao"] = 1

        return self.itens


class BranchAndBoundKnapsackSolver(AbstractKnapsackSolver):
    """
    Classe que implementa a solução de um Problema da Mochila Binária (0-1 Knapsack Problem) utilizando algoritmo
    Branch and Bound.
    """

    # Sobrescrita do método construtor para que haja a ordenação dos itens orçamentários.
    def __init__(self, valor_disponivel, itens):
        """
        Método construtor.

        :param valor_disponivel: Valor do orçamento disponível para distribuição (capacidade da mochila).
        :param itens: Itens que serão avaliados para compor o orçamento.
        """
        super().__init__(valor_disponivel, itens)
        # O algoritmo Branch and Bound pressupõe a ordenação decrescente da razão importância/valor.
        self.itens = itens.sort_values(by="importancia_por_valor", ascending=False)

    def __str__(self):
        return "Branch and Bound"

    class PriorityQueue:
        """
        A classe interna PriorityQueue implementa uma fila onde os nós ativos da busca são enfileirados em ordem crescente.
        O nó retornado será sempre o que pussui o maior limitante dual.
        """

        def __init__(self):
            self.pqueue = []
            self.tamanho = 0

        def enqueue(self, node):
            """
            Insere na fila um nó de forma ordenada.

            :param node: Nó ativo a ser enfileirado.
            """
            # Caso seja informado algum nó e o valor dos itens que o compõem esteja acima do valor disponível,
            # o nó não será adicionado na fila de prioridade (poda por inviabilidade).
            if node is not None and not node.is_valor_acima_do_disponivel:
                i = 0
                # Ordenação em ordem crescente da fila de acordo com limitante dual.
                while i < len(self.pqueue):
                    if self.pqueue[i].limitante_dual > node.limitante_dual:
                        break
                    i += 1
                # Insere na nó na fila e incrementa o contador de tamanho.
                self.pqueue.insert(i, node)
                self.tamanho += 1

        def dequeue(self):
            """
            Retira da fila o nó que estiver na última posição (com maior limitante dual).

            :return: Nó retirado da fila.
            """
            try:
                # Será retornado o último nó que correponde àquele com maior limitante dual encontrado.
                node = self.pqueue.pop()
                self.tamanho -= 1
            except:
                print("Não foi possível remover node da fila: fila de prioridade vazia.")
            else:
                return node

    class Node:
        """
        A classe interna Node implementa a estrutura de dados que armazenará os nós da árvore utilizada pelo algoritmo
        Branch and Bound.
        """

        def __init__(self, valor_disponivel: float, itens: pd.DataFrame):
            """
            Método construtor.

            :param valor_disponivel: Valor do orçamento disponível para distribuição (capacidade da mochila).
            :param itens: Itens que serão avaliados para compor o orçamento.
            """
            self.valor_disponivel = valor_disponivel
            """
            Valor do orçamento disponível para distribuição (capacidade da mochila).
            """
            self.itens = itens
            """
            Itens que serão avaliados para compor o orçamento.
            """
            self.indice_fracionado = -1
            """
            Índice do elemento fracionado usado para se obter o valor fracionado do presente nó.Dicionário contendo o caminho de índices dos itens usados para ramificação até o presente nó, no
            formato: {x: 0 ou 1, ..., y: 0 ou 1}, onde x = índice inicial, y = índice final.
            """
            self.caminho = {}
            """
            Dicionário contendo o caminho de índices dos itens usados para ramificação até o presente nó, no
            formato: {x: 0 ou 1, ..., y: 0 ou 1}, onde x = índice inicial, y = índice final.
            """
            self._limitante_dual = -1
            self._importancia = 0
            self._valor = 0
            self._itens_selecionados = []

        @property
        def limitante_dual(self) -> float:
            """
            Atributo da classe interna Node que implementa a função objetivo da solução representada pelo nó. O
            limitante dual representa o valor máximo de todos os itens que compõe o nó, incluindo o item fracionado que
            não coube inteiramente na solução.
            """
            # Se o limitante dual for igual -1, indica que se trata de um nó novo e executa a função objetivo para se
            # obter o limitante dual e demais atributos do nó.
            if self._limitante_dual == -1:
                self._limitante_dual = 0
                valor_disponivel_restante = self.valor_disponivel
                # Cria cópia dos itens orçamentários para utilização dentro do método. Em cima da cópia, cria um campo
                # chamado "obrigatorio" que indicará se o índice deverá compor ou não o cálculo do limitante dual.
                itens = self.itens.copy()
                itens["obrigatorio"] = 0

                # Bloco que seleciona, a partir do caminho de índices que foi usado até chegar no nó corrente, quais
                # itens serão obrigatoriamente excluídos da solução e quais serão mantidos.
                # Se o índice dentro do caminho estiver marcado como 1, deve ser incluído, caso contrário (0), excluído.
                if len(self.caminho) > 0:
                    # Cria lista de índices a serem mantidos.
                    indices_mantidos = itens.index.values.tolist()
                    # Cria lista de índices a serem excluídos.
                    indices_excluidos = []
                    for chave, valor in self.caminho.items():
                        if valor <= 0:
                            indices_excluidos.append(chave)
                        elif valor >= 1:
                            itens.at[chave, "obrigatorio"] = 1
                            # Reordena a lista de índices mantidos retirando o item corrente de sua posição atual e o
                            # incluíndo na primeira posição da lista (índice 0).
                            indices_mantidos.insert(0, indices_mantidos.pop(indices_mantidos.index(chave)))
                    # Reindexa os itens do dataset com base na lista de índices mantidos que foram inseridos nas
                    # primeiras posições.
                    itens = itens.reindex(indices_mantidos)
                    # Exclui os índices marcados como não obrigatórios.
                    itens = itens.drop(indices_excluidos)

                # Aqui serão calculados: limitante dual, importância e valor. Também são adicionados os itens
                # selecionados que compõem o cálculo do limitante dual e, caso exista, será armazenado o índice do item
                # que foi fracionado para compor o valor do limitante dual.
                for indice, item in itens.iterrows():
                    # Adiciona os itens até estourar o valor disponível restante. Caso o item seja obrigatorio,
                    if item.valor <= valor_disponivel_restante or item.obrigatorio:
                        valor_disponivel_restante -= item.valor
                        self._importancia += item.importancia
                        self._valor += item.valor
                        self._itens_selecionados.append(indice)
                    # Se não couber o item inteiro, adiciona a fração do valor.
                    else:
                        if valor_disponivel_restante > 0:
                            # Marcação de qual o índice do item fracionário para ramificação das folhas deste nó.
                            self.indice_fracionado = indice
                            self._limitante_dual = valor_disponivel_restante * item.importancia_por_valor
                        break

                # Atualiza o valor do limitante com o valor existe mais o valor somado das importâncias.
                self._limitante_dual += self._importancia

            return self._limitante_dual

        @property
        def importancia(self) -> int:
            """
            Importância somada da solução contida no nó.
            """
            _ = self.limitante_dual

            return self._importancia

        @property
        def valor(self) -> float:
            """
            Valor somado dos itens da solução contida no nó.
            """
            _ = self.limitante_dual

            return self._valor

        @property
        def itens_selecionados(self) -> list:
            """
            Itens que compõem a solução contida no nó.
            """
            _ = self.limitante_dual

            return self._itens_selecionados

        @property
        def is_valor_acima_do_disponivel(self) -> bool:
            """
            Índica se o valor somado da solução contida no nó é maior do que o valor disponível (capacidade da mochila).
            """
            return self.valor > self.valor_disponivel

        def ramificar(self):
            """
            Ramifica o nó em dois nós folhas caso o limitante dual seja composto por valor fracionado de determinado
            item, correspondente ao índice armazenado no atributo indice_fracionado.

            :return: Nó Folha 1, Nó Folha 2
            """
            # Se, dentre os índices que compõem a solução armazenada pelo nó, existir índice de item cujo valor
            # tenha sido fracionado, ainda não se chegou em uma solução inteira (limitante dual composto apenas por
            # valores que não são frações de um valor inteiro de item) e, portanto, o nó será ramificado em
            # busca de uma solução inteira.
            if self.indice_fracionado > -1:
                # Ramo xi <= 0.
                folha1 = BranchAndBoundKnapsackSolver.Node(self.valor_disponivel, self.itens)
                # Uma das folhas deverá desprezar o item com valor fracionado.
                folha1.caminho[self.indice_fracionado] = 0  # xi <= 0
                # Atualiza os caminho do nó pra incluir o caminho percorrido nos níveis superiores.
                folha1.caminho.update(self.caminho)

                # Ramo xi >= 1
                folha2 = BranchAndBoundKnapsackSolver.Node(self.valor_disponivel, self.itens)
                # A outra folha deverá obrigatoriamente incluir o item com valor fracionado.
                folha2.caminho[self.indice_fracionado] = 1  # xi >= 1
                # Atualiza os caminho do nó pra incluir o caminho percorrido nos níveis superiores.
                folha2.caminho.update(self.caminho)

                return folha1, folha2

            return None, None

    def solucionar(self):
        # Cria a fila de prioridade que armazenará os nós ativos.
        pq = self.PriorityQueue()

        # Cria o nó raiz que será ramificado até se encontrar a solução ótima.
        node = self.Node(self.valor_disponivel, self.itens)

        # Solução ótima encontrada. Neste caso, começa com zero, dado que, até o momento, a solução inicial é a melhor
        # solução.
        limitante_primal = 0

        itens_selecionados = []
        if node.limitante_dual > 0:
            # Enfileira o nó raiz.
            pq.enqueue(node)

            while pq.tamanho != 0:
                # Remove o nó ativo com o melhor limitante dual.
                node = pq.dequeue()

                # Antes de ramificar, verifica se existe elemento com limitante dual composto por valor fracionado.
                # Se existir e o limitante dual for maior que o limitante primal, continua a ramificação da árvore, caso
                # contrário, despreza o nó ativo dado que solução melhor já existe (poda por limitante).
                if node.indice_fracionado > -1 and node.limitante_dual > limitante_primal:
                    # Ramifica o nó corrente. Caso o valor do nó corrente
                    folha1, folha2 = node.ramificar()

                    # Enfileira os nós folhas.
                    pq.enqueue(folha1)
                    pq.enqueue(folha2)
                # Se o valor for inteiro (índice_fracionado == -1) e se sua importância for maior que o limitante
                # primal, indica que uma melhor solução foi encontrada e atualiza o limitante primal e a lista de itens
                # selecionados.
                elif node.importancia > limitante_primal:
                    limitante_primal = node.importancia
                    itens_selecionados = node.itens_selecionados

        # Atualiza o dataframe de itens para indicar os itens que foram selecionados (proporção = 1).
        self.itens.loc[itens_selecionados, "proporcao"] = 1

        # Reordena o dataset para a ordem original.
        self.itens.sort_index(inplace=True)

        return self.itens

# Trabalho de Algoritmos e Estrutura de Dados

Universidade de Brasília - PPCA<br/>
Algoritmos e Estruturas da Dados

Adriano Nunes Soares - 22/0005249<br/>
Marcos Castro - 22/0005575<br/>
Paulo Célio Soares da Silva Júnior - 22/0005605

Prof. Edison Ishikawa


## Sobre o repositório

Este repositório foi criado para hospedagem do código-fonte do trabalho final da disciplina de Algoritmos e Estruturas de 
Dados do Programa de Pós-Graduação em Computação Aplicada da Universidade de Brasília. Os algoritmos implementados visam
otimizar a alocação de recursos orçamentários, dado que se trata de problema caracterizado como Problema da Mochila Binária.   

## Problema da Mochila Binária (0-1 Knapsack Problem)

<p align="center"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Knapsack.svg/486px-Knapsack.svg.png?20070709074029" alt="Problema da Mochila: Como maximizar o valor com um peso máximo?" width="600" height="500"/></p> 
<h6 align="center">Exemplo de Problema da Mochila.</h6>

A imagem ilustra um exemplo do __Problema da Mochila Binária (0-1 Knapsack Problem)__, assim como o problema descrito e solucionado computacionalmente
neste trabalho.

## Arquivos do repositório:

### abstract_knapsack.py

Arquivo que contém a classe abstrata que descreve um algoritmo *solver* para o __Problema da Mochila Binária__.
[Clique aqui](abstract_knapsack.py) para visualizar a implementação.

### algoritmos_aproximados.py

Classes base para os algoritmos aproximados. Os algoritmos implementados foram o Algoritmo Guloso e Busca Tabu.
[Clique aqui](algoritmos_aproximados.py) para visualizar a implementação.

### algoritmos_exatos.py

Classes base para os algoritmos exatos. Os algoritmos implementados foram de Programação Dinâmica e Branch and Bound.
[Clique aqui](algoritmos_exatos.py) para visualizar a implementação.

### Knapsack.ipynb

*Notebook* do Jupyter com a demostração da resolução do problema a partir do dataset com os itens orçamentários, utilizando
as implementações dos algoritmos em Python.
[Clique aqui](Knapsack.ipynb) para visualizar a implementação.

### knapsack_utils.py

Contém a classe que implementa uma *factory* (*design pattern Factory Method*) para obtenção de *solvers* do Problema da Mochila Binária.
[Clique aqui](knapsack_utils.py) para visualizar a implementação.

### proposicoes_STI_2023.xlsx

Arquivo Excel contendo os itens orçamentários a serem distribuídos dentro do limite orçamentário disponível para o exercício
de 2023.
[Clique aqui](proposicoes_STI_2023.xlsx) para visualizar a implementação.


## Pré-requisitos

Para rodar o código é necessário Python 3, Pandas e Google OR-Tools. Caso seja utilizado o Jupyter Notebook, também é necessário o Seaborn.

### Uso

Todas as implementações podem ser chamadas diretamente, mas se recomenda a execução do *notebook* do Jupyter que já encapsula
as chamadas, resultados e análises feitas.

Caso a opção seja a de rodar o código diretamente, recomenda-se sua chamada através da *factory*:

```
  # exemplo utilizando o algoritmo de Programação Dinâmica
  
  from knapsack_utils import KnapsackSolverFactory
  
  valor_disponivel = float(6200000)
  itens = pd.read_excel("proposicoes_STI_2023.xlsx", sheet_name="Tratado")
  itens = itens.filter(["Ação", "GUT", "Unidade Total"])
  itens = itens.rename(columns={"Ação": "acao", "GUT": "importancia",
                                "Unidade Total": "valor"})
  itens["importancia_por_valor"] = itens.importancia / itens.valor
  itens["proporcao"] = 0
  
  KnapsackSolverFactory.get_solver(KnapsackSolverFactory.DYNAMIC_PROGRAMMING_KNAPSACK_SOLVER, valor_disponivel, itens)
  
  itens_retornados = knapsack_solver.solucionar()
```

## Resultados

Os resultados constam documentados no *notebook* do Jupyter.
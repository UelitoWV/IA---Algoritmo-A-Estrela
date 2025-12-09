# Problema das N-Rainhas (Solução com CSP + Forward Checking)

Este projeto implementa uma solução para o clássico **Problema das N-Rainhas** (N-Queens) utilizando técnicas de **CSP (Constraint Satisfaction Problem)** com **Forward Checking** e múltiplas heurísticas de otimização. O projeto também gera visualizações gráficas da árvore de busca e do tabuleiro final.

## Funcionalidades

- **CSP com Forward Checking:** Verifica se as escolhas atuais eliminam completamente as opções de variáveis futuras, cortando ramos inválidos precocemente.
- **Heurística VRM (Valores Restantes Mínimos):** Seleciona a linha com menos valores disponíveis ("fail-first").
- **Heurística de Grau:** Prioriza linhas que mais restringem outras variáveis.
- **Heurística VMR (Valor Menos Restritivo):** Ordena os valores para tentar primeiro aqueles que deixam mais opções para o futuro.
- **Visualização com NetworkX:** Plota a árvore de decisão completa criada durante a busca, destacando o caminho da solução.
- **Visualização com Matplotlib:** Desenha o tabuleiro de xadrez com a solução encontrada.
- **Comparação de Heurísticas:** Função para comparar diferentes combinações de heurísticas e avaliar desempenho.

## Heurísticas Implementadas

### VRM - Valores Restantes Mínimos
Escolhe a variável (linha) com **menos valores disponíveis** no domínio. Esta é uma estratégia "fail-first" que detecta falhas mais cedo na busca.

### Grau
Escolhe a variável que **mais restringe** outras variáveis não atribuídas. No N-Rainhas, linhas mais próximas do topo restringem mais linhas futuras.

### VMR - Valor Menos Restritivo
Ordena os valores (colunas) da **menos restritiva para a mais restritiva**, tentando primeiro valores que deixam mais opções disponíveis para variáveis futuras.

### Forward Checking
Após cada atribuição, verifica se alguma variável futura ficou sem valores válidos. Se sim, realiza backtrack imediatamente sem explorar esse ramo.

## Pré-requisitos

Para executar este projeto, você precisará ter instalado:

- **Python 3.x**

As bibliotecas externas necessárias estão no `requirements.txt`:
- matplotlib
- networkx
- numpy

## Instalação e Execução

Siga os passos abaixo para configurar o ambiente virtual e rodar o projeto.

### 1. Clone ou baixe o projeto

Crie uma pasta para o projeto e coloque o arquivo do código (`main.py`) dentro dela.

### 2. Crie um Ambiente Virtual (venv)

O uso de `venv` isola as dependências do projeto. Abra o terminal na pasta do projeto e execute:

**Windows:**
```bash
python -m venv venv
```

**Linux/Mac:**
```bash
python3 -m venv venv
```

### 3. Ative o ambiente virtual

**Windows (CMD):**
```bash
venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instale as dependências

Após ativar o ambiente virtual, instale todas as dependências do projeto:

```bash
pip install -r requirements.txt
```

### 5. Execute o projeto

Após tudo estar devidamente instalado, inicialize o `main.py` para observar o algoritmo rodando:

```bash
python main.py
```

## Exemplos de Uso

### Exemplo 1: Resolver N=8 com todas as heurísticas

```python
solver = NQueensCSP(8, use_vrm=True, use_grau=True, use_vmr=True)
solver.solve()
solver.plot_search_tree()
solver.plot_chessboard()
```

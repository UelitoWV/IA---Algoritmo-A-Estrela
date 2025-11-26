# Problemas da N rainhas (Solução com o algoritmo de Busca A*)

Este projeto implementa uma solução para o clássico **Problema das N-Rainhas** (N-Queens) utilizando o algoritmo de busca **A* (A-Star)**. O projeto também gera visualizações gráficas da árvore de busca e do tabuleiro final.

## Funcionalidades

- **Algoritmo A*:** Busca heurística que tenta minimizar o custo $f(n) = g(n) + h(n)$.
- **Heurística:** Calcula quantas posições nas linhas futuras são "bloqueadas" pela rainha atual, guiando a busca para ramos mais promissores.
- **Visualização com NetworkX:** Plota a árvore de decisão criada durante a busca.
- **Visualização com Matplotlib:** Desenha o tabuleiro de xadrez com a solução encontrada.

## Pré-requisitos

Para executar este projeto, você precisará ter instalado:

- **Python 3.x**

As bibliotecas externas necessárias estão no `requirements.txt`


## 🚀 Instalação e Execução

Siga os passos abaixo para configurar o ambiente virtual e rodar o projeto.

### 1. Clone ou baixe o projeto
Crie uma pasta para o projeto e coloque o arquivo do código (`main.py`) dentro dela.

### 2. Crie um Ambiente Virtual (venv)
O uso de `venv` isola as dependências do projeto. Abra o terminal na pasta do projeto e execute:

**Windows:**
```bash
python -m venv venv
```

### 3. Instale as dependências
Após instalar o Ambiente Virtual, instale todas as dependências do projeto, seguindo os seguintes passos:

**Windows (CMD)**
```bash
# Ative o ambiente virtual
venv\Scripts\activate

# Baixe as dependências
pip install -r requirements.txt
```

### 4. Inicialize o projeto
Após tudo estar devidamente instalado, inicialize o `main.py` para observar o algoritmo rodando:
```bash
pip install -r requirements.txt
```

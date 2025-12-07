import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import time

class NQueensCSP:
    def __init__(self, n, use_mrv=True, use_degree=True, use_lcv=True):
        self.n = n
        self.use_mrv = use_mrv
        self.use_degree = use_degree
        self.use_lcv = use_lcv
        
        # Estatísticas
        self.nodes_explored = 0
        self.backtracks = 0
        self.solution = None
        
        # Visualização
        self.G = nx.DiGraph()
        self.node_labels = {}
        self.exploration_order = {}
        
        # Domínios: assignment[row] = col (ou None se não atribuído)
        self.assignment = {}
        
    def is_safe_assignment(self, assignment, row, col):
        """
        Verifica se é seguro colocar uma rainha em (row, col)
        dado o assignment atual (dicionário row->col)
        """
        for assigned_row, assigned_col in assignment.items():
            # Mesma coluna
            if assigned_col == col:
                return False
            
            # Mesma diagonal
            if abs(assigned_row - row) == abs(assigned_col - col):
                return False
        
        return True
    
    def get_available_columns(self, assignment, row):
        """Retorna colunas disponíveis para uma linha dado o assignment"""
        available = []
        for col in range(self.n):
            if self.is_safe_assignment(assignment, row, col):
                available.append(col)
        return available
    
    def count_conflicts(self, assignment, row, col):
        """
        Conta quantas posições futuras serão bloqueadas se colocarmos
        uma rainha em (row, col). Usado pela heurística LCV.
        """
        conflicts = 0
        temp_assignment = assignment.copy()
        temp_assignment[row] = col
        
        # Para cada linha não atribuída
        for future_row in range(self.n):
            if future_row not in temp_assignment:
                for future_col in range(self.n):
                    if not self.is_safe_assignment(temp_assignment, future_row, future_col):
                        conflicts += 1
        
        return conflicts
    
    def mrv_heuristic(self, assignment, unassigned_rows):
        """
        Heurística MRV (Minimum Remaining Values)
        Retorna a linha com MENOS valores disponíveis.
        "Fail-first" - se vai falhar, falhe cedo.
        """
        min_values = float('inf')
        best_row = None
        
        for row in unassigned_rows:
            available = len(self.get_available_columns(assignment, row))
            if available < min_values:
                min_values = available
                best_row = row
        
        return best_row
    
    def degree_heuristic(self, board, unassigned_rows):
        """
        Heurística de Grau (Degree Heuristic)
        Retorna a linha que MAIS restringe outras linhas.
        No N-Rainhas, quanto mais cedo na sequência, mais restringe.
        """
        # A linha mais próxima do topo restringe mais linhas futuras
        return min(unassigned_rows)
    
    def combined_heuristic(self, assignment, unassigned_rows):
        """
        Combina MRV e Degree:
        1. Usa MRV como principal
        2. Em caso de empate, usa Degree como desempate
        """
        if not self.use_mrv and not self.use_degree:
            return min(unassigned_rows)  # Ordem padrão
        
        if self.use_mrv and not self.use_degree:
            return self.mrv_heuristic(assignment, unassigned_rows)
        
        if not self.use_mrv and self.use_degree:
            return self.degree_heuristic(assignment, unassigned_rows)
        
        # Ambas habilitadas: MRV com desempate por Degree
        min_values = float('inf')
        candidates = []
        
        for row in unassigned_rows:
            available = len(self.get_available_columns(assignment, row))
            if available < min_values:
                min_values = available
                candidates = [row]
            elif available == min_values:
                candidates.append(row)
        
        # Se há empate, usa degree (escolhe a linha mais cedo)
        return min(candidates)
    
    def lcv_order_values(self, assignment, row, available_cols):
        """
        Heurística LCV (Least Constraining Value)
        Ordena as colunas da MENOS restritiva para a MAIS restritiva.
        Prefere valores que deixam mais opções para o futuro.
        """
        if not self.use_lcv:
            return available_cols
        
        # Calcula quantos conflitos cada coluna causa
        col_conflicts = []
        for col in available_cols:
            conflicts = self.count_conflicts(assignment, row, col)
            col_conflicts.append((col, conflicts))
        
        # Ordena por número de conflitos (menor primeiro)
        col_conflicts.sort(key=lambda x: x[1])
        
        return [col for col, _ in col_conflicts]
    
    def solve(self):
        """Resolve usando backtracking com forward checking"""
        print(f"\n{'='*70}")
        print(f"Resolvendo N-Rainhas (N={self.n}) com CSP + Forward Checking")
        print(f"Heurísticas ativas: MRV={self.use_mrv}, Degree={self.use_degree}, LCV={self.use_lcv}")
        print(f"{'='*70}\n")
        
        start_time = time.time()
        
        # Cria nó raiz para visualização
        initial_state = tuple()
        self.G.add_node(initial_state)
        self.node_labels[initial_state] = "Início"
        self.exploration_order[initial_state] = 0
        
        result = self._backtrack({}, set(range(self.n)), initial_state)
        
        end_time = time.time()
        elapsed = (end_time - start_time) * 1000  # em ms
        
        if result:
            self.solution = result
            # Converte dicionário para tupla ordenada
            solution_tuple = tuple(result[i] for i in range(self.n))
            print(f"\n✅ Solução encontrada: {solution_tuple}")
            
            # Valida a solução
            if self._validate_solution(result):
                print("✓ Solução validada - sem conflitos!")
            else:
                print("✗ ERRO: Solução tem conflitos!")
        else:
            print(f"\n❌ Nenhuma solução encontrada")
        
        print(f"\n📊 Estatísticas:")
        print(f"   • Nós explorados: {self.nodes_explored}")
        print(f"   • Backtracks: {self.backtracks}")
        print(f"   • Tempo: {elapsed:.2f}ms")
        print(f"{'='*70}\n")
        
        return result
    
    def _validate_solution(self, assignment):
        """Valida se uma solução não tem conflitos"""
        for r1 in range(self.n):
            for r2 in range(r1 + 1, self.n):
                c1 = assignment[r1]
                c2 = assignment[r2]
                
                # Mesma coluna
                if c1 == c2:
                    print(f"Conflito coluna: Q({r1},{c1}) e Q({r2},{c2})")
                    return False
                
                # Mesma diagonal
                if abs(r1 - r2) == abs(c1 - c2):
                    print(f"Conflito diagonal: Q({r1},{c1}) e Q({r2},{c2})")
                    return False
        
        return True
    
    def _backtrack(self, assignment, unassigned_rows, parent_state):
        """Backtracking recursivo com forward checking"""
        self.nodes_explored += 1
        
        # Caso base: todas as rainhas colocadas
        if len(assignment) == self.n:
            return assignment
        
        # Seleciona próxima linha usando heurística combinada
        row = self.combined_heuristic(assignment, unassigned_rows)
        
        # Obtém colunas disponíveis
        available_cols = self.get_available_columns(assignment, row)
        
        # Forward Checking (Base): Se a variável atual não tem valores, falha
        if not available_cols:
            self.backtracks += 1
            return None
        
        # Ordena colunas usando LCV
        ordered_cols = self.lcv_order_values(assignment, row, available_cols)
        
        # Tenta cada coluna
        for col in ordered_cols:
            # Cria novo assignment
            new_assignment = assignment.copy()
            new_assignment[row] = col
            
            # Cria estado para visualização (tupla ordenada pelas linhas atribuídas)
            state_list = [(r, new_assignment[r]) for r in sorted(new_assignment.keys())]
            new_state = tuple(state_list)
            
            # Adiciona ao grafo de visualização
            self.G.add_edge(parent_state, new_state)
            self.node_labels[new_state] = f"Q{row}:{col}"
            self.exploration_order[new_state] = self.nodes_explored
            
            # --- FORWARD CHECKING ---
            # Verifica se essa escolha "matou" alguma linha futura
            new_unassigned = unassigned_rows - {row}
            forward_check_ok = True
            
            for future_row in new_unassigned:
                # Se uma linha futura ficou sem opções válidas...
                if not self.get_available_columns(new_assignment, future_row):
                    forward_check_ok = False # ...então este caminho é inválido.
                    break
            
            if forward_check_ok:
                # Recursão
                result = self._backtrack(new_assignment, new_unassigned, new_state)
                if result is not None:
                    return result
            
            # Backtrack
            self.backtracks += 1
        
        return None
    
    def plot_search_tree(self):
        """Plota a árvore de busca (CORRIGIDO)"""
        if self.G.number_of_nodes() == 0:
            print("Nenhuma árvore para plotar")
            return
        
        plt.figure(figsize=(16, 10))
        pos = self._hierarchy_pos(self.G, ())
        
        # Atualiza labels com ordem de exploração
        updated_labels = {}
        for node in self.G:
            order = self.exploration_order.get(node, "?")
            if order != "?":
                original_label = self.node_labels.get(node, "")
                updated_labels[node] = f"#{order}\n{original_label}"
            else:
                updated_labels[node] = self.node_labels.get(node, "")
        
        # CORREÇÃO: Prepara lista de nós que fazem parte do caminho da solução
        solution_path_nodes = []
        if self.solution:
            # Converte o dict {row:col} para lista de tuplas [(row,col), ...] ordenada
            sol_list = sorted(self.solution.items())
            # Gera todos os prefixos do caminho
            solution_path_nodes = [tuple(sol_list[:i]) for i in range(1, len(sol_list) + 1)]

        # Define cores
        color_map = []
        for node in self.G:
            # Verde escuro: Solução Final
            if self.solution and node == tuple(sorted(self.solution.items())):
                color_map.append('#4CAF50')
            # Vermelho: Início
            elif len(node) == 0:
                color_map.append('#FF5722')
            # Verde claro: Faz parte do caminho da solução
            elif node in solution_path_nodes:
                color_map.append('#81C784')
            # Azul: Caminhos descartados
            else:
                color_map.append('#89CFF0')
        
        nx.draw(self.G, pos, with_labels=True, labels=updated_labels,
                node_size=3500, node_color=color_map, font_size=7,
                node_shape="s", edge_color="gray", arrows=True)
        
        heuristics_text = f"MRV: {'✓' if self.use_mrv else '✗'}, " \
                          f"Degree: {'✓' if self.use_degree else '✗'}, " \
                          f"LCV: {'✓' if self.use_lcv else '✗'}"
        
        plt.title(f"Árvore CSP com Forward Checking (N={self.n})\n"
                 f"{heuristics_text}\n"
                 f"Nós explorados: {self.nodes_explored} | Backtracks: {self.backtracks}",
                 fontsize=14)
        plt.tight_layout()
        plt.show()
    
    def plot_chessboard(self):
        """Plota o tabuleiro com a solução"""
        if not self.solution:
            print("Nenhuma solução para plotar")
            return
        
        board_img = np.zeros((self.n, self.n))
        for r in range(self.n):
            for c in range(self.n):
                board_img[r, c] = 1 if (r + c) % 2 == 0 else 0.5
        
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(board_img, cmap='gray', vmin=0, vmax=1)
        
        # Plota as rainhas
        for row, col in self.solution.items():
            ax.text(col, row, '♛', fontsize=40, ha='center', va='center',
                    color='gold', weight='bold')
        
        ax.set_title(f"Solução N-Rainhas (N={self.n})\n"
                     f"CSP + Forward Checking", fontsize=14)
        ax.axis('off')
        plt.tight_layout()
        plt.show()
    
    def _hierarchy_pos(self, G, root, width=1., vert_gap=0.2, vert_loc=0,
                       xcenter=0.5, pos=None, parent=None):
        """Calcula posições hierárquicas para o grafo (Layout de árvore)"""
        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)
        
        if len(children) != 0:
            dx = width / len(children)
            nextx = xcenter - width / 2 - dx / 2
            for child in children:
                nextx += dx
                pos = self._hierarchy_pos(G, child, width=dx, vert_gap=vert_gap,
                                          vert_loc=vert_loc - vert_gap,
                                          xcenter=nextx, pos=pos, parent=root)
        return pos


def compare_heuristics(n=8):
    """Compara diferentes combinações de heurísticas"""
    configs = [
        ("Sem heurísticas", False, False, False),
        ("Apenas MRV", True, False, False),
        ("Apenas Degree", False, True, False),
        ("Apenas LCV", False, False, True),
        ("MRV + Degree", True, True, False),
        ("MRV + LCV", True, False, True),
        ("MRV + Degree + LCV", True, True, True),
    ]
    
    print(f"\n{'='*80}")
    print(f"COMPARAÇÃO DE HEURÍSTICAS CSP PARA N={n}")
    print(f"{'='*80}")
    
    results = []
    
    for name, mrv, degree, lcv in configs:
        solver = NQueensCSP(n, use_mrv=mrv, use_degree=degree, use_lcv=lcv)
        
        start = time.time()
        solution = solver.solve()
        elapsed = (time.time() - start) * 1000
        
        results.append({
            'name': name,
            'nodes': solver.nodes_explored,
            'backtracks': solver.backtracks,
            'time': elapsed,
            'found': solution is not None
        })
    
    # Imprime tabela de resultados
    print(f"\n{'='*80}")
    print(f"{'Configuração':<30} {'Nós':<10} {'Backtracks':<12} {'Tempo (ms)':<12} {'Solução'}")
    print(f"{'='*80}")
    
    for r in results:
        status = '✓' if r['found'] else '✗'
        print(f"{r['name']:<30} {r['nodes']:<10} {r['backtracks']:<12} "
              f"{r['time']:<12.2f} {status}")
    
    print(f"{'='*80}\n")


if __name__ == "__main__":
    # Exemplo Principal: Resolver e Plotar
    print("🎯 Resolvendo N=8 com TODAS as heurísticas e Forward Checking")
    # Nota: Para visualização em árvore ficar legível, N=4 ou N=5 é melhor. 
    # Para N=8 a árvore fica muito grande na tela.
    solver = NQueensCSP(8, use_mrv=True, use_degree=True, use_lcv=True)
    solver.solve()
    
    # Plota os gráficos
    solver.plot_search_tree()
    solver.plot_chessboard()
    
    # Exemplo 2: Comparar heurísticas (Opcional)
    # print("\n📊 Comparando diferentes combinações de heurísticas...")
    # compare_heuristics(8)
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import time

class NQueensCSP:
    def __init__(self, n, use_vrm=True, use_grau=True, use_vmr=True):
        self.n = n
        self.use_vrm = use_vrm
        self.use_grau = use_grau
        self.use_vmr = use_vmr
        
        # Estatísticas
        self.nodes_explored = 0
        self.backtracks = 0
        self.solution = None
        
        # Visualização
        self.G = nx.DiGraph()
        self.node_labels = {}
        self.exploration_order = {}
        
        # Domínios: assignment[linha] = coluna (ou None se não atribuído)
        self.assignment = {}
        
    def is_safe_assignment(self, assignment, linha, col):
        """
        Verifica se é seguro colocar uma rainha em (linha, coluna)
        dado o assignment atual (dicionário linha -> coluna)
        """
        for assigned_linha, assigned_col in assignment.items():
            # Mesma coluna
            if assigned_col == col:
                return False
            
            # Mesma diagonal
            if abs(assigned_linha - linha) == abs(assigned_col - col):
                return False
        
        return True
    
    def get_available_colunas(self, assignment, linha):
        """Retorna colunas disponíveis para uma linha dado o assignment"""
        available = []
        for col in range(self.n):
            if self.is_safe_assignment(assignment, linha, col):
                available.append(col)
        return available
    
    def count_conflicts(self, assignment, linha, col):
        """
        Conta quantas posições futuras serão bloqueadas se colocarmos
        uma rainha em (linha, coluna). Usado pela heurística VMR (Valor Menos Restritivo).
        """
        conflicts = 0
        temp_assignment = assignment.copy()
        temp_assignment[linha] = col
        
        # Para cada linha não atribuída
        for future_linha in range(self.n):
            if future_linha not in temp_assignment:
                for future_col in range(self.n):
                    if not self.is_safe_assignment(temp_assignment, future_linha, future_col):
                        conflicts += 1
        
        return conflicts
    
    def vrm_heuristic(self, assignment, unassigned_linhas):
        """
        Heurística VRM (Valores Mínimos Restantes)
        Retorna a linha com MENOS valores disponíveis.
        "Fail-first" - se vai falhar, falhe cedo.
        """
        min_values = float('inf')
        best_linha = None
        
        for linha in unassigned_linhas:
            available = len(self.get_available_colunas(assignment, linha))
            if available < min_values:
                min_values = available
                best_linha = linha
        
        return best_linha
    
    def grau_heuristic(self, board, unassigned_linhas):
        """
        Heurística de Grau
        Retorna a linha que MAIS restringe outras linhas.
        No N-Rainhas, quanto mais cedo na sequência, mais restringe.
        """
        # A linha mais próxima do topo restringe mais linhas futuras
        return min(unassigned_linhas)
    
    def combined_heuristic(self, assignment, unassigned_linhas):
        """
        Combina VRM (Valores Restantes Mínimos) e Grau:
        1. Usa VRM como principal
        2. Em caso de empate, usa grau como desempate
        """
        if not self.use_vrm and not self.use_grau:
            return min(unassigned_linhas)  # Ordem padrão
        
        if self.use_vrm and not self.use_grau:
            return self.vrm_heuristic(assignment, unassigned_linhas)
        
        if not self.use_vrm and self.use_grau:
            return self.grau_heuristic(assignment, unassigned_linhas)
        
        # Ambas habilitadas: VRM (Valores Restantes Mínimos) com desempate por grau
        min_values = float('inf')
        candidates = []
        
        for linha in unassigned_linhas:
            available = len(self.get_available_colunas(assignment, linha))
            if available < min_values:
                min_values = available
                candidates = [linha]
            elif available == min_values:
                candidates.append(linha)
        
        # Se há empate, usa grau (escolhe a linha mais cedo)
        return min(candidates)
    
    def vmr_order_values(self, assignment, linha, available_cols):
        """
        Heurística VMR (Valor Menos Restritivo)
        Ordena as colunas da MENOS restritiva para a MAIS restritiva.
        Prefere valores que deixam mais opções para o futuro.
        """
        if not self.use_vmr:
            return available_cols
        
        # Calcula quantos conflitos cada coluna causa
        col_conflicts = []
        for col in available_cols:
            conflicts = self.count_conflicts(assignment, linha, col)
            col_conflicts.append((col, conflicts))
        
        # Ordena por número de conflitos (menor primeiro)
        col_conflicts.sort(key=lambda x: x[1])
        
        return [col for col, _ in col_conflicts]
    
    def solve(self):
        """Resolve usando backtracking com Forward Checking"""
        print(f"\n{'='*70}")
        print(f"Resolvendo N-Rainhas (N={self.n}) com CSP + Forward Checking")
        print(f"Heurísticas ativas: vrm={self.use_vrm}, grau={self.use_grau}, vmr={self.use_vmr}")
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
                print("Solução validada - sem conflitos!")
            else:
                print("ERRO: Solução tem conflitos!")
        else:
            print(f"\nNenhuma solução encontrada")
        
        print(f"\nEstatísticas:")
        print(f"Nós explorados: {self.nodes_explored}")
        print(f"Backtracks: {self.backtracks}")
        print(f"Tempo: {elapsed:.2f}ms")
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
    
    def _backtrack(self, assignment, unassigned_linhas, parent_state):
        """Backtracking recursivo com Forward Checking"""
        self.nodes_explored += 1
        
        # Caso base: todas as rainhas colocadas
        if len(assignment) == self.n:
            return assignment
        
        # Seleciona próxima linha usando heurística combinada
        linha = self.combined_heuristic(assignment, unassigned_linhas)
        
        # Obtém colunas disponíveis
        available_cols = self.get_available_colunas(assignment, linha)
        
        # Forward Checking (Base): Se a variável atual não tem valores, falha
        if not available_cols:
            self.backtracks += 1
            return None
        
        # Ordena colunas usando VMR (Valor Menos Restritivo)
        ordered_cols = self.vmr_order_values(assignment, linha, available_cols)
        
        # Tenta cada coluna
        for col in ordered_cols:
            # Cria novo assignment
            new_assignment = assignment.copy()
            new_assignment[linha] = col
            
            # Cria estado para visualização (tupla ordenada pelas linhas atribuídas)
            state_list = [(r, new_assignment[r]) for r in sorted(new_assignment.keys())]
            new_state = tuple(state_list)
            
            # Adiciona ao grafo de visualização
            self.G.add_edge(parent_state, new_state)
            self.node_labels[new_state] = f"Q{linha}:{col}"
            self.exploration_order[new_state] = self.nodes_explored
            
            # --- FORWARD CHECKING ---
            # Verifica se essa escolha "matou" alguma linha futura
            new_unassigned = unassigned_linhas - {linha}
            forward_check_ok = True
            
            for future_linha in new_unassigned:
                # Se uma linha futura ficou sem opções válidas...
                if not self.get_available_colunas(new_assignment, future_linha):
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
        """Plota a árvore de busca"""
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
        
        # Prepara lista de nós que fazem parte do caminho da solução
        solution_path_nodes = []
        if self.solution:
            # Converte o dict {linha:coluna} para lista de tuplas [(linha,coluna), ...] ordenada
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
        
        heuristics_text = f"vrm: {'✓' if self.use_vrm else 'X'}, " \
                          f"grau: {'✓' if self.use_grau else 'X'}, " \
                          f"vmr: {'✓' if self.use_vmr else 'X'}"
        
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
        for linha, col in self.solution.items():
            ax.text(col, linha, '♛', fontsize=40, ha='center', va='center',
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
        ("Apenas VRM", True, False, False),
        ("Apenas Grau", False, True, False),
        ("Apenas VMR", False, False, True),
        ("VRM + Grau", True, True, False),
        ("VRM + VMR", True, False, True),
        ("VRM + Grau + VMR", True, True, True),
    ]
    
    print(f"\n{'='*80}")
    print(f"COMPARAÇÃO DE HEURÍSTICAS CSP PARA N={n}")
    print(f"{'='*80}")
    
    results = []
    
    for name, vrm, grau, vmr in configs:
        solver = NQueensCSP(n, use_vrm=vrm, use_grau=grau, use_vmr=vmr)
        
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
        status = '✓' if r['found'] else 'X'
        print(f"{r['name']:<30} {r['nodes']:<10} {r['backtracks']:<12} "
              f"{r['time']:<12.2f} {status}")
    
    print(f"{'='*80}\n")


if __name__ == "__main__":
    # Exemplo Principal: Resolver e Plotar
    print("Resolvendo N=8 com TODAS as heurísticas e Forward Checking")
    # Nota: Para visualização em árvore ficar legível, N=4 ou N=5 é melhor. 
    # Para N=8 a árvore fica muito grande na tela.
    solver = NQueensCSP(8, use_vrm=True, use_grau=True, use_vmr=True)
    solver.solve()
    
    # Plota os gráficos
    solver.plot_search_tree()
    solver.plot_chessboard()
    
    # Exemplo 2: Comparar heurísticas (Opcional)
    #print("\nComparando diferentes combinações de heurísticas...")
    # compare_heuristics(8)
import models.min_heap as min_heap
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import random

class NQueens:
    def __init__(self, n):
        self.n = n
        self.solutions = []
        self.G = nx.DiGraph()
        self.node_labels = {}
        self.colors = [] 

    def is_safe(self, board, row, col):
        for r in range(row):
            c = board[r]
            if c == col or abs(r - row) == abs(c - col):
                return False
        return True

    def heuristic(self, board, current_row):
        blocked_count = 0
        for r in range(current_row + 1, self.n):
            for c in range(self.n):
                if not self.is_safe(board + (c,), r, c): 
                    blocked_count += 1
        return blocked_count

    def solve(self):
        pq = min_heap.ManualMinHeap()
        initial_state = ()
        pq.push((0, 0, initial_state))
        
        self.G.add_node(initial_state)
        self.node_labels[initial_state] = "Início"

        print(f"Procurando uma solução aleatória para N={self.n}...")

        while pq.is_not_empty:
            f, g, current_board = pq.pop()
            row = len(current_board)

            if row == self.n:
                self.solutions.append(current_board)
                print(f"Solução encontrada: {current_board}")
                return


            possible_cols = list(range(self.n))
            random.shuffle(possible_cols) # Mistura a ordem de tentativa, pra não dar o mesmo ramo
            
            for col in possible_cols:
                if self.is_safe(current_board, row, col):
                    new_board = current_board + (col,)
                    
                    new_g = g + 1
                    h = self.heuristic(new_board, row)
                    new_f = new_g + h
                    
                    self.G.add_edge(current_board, new_board)
                    self.node_labels[new_board] = f"Q{row}:{col}\n(f={new_f})"
                    
                    pq.push((new_f, new_g, new_board))

    def plot_search_tree(self):
        if self.G.number_of_nodes() == 0: return

        plt.figure(figsize=(12, 8))
        pos = self._hierarchy_pos(self.G, ())
        
        color_map = []
        for node in self.G:
            if node in self.solutions:
                color_map.append('#4CAF50') 
            elif len(node) == 0:
                color_map.append('#FF5722') 
            else:
                color_map.append('#89CFF0') 

        nx.draw(self.G, pos, with_labels=True, labels=self.node_labels, 
                node_size=2500, node_color=color_map, font_size=8, 
                node_shape="s", edge_color="gray", arrows=True)
        plt.title(f"Árvore Aleatória (N={self.n})", fontsize=14)
        plt.show()

    def plot_chessboard(self):
        if not self.solutions: return
        sol = self.solutions[0]
        
        board_img = np.zeros((self.n, self.n))
        for r in range(self.n):
            for c in range(self.n):
                board_img[r, c] = 1 if (r + c) % 2 == 0 else 0.5
        
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.imshow(board_img, cmap='gray', vmin=0, vmax=1)
        for r, c in enumerate(sol):
            ax.text(c, r, 'Q', fontsize=25, ha='center', va='center', color='gold')
        ax.axis('off')
        plt.show()

    def _hierarchy_pos(self, G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None):
        if pos is None: pos = {root:(xcenter,vert_loc)}
        else: pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None: children.remove(parent)  
        if len(children)!=0:
            dx = width/len(children) 
            nextx = xcenter - width/2 - dx/2
            for child in children:
                nextx += dx
                self._hierarchy_pos(G,child, width=dx, vert_gap=vert_gap, vert_loc=vert_loc-vert_gap, xcenter=nextx, pos=pos, parent=root)
        return pos

if __name__ == "__main__":
    # Teste com N=5, a partir de N=7 os gráficos começam a ficar estranho
    algorithm = NQueens(5)
    algorithm.solve()
    algorithm.plot_search_tree()
    algorithm.plot_chessboard()
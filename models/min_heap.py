

class ManualMinHeap:
    def __init__(self):
        self.heap = []

    def push(self, item):
        # Adiciona um item e reorganiza o heap (bubble up)
        self.heap.append(item)
        self._bubble_up(len(self.heap) - 1)

    def pop(self):
        # Remove e retorna o menor item (raiz) e reorganiza (bubble down)
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        
        root = self.heap[0]
        self.heap[0] = self.heap.pop() # Coloca o último elemento na raiz
        self._bubble_down(0)           # Faz ele descer até a posição correta
        return root

    def is_not_empty(self):
        # Verifica se há elementos na lista
        return len(self.heap) > 0

    def _bubble_up(self, index):
        parent_index = (index - 1) // 2
        # Se o item atual for menor que o pai, troca (pois é um Min-Heap)
        # O Python compara tuplas elemento a elemento (f, g, board), o que é perfeito aqui.
        if index > 0 and self.heap[index] < self.heap[parent_index]:
            self.heap[index], self.heap[parent_index] = self.heap[parent_index], self.heap[index]
            self._bubble_up(parent_index)

    def _bubble_down(self, index):
        smallest = index
        left_child = 2 * index + 1
        right_child = 2 * index + 2
        size = len(self.heap)

        if left_child < size and self.heap[left_child] < self.heap[smallest]:
            smallest = left_child

        if right_child < size and self.heap[right_child] < self.heap[smallest]:
            smallest = right_child

        if smallest != index:
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            self._bubble_down(smallest)
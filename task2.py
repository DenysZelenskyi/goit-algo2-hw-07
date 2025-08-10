import timeit
import sys
from functools import lru_cache
import matplotlib.pyplot as plt
from tabulate import tabulate

sys.setrecursionlimit(5000)



@lru_cache(maxsize=None)
def fibonacci_lru(n):
    if n < 2:
        return n
    return fibonacci_lru(n - 1) + fibonacci_lru(n - 2)


class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None



class SplayTree:
    def __init__(self):
        self.root = None

    def _right_rotate(self, x):
        y = x.left
        x.left = y.right
        y.right = x
        return y

    def _left_rotate(self, x):
        y = x.right
        x.right = y.left
        y.left = x
        return y

    def _splay(self, root, key):
        if root is None or root.key == key:
            return root

        if key < root.key:
            if root.left is None:
                return root
            if key < root.left.key:
                root.left.left = self._splay(root.left.left, key)
                root = self._right_rotate(root)
            elif key > root.left.key:
                root.left.right = self._splay(root.left.right, key)
                if root.left.right:
                    root.left = self._left_rotate(root.left)
            return self._right_rotate(root) if root.left else root
        else:
            if root.right is None:
                return root
            if key > root.right.key:
                root.right.right = self._splay(root.right.right, key)
                root = self._left_rotate(root)
            elif key < root.right.key:
                root.right.left = self._splay(root.right.left, key)
                if root.right.left:
                    root.right = self._right_rotate(root.right)
            return self._left_rotate(root) if root.right else root

    def get(self, key):
        self.root = self._splay(self.root, key)
        if self.root and self.root.key == key:
            return self.root.value
        return None

    def insert(self, key, value):
        if self.root is None:
            self.root = Node(key, value)
            return

        self.root = self._splay(self.root, key)

        if self.root.key == key:
            return

        new_node = Node(key, value)
        if key < self.root.key:
            new_node.right = self.root
            new_node.left = self.root.left
            self.root.left = None
        else:
            new_node.left = self.root
            new_node.right = self.root.right
            self.root.right = None
        self.root = new_node



def fibonacci_splay(n, tree):
    cached = tree.get(n)
    if cached is not None:
        return cached
    if n < 2:
        tree.insert(n, n)
        return n
    val = fibonacci_splay(n - 1, tree) + fibonacci_splay(n - 2, tree)
    tree.insert(n, val)
    return val



def measure_time(func, *args, repeat=3):
    timer = timeit.Timer(lambda: func(*args))
    return timer.timeit(number=repeat) / repeat


ns = list(range(0, 500, 50))
lru_times = []
splay_times = []
results_table = []

for n in ns:
    fibonacci_lru.cache_clear()
    lru_time = measure_time(fibonacci_lru, n)

    tree = SplayTree()
    splay_time = measure_time(lambda: fibonacci_splay(n, tree))

    lru_times.append(lru_time)
    splay_times.append(splay_time)
    results_table.append((n, lru_time, splay_time))

headers = ["n", "LRU Cache Time (s)", "Splay Tree Time (s)"]
print(tabulate([[n, f"{l:.9f}", f"{s:.9f}"] for n, l,
      s in results_table], headers=headers, tablefmt="github"))

plt.figure(figsize=(12, 6))
plt.plot(ns, lru_times, label="LRU Cache", marker="o")
plt.plot(ns, splay_times, label="Splay Tree", marker="s")
plt.xlabel("n — Fibonacci number index")
plt.ylabel("Average execution time (seconds)")
plt.title("Execution Time Comparison: Fibonacci with LRU Cache vs Splay Tree")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
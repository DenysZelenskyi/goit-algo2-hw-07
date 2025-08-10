import random
from time import perf_counter
from collections import OrderedDict
from typing import List, Tuple

N = 100_000     
Q = 50_000      
K = 1000       
SEED = 42      
random.seed(SEED)

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self._od = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key: Tuple[int, int]) -> int:
        if key not in self._od:
            self.misses += 1
            return -1
        self._od.move_to_end(key) 
        self.hits += 1
        return self._od[key]

    def put(self, key: Tuple[int, int], value: int) -> None:
        if key in self._od:
            self._od.move_to_end(key)
        self._od[key] = value
        if len(self._od) > self.capacity:
            self._od.popitem(last=False)  

    def invalidate_index(self, idx: int) -> None:
        """Лінійний прохід по ключах та видалення всіх діапазонів, що містять idx."""
        for key in list(self._od.keys()):
            L, R = key
            if L <= idx <= R:
                del self._od[key]

cache = LRUCache(K)

def range_sum_no_cache(array: List[int], left: int, right: int) -> int:
    return sum(array[left:right + 1])

def update_no_cache(array: List[int], index: int, value: int) -> None:
    array[index] = value

def range_sum_with_cache(array: List[int], left: int, right: int) -> int:
    key = (left, right)
    val = cache.get(key)
    if val != -1:
        return val
    s = sum(array[left:right + 1])
    cache.put(key, s)
    return s

def update_with_cache(array: List[int], index: int, value: int) -> None:
    array[index] = value
    cache.invalidate_index(index)

def make_queries(n: int, q: int, hot_pool: int = 30,
                 p_hot: float = 0.95, p_update: float = 0.03):
    hot = [(random.randint(0, n // 2), random.randint(n // 2, n - 1))
           for _ in range(hot_pool)]
    queries = []
    for _ in range(q):
        if random.random() < p_update:        
            idx = random.randint(0, n - 1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:                                
            if random.random() < p_hot:       
                left, right = random.choice(hot)
            else:                             
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)
            queries.append(("Range", left, right))
    return queries

if __name__ == "__main__":
    array = [random.randint(1, 100) for _ in range(N)]
    queries = make_queries(N, Q)

    arr_nc = array[:] 
    t0 = perf_counter()
    for typ, a, b in queries:
        if typ == "Range":
            range_sum_no_cache(arr_nc, a, b)
        else:  
            update_no_cache(arr_nc, a, b)
    no_cache_time = perf_counter() - t0

    arr_c = array[:]   
    t1 = perf_counter()
    for typ, a, b in queries:
        if typ == "Range":
            range_sum_with_cache(arr_c, a, b)
        else:
            update_with_cache(arr_c, a, b)
    cache_time = perf_counter() - t1

    total_lookups = cache.hits + cache.misses
    hit_rate = (cache.hits / total_lookups * 100) if total_lookups else 0.0
    speedup = (no_cache_time / cache_time) if cache_time > 0 else float("inf")

    print("=== Параметри ===")
    print(f"N={N:,}, Q={Q:,}, K={K}, seed={SEED}")
    print("=== Результати ===")
    print(f"Час без кешу:   {no_cache_time:.3f} с")
    print(f"Час з LRU-кешем:{cache_time:.3f} с")
    print(f"Прискорення:    {speedup:.2f}×")
    print("=== Cache stats ===")
    print(f"Hits: {cache.hits:,}, Misses: {cache.misses:,}, Hit-rate: {hit_rate:.1f}%")

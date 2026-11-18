from collections import OrderedDict, deque
import random

class CacheSet:
    def __init__(self, ways, policy):
        self.ways = ways
        self.policy = policy.upper()
        self.blocks = []
        self.fifo = deque()
        self.lru = OrderedDict()

    def access(self, tag):
        if tag in self.blocks:
            if self.policy == "LRU":
                self.lru.move_to_end(tag)
            return True, None

        evicted = None
        if len(self.blocks) >= self.ways:
            if self.policy == "FIFO":
                evicted = self.fifo.popleft()
            elif self.policy == "LRU":
                evicted, _ = self.lru.popitem(last=False)
            else:
                evicted = random.choice(self.blocks)
            self.blocks.remove(evicted)
            self.lru.pop(evicted, None)

        self.blocks.append(tag)
        self.fifo.append(tag)
        self.lru[tag] = True
        return False, evicted

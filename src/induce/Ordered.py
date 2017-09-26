import sys, collections

class Multidict(collections.defaultdict):
    def merge(self, g2):
        for k,v in g2.items(): self[k] = self[k] | v

class RSet(set):
    def replace(self, key, replacement):
        self.remove(key)
        self.add(replacement)


# Create a trie data structure for searching case problems or output problems

class trie:

    def __init__(self):

        self.root = TrieNode()

    def insert(self, title: str):

        node = self.root 

        for char in title:

            node = node.children.setdefault(char, TrieNode())

        node.is_end = True

    def getWordsWithPrefix(self, prefix: str):

        node = self.root
        
        for char in prefix:
            if char not in node.children:
                return []         
            node = node.children[char]
        
        words = []
        self._collect(node, prefix, words)
        return words

    def _collect(self, node, current_word, words):
        if node.is_end:
            words.append(current_word)      

        for char in node.children:          
            next_node = node.children[char]
            self._collect(next_node, current_word + char, words)

class TrieNode:

    def __init__(self):

        self.children = {}
        self.is_end = False








# Create a trie data structure for searching case problems or output problems

class trie:

    def __init__(self):

        self.root = TrieNode()

    def insert(self, titles: str):

        node = self.root 

        for title in titles:

            node = node.children.setdefault(title, TrieNode())

        node.is_end = True

    def getWordsWithPrefix(self, prefix: str):

        node = self.root

        # walk down to the end of the prefix
        for char in prefix:
            if char not in node.children:
                return []           # prefix doesn't exist, return empty
            node = node.children[char]

        # now collect all words from this node downward
        words = []
        self._collect(node, prefix, words)
        return words

    def _collect(self, node, current_word, words):
        if node.is_end:
            words.append(current_word)      # found a complete word

        for char in node.children:          # try every child
            next_node = node.children[char]
            self._collect(next_node, current_word + char, words)

class TrieNode:

    def __init__(self):

        self.children = {}
        self.is_end = False








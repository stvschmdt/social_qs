import csv
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

from nltk import word_tokenize

import logger
import instaparse
import formatter

class Node(object):

    def __init__(self, tag):
        self.tag = tag



class Edge(object):

    def __init__(self, n1, n2):
        self.left = n1
        self.right = n2


class GraphBuilder(object):

    def __init__(self, items=None):
        self.G = nx.Graph()

    def create_nodes(self, l_items):
        l_nodes = []
        for n in l_items:
            l_nodes.append(Node(n))
        return l_nodes

    #this should take in nodes list and post dict of comments
    def edges_from_text(self, hashtags_dict, valid_list):
        for idx, tags in hashtags_dict.items():
            #tokenize the comment
            #get all permutations of edges - not to oneself tho
            edges = [(i,j) for i in tags for j in tags if i != j and i in valid_list and j in valid_list]
            #loop through each pair and add or update edge weight
            for e in edges:
                if self.G.has_edge(e[0], e[1]):
                    self.G[e[0]][e[1]]['weight'] += 1
                else:
                    self.G.add_edge(e[0], e[1], weight= 1)
            

    def build_nodes(self, nodes):
        self.G.add_nodes_from(nodes)
        return 0
    
if __name__ == '__main__':
    bldr = GraphBuilder()

#author steve schmidt
#this class object takes in a instaparse object or the
#equivalent data structures to format into the following
#   paragraph level text
#   sentence level text
#   word histogram
#   word tag dictionary
from __builtin__ import any as b_any

import csv
import numpy as np
import pandas as pd
import argparse
import matplotlib.pyplot as plt
import collections
import networkx as nx


from nltk import sent_tokenize, word_tokenize, pos_tag
from collections import Counter


import logger
import instaparse
import graphbuilder

class Formatter(object):

    def __init__(self, IP, FLAGS):
        self.log = logger.Logging()
        if not FLAGS.outfile:
            self.log.error('must supply an output file')
        else:
            if FLAGS.all:
                self.paragraphs = self.create_paragraphs(IP.comments.values())
                self.num_paragraphs = len(self.paragraphs)
                self.sentences = self.create_sentences(IP.comments.values())
                self.num_sentences = len(self.sentences)
                self.words, self.pos_words = self.create_words(IP.comments.values())
                self.num_words = len(self.words)
            elif FLAGS.sent:
                self.create_sentences(IP.comments.values())
                self.words, self.pos_words = self.create_words(IP.comments.values())
                self.num_words = len(self.words)
            elif FLAGS.para:
                self.create_paragraphs(IP.comments.values())
                self.words, self.pos_words = self.create_words(IP.comments.values())
                self.num_words = len(self.words)
               
    #create paragraphs, this is probably less important than sentences
    def create_paragraphs(self, paragraphs):
        para_list = []
        for idx, para in enumerate(paragraphs):
            para = self.clean(para)
            para_list.append(para)
        self.log.info('found %s paragraphs'%len(para_list))
        return para_list

    #create a list of sentences used in comments - each actual sentence is a sentence, use helper function for nltk
    def create_sentences(self, sentences):
        sent_list = []
        #extra little something
        pos_tag_list = []
        #input must just be the vals of the dict = aka a list of comments
        for idx, sent in enumerate(sentences):
            try:
                #split the comments in case multiple sentences or fragments
                splitter = sent_tokenize(sent)
            except Exception as e:
                print idx
            for split in splitter:
                split = self.clean(split)
                sent_list.append(split)
        self.log.info('found %s sentences'%len(sent_list))
        return sent_list
    
    #helper function to clean some rando off the strings before encoding
    def clean(self, tok):
        tok = tok.replace(':','')
        tok = tok.replace(';','')
        tok = tok.replace('(','')
        tok = tok.replace(')','')
        tok = tok.replace('-','')
        return tok

    def create_words(self, corpus):
        word_dict = collections.defaultdict(int)
        tag_dict = collections.defaultdict()
        #loop through corpus, clean, then split words and count em
        for idx,tok in enumerate(corpus):
            tok = self.clean(tok)
            words = word_tokenize(tok)
            for word in words:
                word_dict[word.lower()] += 1
            #get the nltk noun, verb tag out may as well
            tag_dict[idx] = pos_tag(words)
        self.log.info('found %s unique words'%len(word_dict))
        return collections.OrderedDict(sorted(word_dict.items(), key=lambda val: val[1], reverse=True)), tag_dict

    #return top word dict
    def top_n_words(self, n, data=None):
        if not data:
            data = self.words
        top = Counter(data)
        return top.most_common(n)

    def write_clique(self, l_clique):
        with open('scrape_file.txt', 'w') as f:
            for l in l_clique:
                f.write('{}\n'.format(l))


if __name__ == '__main__':
    #argument parser - demand an infile to avoid overwriting data
    parser = argparse.ArgumentParser()
    parser.add_argument('-of', dest='outfile', default='../data/', help='supply outfile to save data into')
    parser.add_argument('-if', dest='infile', default='../data/', help='supply infile for instaparse')
    parser.add_argument('-graphics', dest='graphics', default=False, action='store_true', help='turn graphics on / off')
    parser.add_argument('-create', dest='create', default=True, action='store_true', help='create full dictionary')
    parser.add_argument('-all', dest='all', default=True, action='store_true', help='create all dictionarys')
    #store in FLAGS
    FLAGS = parser.parse_args()
    #instaparse object
    if not (FLAGS.outfile and FLAGS.infile):
        print 'USAGE: must supply outfile to save data'
    else:
        ip = instaparse.InstaParse(FLAGS.infile, FLAGS)
        #return dictionary
        data = ip.get_data()
        f = Formatter(ip, FLAGS)	
        graph = graphbuilder.GraphBuilder()
        top_tags = [ t for t,c in ip.tags.items() if c >= 10 ]
        graph.edges_from_text(ip.d_insta, top_tags)
        #ccs = nx.connected_component_subgraphs(graph.G)
        #for c in ccs:
        cliq = list(nx.find_cliques(graph.G))
        skips = ['firestone']
        next_scrapings = set()
        for c in cliq:
            for word in c:
                if b_any(x in word for x in skips):
                    print word
                else:
                    next_scrapings.add(word)
        f.write_clique(next_scrapings)
        nx.make_max_clique_graph(graph.G)
        pos = nx.spring_layout(graph.G)
        elarge=[(u,v) for (u,v,d) in graph.G.edges(data=True) if d['weight'] > 15]
        esmall=[(u,v) for (u,v,d) in graph.G.edges(data=True) if d['weight'] <= 15]
        nx.draw_networkx_nodes(graph.G,pos,node_size=10)
        nx.draw_networkx_edges(graph.G,pos,edgelist=elarge,width=3,edge_color='g')
        nx.draw_networkx_edges(graph.G,pos,edgelist=esmall,width=1,alpha=0.5,edge_color='b',style='solid')
        nx.draw_networkx_labels(graph.G,pos,font_size=7,font_family='sans-serif')
        #nx.draw(graph.G)
        plt.axis('off')
        plt.show()

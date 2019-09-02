import json
import sys
import csv
import numpy as np
from collections import Counter
import collections
import matplotlib.pyplot as plt
import argparse
from unidecode import unidecode

import logger

class InstaParse(object):

    def __init__(self, filename, FLAGS=None):
        self.fn = filename
        self.log = logger.Logging()
        with open(filename, 'rb') as f:
            self.data = json.load(f)
            self.log.info('read in json data from %s'%filename)
        # create master dictionary key post.id value tags to each post
        self.d_insta = collections.defaultdict()
        #holder for set of columns found in any and all posts
        self.col_insta = set()
        #dictionary counting tags overall in the corpus
        self.tags = collections.defaultdict(int)
        #dictionary linking views to a post id
        self.views = collections.defaultdict(int)
        #dictionary of users
        self.users = collections.defaultdict()
        #dictionary of actual urls for quick view
        self.urls = collections.defaultdict()
        #dictionary of likes
        self.likes = collections.defaultdict(int)
        #dictionary of comments in edge, node format
        self.comments = collections.defaultdict()
        if FLAGS.create:
            self.create_data_dict()

    def get_data(self):
        return self.data

    def create_data_dict(self):
        for post in self.data:
            #use pid as post id for all dict keys
            pid = post['id']
            # run through the comment dictionary format (odd) to get text
            for p in post.get('edge_media_to_caption','').items():
                for l in p[1]:
                     self.comments[pid] = unidecode(l['node']['text'])
            #self.comments[pid] = unidecode(post['edge_media_to_caption']['edges'][0]['node']['text'])
            
            #retrieve the list of tags for this post
            tgs = post.get('tags','')
            self.urls[pid] = post.get('display_url','')
            self.users[pid] = post.get('owner','')
            #loop through list of tags, and count them in master tags dict
            for t in tgs:
                t = t.lower()
                self.tags[t] += 1
            #master post to list of tags update add
            self.d_insta[post['id']] = tgs
            #get number of likes and convert to num
            ppl = post.get('edge_liked_by', '')
            self.likes[pid] += int(ppl.get('count',0))
            #count video views
            views = post.get('video_view_count',0)
            self.views[pid] += int(views)
            #lastly for bookkeeping and investigation, lets see what all columns we scraped
            for k in post.keys():
                self.col_insta.add(k)
        #make tags dictionary ordered by largest frequency of tags
        self.tags = collections.OrderedDict(sorted(self.tags.items(), key=lambda val:val[1], reverse=True))
        self.log.info('data contains columns %s'%self.col_insta)
        self.log.info('data contains %s posts'% len(self.data))
        self.log.info('data contains %s unique tags'% len(self.tags))
        return self.d_insta
            
    def top_n_hashtags(self, n, data=None):
        #can supply own dict of tags
        if not data:
            data = self.tags
        top = Counter(data)
        return top.most_common(n)

if __name__ == '__main__':
    #argument parser - demand an infile to avoid overwriting data
    parser = argparse.ArgumentParser()
    parser.add_argument('-if', dest='infile', help='supply infile json to read data into')
    parser.add_argument('-graphics', dest='graphics', default=False, action='store_true', help='turn graphics on / off')
    parser.add_argument('-create', dest='create', default=True, action='store_true', help='create full dictionary')
    #store in FLAGS
    FLAGS = parser.parse_args()
    #instaparse object
    if not FLAGS.infile:
        print 'USAGE: must supply json filename to read'
    else:
        ip = InstaParse(FLAGS.infile, FLAGS)
        #return dictionary
        data = ip.get_data()
    #print 'top hashtags'
    #print top
    #print 'top persons'
    #print ip.people
    #xtags = [ t[0] for t in top ]
    #y = [ t[1] for t in top ]
    #x = range(len(top))
    #plt.xticks(x,xtags, rotation='vertical')
    #plt.yticks(range(0,np.max(y), 10))
    ##plt.grid(b=True, which='major', linestyle='--')
    #plt.bar(x,y, align='edge', color='green')
    #plt.show()



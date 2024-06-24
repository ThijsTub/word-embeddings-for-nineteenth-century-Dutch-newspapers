# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 08:50:35 2024

@author: Thijs
"""

from gensim.models import Word2Vec
from gensim.models.word2vec import PathLineSentences
from gensim.models.callbacks import CallbackAny2Vec
import multiprocessing
from os import walk
import os
from tqdm import tqdm

# Epochlogger is used to track progress of word embedding creation
class EpochLogger(CallbackAny2Vec):

    '''Callback to log information about training'''


    def __init__(self):

        self.epoch = 0


    def on_epoch_begin(self, model):

        print("Epoch #{} start".format(self.epoch))


    def on_epoch_end(self, model):

        print("Epoch #{} end".format(self.epoch))

        self.epoch += 1

epoch_logger = EpochLogger()

# I saved the data in folders for each timeframe I wanted to construct word embeddings for
# Here I retrieve the names of the folders to locate the data and give a name to the word embeddings
input_dir = r'D:\Thijs\Python\potatoPrograms\data\preprocessedTextPerYear' 
paths = []
pathNames = []
for (dirpath, dirnames, filenames) in walk(input_dir):
    paths.extend(os.path.join('data', 'preprocessedTextPerYear', dirname) for dirname in dirnames)
    pathNames.extend(dirnames)    

# Make word embeddings for each timeframe
for (path, pathName) in tqdm(zip(paths, pathNames)):
    print(path)

    model = Word2Vec(PathLineSentences(path), 
                      vector_size=300, 
                      window=5,
                      workers=multiprocessing.cpu_count() * 2,
                      epochs=5,
                      callbacks=[epoch_logger])
    
    word_vectors = model.wv
    
    outfile = os.path.join('models', 'wordvectorsTimeLine', pathName + '_wv.wordvectors')
    word_vectors.save(outfile)

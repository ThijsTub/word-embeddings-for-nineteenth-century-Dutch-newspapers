# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 10:50:25 2024

@author: Thijs
"""
from os import walk
import os
from gensim.models import KeyedVectors
import pandas as pd
from tqdm import tqdm

def getDfSimilarWords(wordsOfReference, paths, pathNames):
    similarWordsDf = pd.DataFrame()
    
    for (path, pathName) in zip(paths, pathNames):
        wv = KeyedVectors.load(path)
        
        try:          
            similarWords = []
            similarWordValues = []
            for similarWord in wv.most_similar(wordsOfReference, topn=150):
                similarWords.append(list(similarWord)[0])
                similarWordValues.append(float(list(similarWord)[1]))
            
            newData = {pathName + '_similar word' : similarWords, pathName + '_similarity value' : similarWordValues}
            similarWordsDf = similarWordsDf.assign(**newData)
        except KeyError:
            continue
        
    return similarWordsDf
        
def calculateCosineSimilarities(wordsOfInterest, wordsOfReference, paths, pathNames):    
    
    def getSimilarity(wordOfReference, wordOfInterest):
        try:
            return float(wv.similarity(wordOfReference, wordOfInterest))
        except KeyError:
            return 0
    
    def getWeight(word):
        try:
            return wv.get_vecattr(word, 'count')
        except KeyError:
            return 1
    
    results = {}
    
    for (path, pathName) in zip(paths, pathNames):
        similarities = {}
        
        wv = KeyedVectors.load(path)
        
        wordWeights = [getWeight(wordOfReference) for wordOfReference in wordsOfReference]
        
        for wordOfInterest in tqdm(wordsOfInterest):
            try:
                if wordOfInterest in wordsOfReference:
                    continue
                elif wv.get_vecattr(wordOfInterest, 'count') < 10:
                    similarities[wordOfInterest] = '#N/B'
                else:
                    wordSimilarities = [getSimilarity(wordOfReference, wordOfInterest) for wordOfReference in wordsOfReference]
                    weightedWordSimilarities = [wordSimilarity * wordWeight for (wordSimilarity, wordWeight) in zip(wordSimilarities, wordWeights)]
                    meanSimilarity = sum(weightedWordSimilarities) / sum(wordWeights)
                    similarities[wordOfInterest] = meanSimilarity
            except KeyError:
                similarities[wordOfInterest] = '#N/B'
          
        results[pathName] = similarities
    
    similaritiesDf = pd.DataFrame(results)
        
    return similaritiesDf

# Define the reference and interest words
potatoWords = ['aardappel', 'aardappels', 'aardappelen']
wordsOfInterest = ['nederland', 'wetenschap', 'landman', 'verlichting', 'oeconomie', 'landbouw', 'statistiek', 'boer', 'hoogleraar']

# Set the input directory where word vector files are saved
input_dir = r'D:\Thijs\Python\potatoPrograms\data\preprocessedTextPerYear' 

# Give the names of the vectorfiles and build their related paths
pathNames = ['1815-1824', '1825-1834', '1835-1844', '1845-49', '1850-54', '1855-59', '1860-64', '1865-1869', '1870-1874', '1875-1879'] 
paths = [os.path.join('models', 'wordvectorsTimeline', pathName + '_wv.wordvectors') for pathName in pathNames]

# Get the DataFrame of similar words and save it to a CSV file
similarWordsDf = getDfSimilarWords(wordsOfInterest, paths, pathNames)
similarWordsDf.to_csv('similarWords.csv', sep=';')

# Calculate the cosine similarities and save the results to a CSV file
similaritiesDf = calculateCosineSimilarities(wordsOfInterest, potatoWords, paths, pathNames)
similaritiesDf.to_csv('cosineSimilarities.csv', sep=';')


    
    

        

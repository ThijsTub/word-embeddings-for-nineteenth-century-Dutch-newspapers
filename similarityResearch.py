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

input_dir = r'D:\Thijs\Python\potatoPrograms\data\preprocessedTextPerYear'

pathNames = []
for (dirpath, dirnames, filenames) in walk(input_dir):
    pathNames.extend(dirnames) 

paths = [os.path.join('models', 'wordvectorsTimeline', pathName + '_wv.wordvectors') for pathName in pathNames]

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

def getListSimilarWords(wordOfReference, paths, pathNames):
    similarWords = []
    for (path, pathName) in zip(paths, pathNames):
        wv = KeyedVectors.load(path)
        
        try:
            for similarWord in wv.most_similar(wordOfReference, topn=68):
                similarWords.append(list(similarWord)[0])
        except KeyError:
            continue
        
    return list(set(similarWords))
        
    

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

wordsOfInterest = [
    'gedroogde',
    'klaver',
    'knollen',
    'veevoeder',
    'druiven',
    'gerooid',
    'poters',
    'spurrie',
    'gerooid',
    'meel',
    'zaad',
    'rot',
    'ziekte',
    'aardappelziekte',
    'verderf',
    'gezond',
    'gezondheid',
    'insect',
    'veldmuizen',
    'rups',
    'wetenschap',
    'kennis',
    'proef',
    'proefondervindelijk',
    'smaak'
    ]

potatoWords = [
    'aardappel', 
    'aardappels', 
    'aardappelen'
         ]

diseaseWords = [
    'aardappelziekte'
    ]

wordsOfInterestWetenschap = [
    'beschaving',
    'befchaving',
    'kunst',
    'verlichting',
    'godsvrucht',
    'theoretische',
    'theorie',
    'theoretisch',
    'praktische',
    'praktijk',
    'praktisch',
    ]

wordsToCompare = [
    'jenever',
    'voeder',
    'meel',
    'brood',
    'ziekte',
    'bederf',
    'stank',
    'smakelijk',
    'verrot',
    'mooi',
    'overheerlijk',
    'slakken',
    'muizen',
    'wormen',
    'insekten',
    'onkruid',
    'aardappelziekte',
    'worm',
    'nachtvorsten',
    'hazen',
    'loof',
    'vroege',
    'zaad',
    'wetenschap',
    'landman',
    'boer',
    'bemeste',
    'mest',
    'gezaaid',
    'bezaaijen',
    'bezaaide',
    'gemaaid',
    'maaijen',
    'bemest',
    'bepoot',
    'geteeld',
    'gepoot',
    'omgeploegd',
    'gerooid',
    'kalk',
    'bearbeid',
    'geoogst',
    'gezaaide',
    'uitgezaaid',
    'gebakken',
    'gezouten',
    'gepelde',
    'gekookt',
    'gerookt',
    'gedroogd',
    'overgehouden',
    'gestookt',
    'gemalen',
    'heete',
    'flesschen',
    'vaten',
    'gewassen']

wordsOfReferenceWetenschap = ['wetenschap', 'weienschap', 'wetenfehappen', 'wetenfehap', 'wetenschappen']
wordsOfInterest = ['nederland', 'wetenschap', 'landman', 'verlichting', 'oeconomie', 'landbouw', 'statistiek', 'boer', 'hoogleraar']

# similarWordsDf = getDfSimilarWords(['hoogleraar'], paths, pathNames)
# similarWordsDf.to_csv('wordsSimilarToHoogleraar.csv', sep=';')

# similarWordList = []
# for wordOfInterest in tqdm(potatoWords):
#     similarWordList += getListSimilarWords(wordOfInterest, [paths[3]], [pathNames[3]])
# similarWordList = getListSimilarWords(['aardappelziekte'], [paths[3]], [pathNames[3]])

similaritiesDf = calculateCosineSimilarities(wordsOfInterest, potatoWords, paths, pathNames)
similaritiesDf.to_csv('timelineTargetedSearch02.csv', sep=';')


    
    

        
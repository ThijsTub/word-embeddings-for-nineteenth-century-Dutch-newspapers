# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 15:58:13 2024

@author: Thijs
"""
#create preprocessed textfile for each year

from scripts import getData
import time
import os
import spacy
from tqdm import tqdm

startTime = time.time()

#set metadataPath
metadataPath = os.path.join('metadata', 'metadata_kranten_1810-1879.csv')

#set filters for iterations
years = range(1879, 1880)
startMonth = '01'
startDay = '01'
endMonth = '12'
endDay = '31'
 
#set other filters
excludedNewspapersFilter = []
contentFilter = ['artikel']
circulationFilter = ['Regionaal/lokaal']   #Regionaal/lokaal, Landelijk
languageFilter = ['nl', 'NL', 'Nl']

#set circulation name for outPaths
circulationName = '+'.join(circulationFilter).replace('/','+')

#import stopwords
with open('stopwoorden.txt', 'r') as f:
    stopwordList = f.read().split(' ')
stopwordSet = set(stopwordList)
del stopwordList

#import approved vocabulary
vocabularyList = []
with open('WoordenlijstHistorischNederlands_lowercase.txt', 'r', encoding = 'utf8') as f:
    for line in f.read().splitlines():
        vocabularyList.append(line)
vocabularySet = set(vocabularyList)
del vocabularyList

prefilteredMetadata = getData.filterMetadata(metadataPath, 
                              excludedNewspapers = excludedNewspapersFilter,  
                              content = contentFilter,
                              startdate = '1810-01-01',
                              enddate = '1879-12-31',
                              circulation = circulationFilter,
                              language = languageFilter,
                              )

#load and filter metadata
for year in years:
    #load SpaCy sentencizer for each iteration to reduce memory usage over time
    nlp = spacy.blank('nl')
    nlp.add_pipe('sentencizer')
    
    startdate = '-'.join([str(year), startMonth, startDay])  
    enddate = '-'.join([str(year), endMonth, endDay])
    
    filteredMetadata = prefilteredMetadata.loc[
        (prefilteredMetadata['date']>=startdate)&
        (prefilteredMetadata['date']<=enddate)
                                        ]
    print('Number of articles found for year %s: %s' % (year, len(filteredMetadata)))
    
    #processing in batches
    batchSize = 1000
    totalRows = len(filteredMetadata)
    
    print('Gathering and processing text in batches of a %s articles' % batchSize)
    preprocessedText = []
    for i in tqdm(range(0, totalRows, batchSize)):
        batch = filteredMetadata.iloc[i:i+batchSize]
    
        #getting text from batch of filtered articles
        text = getData.getText(batch)
        #convert paragraphs to sentences using SpaCy
        sentencizedText = getData.textToSentences(text, nlp)
        #preprocessing
        preprocessedText += getData.preprocess(sentencizedText, stopwordSet, vocabularySet)
    
    #count words in preprocessedText
    with open('keep_wordcounts_for_yearly_datasets.txt', 'a') as f:
        f.write(str(year)+' '+str(sum(len(sent) for sent in preprocessedText))+'\n')
    print('Amount of words in preprocessed text: %s' % sum(len(sent) for sent in preprocessedText))
    
    #write preprocessed text to file
    preprocessedDataOutPath = os.path.join('data', 'preprocessedTextPerYear', str(year) + '_preprocessedArticleText_' + circulationName)
    getData.writeDataToFile(preprocessedDataOutPath, preprocessedText)
    print('--- %s seconds ---' % (time.time() - startTime))
    print('The preprocessed text data can be found at: %s \n' % preprocessedDataOutPath)
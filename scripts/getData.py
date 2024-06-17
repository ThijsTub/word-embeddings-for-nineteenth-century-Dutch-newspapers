# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 09:15:22 2024

@author: Thijs
"""
from bs4 import BeautifulSoup as BS
import pandas as pd
import time
import os
import spacy
from tqdm import tqdm

def filterMetadata(metadataPath, excludedNewspapers, content, startdate, enddate, circulation, language):        
    #filter metadata in chunks
    filteredMetadatas = []
    for chunk in pd.read_csv(metadataPath, sep=';', index_col='Unnamed: 0', chunksize=1000):
        filteredMetadatas.append(chunk.loc[
            (~chunk['newspaperTitle'].isin(excludedNewspapers))&
            (chunk['content'].isin(content))&
            (chunk['date']>=startdate)&
            (chunk['date']<=enddate)&
            (chunk['circulation'].isin(circulation))&
            (chunk['language'].isin(language))
                                            ])
    #put together chunks
    filteredMetadata = pd.concat(filteredMetadatas, ignore_index=True)
    
    return filteredMetadata

def getText(metadata):
    articlePaths = [path for path in metadata['path']]
    
    text = []
    for articlePath in articlePaths:
        try:
            with open(articlePath, encoding='utf8') as articleFile:
                articleRoot = BS(articleFile, 'xml')
            articleText = articleRoot.find('text')
            paragraphs = articleText.find_all('p')
            
            for paragraph in paragraphs:
                text.append(paragraph.text)
        except FileNotFoundError: 
            continue       
        
    return text

def textToSentences(text, nlp):  
    sents = []
    for paragraph in text:
        sents += nlp(paragraph).sents
    
    sentencizedText = []
    for sent in sents:
        tokens = []
        for token in sent:
            tokens.append(token.text)
        sentencizedText.append(tokens)
    
    return sentencizedText

def preprocess(text, stopwordSet, vocabularySet):
    newText = []
    for sent in text:
        #add lowercased token to new sentence if token is longer than 3 and shorter than 15 characters
        newSent = [token.lower() for token in sent if len(token)>3 and len(token)<16]
        
        #keep tokens that are not stopwords
        newSent = [token for token in newSent if token not in stopwordSet]
        
        #keep sentences with 70 percent or more tokens that are in vocabulary
        lenSent = len(newSent)
        if lenSent > 2:
            realWordCount = 0
            realWords = []
            for token in newSent:
                if token in vocabularySet:
                    realWordCount += 1
                    realWords.append(token)
            if realWordCount / lenSent >= 0.7:
                newText.append(newSent)

    return newText

def writeDataToFile(dataName, sentencizedText):
    with open(dataName + '.txt', 'w', encoding='utf8') as outfile:
        for sent in sentencizedText:
            outfile.write(' '.join(token for token in sent) + '\n')

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

#load and prefilter metadata
prefilteredMetadata = filterMetadata(metadataPath, 
                              excludedNewspapers = excludedNewspapersFilter,  
                              content = contentFilter,
                              startdate = '1810-01-01',
                              enddate = '1879-12-31',
                              circulation = circulationFilter,
                              language = languageFilter,
                              )

#get data per year
for year in years:
    #load SpaCy sentencizer for each iteration to reduce memory usage over time
    nlp = spacy.blank('nl')
    nlp.add_pipe('sentencizer')
    
    startdate = '-'.join([str(year), startMonth, startDay])  
    enddate = '-'.join([str(year), endMonth, endDay])

    #filter prefiltered metadata
    filteredMetadata = prefilteredMetadata.loc[
        (prefilteredMetadata['date']>=startdate)&
        (prefilteredMetadata['date']<=enddate)                             ]
    print('Number of articles found for year %s: %s' % (year, len(filteredMetadata)))
    
    #processing in batches
    batchSize = 1000
    totalRows = len(filteredMetadata)
    print('Gathering and processing text in batches of a %s articles' % batchSize)
    
    preprocessedText = []
    for i in tqdm(range(0, totalRows, batchSize)):
        batch = filteredMetadata.iloc[i:i+batchSize]
    
        #getting text from batch of filtered articles
        text = getText(batch)
        #convert paragraphs to sentences using SpaCy
        sentencizedText = textToSentences(text, nlp)
        #preprocessing
        preprocessedText += preprocess(sentencizedText, stopwordSet, vocabularySet)
    
    #count words in preprocessedText
    with open('keep_wordcounts_for_yearly_datasets.txt', 'a') as f:
        f.write(str(year)+' '+str(sum(len(sent) for sent in preprocessedText))+'\n')
    print('Amount of words in preprocessed text: %s' % sum(len(sent) for sent in preprocessedText))
    
    #write preprocessed text to file
    preprocessedDataOutPath = os.path.join('data', 'preprocessedTextPerYear', str(year) + '_preprocessedArticleText_' + circulationName)
    writeDataToFile(preprocessedDataOutPath, preprocessedText)
    print('--- %s seconds ---' % (time.time() - startTime))
    print('The preprocessed text data can be found at: %s \n' % preprocessedDataOutPath)

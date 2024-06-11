# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 09:15:22 2024

@author: Thijs
"""
from bs4 import BeautifulSoup as BS
import pandas as pd

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


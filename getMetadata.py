# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 13:34:04 2024

@author: Thijs
"""
from bs4 import BeautifulSoup as BS
import re
from tqdm import tqdm
import os
import csv

def extractMetadataFromDidlFile(path):
    metadataDidl = []
    
    #open didl file
    didlPath = os.path.join(path, 'didl.xml')
    try: 
        with open(didlPath, encoding = 'utf8') as didlFile:
            didlRoot = BS(didlFile,'xml')
    except FileNotFoundError:
        print('didlFile not found')
        return
    
    #get newspaper metadata
    newspaperTitle = didlRoot.find('title').text
    date = didlRoot.find('date').text
    frequency = didlRoot.find('temporal').text
    publisher = didlRoot.find('publisher').text
    circulation = didlRoot.find('spatial').text
    language = didlRoot.find('language').text
    newspaperId = didlRoot.find('recordIdentifier').text
    
    #get metadata for each article in newspaper
    articles = didlRoot.find_all('Item', attrs = {'dc:identifier':re.compile(newspaperId + ':a')})
    
    for article in articles:
        articleId = article.find('recordIdentifier').text
        resource = article.find('Resource', attrs = {'dcx:filename':True})
        try: 
            filename = resource.get('dcx:filename')
        except AttributeError:
            print(articleId)
            filename = ''
            
        
        metadataArticle = {
            'articleId' : articleId,
            'articleTitle' : article.find('title').text,
            'content' : article.find('subject').text,
            'path' : os.path.join(path, filename),
            'newspaperTitle' : newspaperTitle,
            'date' : date,
            'frequency' : frequency,
            'publisher' : publisher,
            'circulation' : circulation,
            'language' : language,
            'url' : article.find('identifier').text
            }
        metadataDidl.append(metadataArticle)
        
    return metadataDidl

def createDidlPaths(indexPath, datasetPath):
    #open index
    with open(indexPath, 'r', encoding='utf8') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        index = [row for row in reader]
    
    #build paths
    paths = []
    for item in index:
        # if item[0] == 'Arnhemsche courant':
        path = item[3].replace('.', datasetPath)
        paths.append(path)
    
    return paths

#define datasets by their name 
datasets = [
    'kranten_pd_181x',
    'kranten_pd_182x',
    'kranten_pd_183x',
    'kranten_pd_184x',
    'kranten_pd_1850-4',
    'kranten_pd_1855-9',
    'kranten_pd_1860-4',
    'kranten_pd_1865-9',
    'kranten_pd_1870-4',
    'kranten_pd_1875-6',
    'kranten_pd_1877-9'
    ]

#compile metadata for each dataset
for dataset in datasets:
    datasetPath = os.path.join('D:\Thijs\Python', dataset)
    print(datasetPath)
    indexPath = os.path.join(datasetPath, 'index_' + dataset + '.tsv')
    paths = createDidlPaths(indexPath, datasetPath)
    
    #process didl files per batch
    batch_size = 100  # Adjust the batch size as needed
    
    metadata = []
    for i in tqdm(range(0, len(paths), batch_size)):
        batch_paths = paths[i:i + batch_size]
        batch_metadata = [extractMetadataFromDidlFile(path) for path in batch_paths]
        for sublist in batch_metadata:
            if sublist is not None:
                metadata += [item for item in sublist]
    
    #create pandas DataFrame of metadata
    import pandas as pd
    metadataDf = pd.DataFrame(data=metadata)
    metadataDf['date'] = pd.to_datetime(metadataDf['date'], format='%Y-%m-%d')
    print(metadataDf.head(None))

    metadataDf.to_csv('metadata_'+dataset+'.csv', sep = ';')

#make one csv metadata file
filenames = ['metadata_' + dataset + '.csv' for dataset in datasets]
metadatas = [pd.read_csv(filename, sep=';', index_col = 'Unnamed: 0') for filename in filenames]
metadata = pd.concat(metadatas, ignore_index=True)
metadata.to_csv(r'D:\Thijs\Python\metadata_kranten_1810-1879.csv', sep = ';')

This repository in first instance aims to document the scripts created for my thesis to clarify my research methodology. 
The scripts and word embeddings may also be useful for anyone looking to conduct similar research as I did. 

The data used: Delpher open krantenarchief (1.0). Creative Commons Naamsvermelding 4.0, Den Haag, 2019.
https://www.delpher.nl/over-delpher/delpher-open-krantenarchief/wat-zit-er-in-het-delpher-open-krantenarchief#e6bce 

The scripts 'getMetadata', 'getData', and 'makeWordembeddings' were respectively used to:
  1) create an excel metadata file that could be used to filter relevant newspaper articles;
  2) compile all text from relevant articles per year in textfiles;
  3) train word embeddings for timeframes of either 10 or 5 years depending on amount of data available.

One could take inspiration from these scripts to construct word embeddings using the Delpher open newspaper archive.

The word embeddings I created for my thesis research are uploaded to the map 'wordembeddings'. 
The script 'similarityResearch' was used to work with the word embeddings. 
Without the need to construct word embeddings, one could use these for their own research purposes. 

For more information about the methodology and overarching research, please see my thesis (to be uploaded in Utrecht University's thesis repository). 

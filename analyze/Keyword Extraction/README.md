# MIDS W210 - Capstone Project - "Job Fiction/Keyword extract with MAUI"

- Tutorial at https://www.airpair.com/nlp/keyword-extraction-tutorial
- More info at: https://code.google.com/archive/p/maui-indexer/wikis/Resources.wiki
- Based on KEA: http://www.nzdl.org/Kea/description.html

## Training data:
- Only jobs containing "data"
- Keywords retrieved from jobscan.co

## Vocabulary 
- ACM Computer related topics SKOS format
- Extended with keywords from jobscan


## Train the model:
java -Xmx1024m -jar maui-standalone-1.1-SNAPSHOT.jar train -l data/jobscan/train -m data/models/keyword_extraction_model -v ACMTaxonomySkosExtended.rdf -f skos -o 1


## Test the model and generate keywords:
java -Xmx1024m -jar maui-standalone-1.1-SNAPSHOT.jar test -l data/jobscan/test -m data/models/keyword_extraction_model -v ACMTaxonomySkosExtended.rdf -f skos -n 50

## Options:
-Xmx[size]m set the java heap size
-l path to the training/test data
-m path to the model
-v path to the vocabulary
-f format of the vocabulary
-o in training phase, set the minimum occurence of keyphrase candidates
-n in testing phase, set the maximimun number of keyphrases per document 

## TO DO:
- Maybe add more training data


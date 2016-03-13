# MIDS W210 - Capstone Project - "Job Fiction/Keyword extract with MAUI"

- Tutorial at https://www.airpair.com/nlp/keyword-extraction-tutorial
- More info at: https://code.google.com/archive/p/maui-indexer/wikis/Resources.wiki
- Based on KEA: http://www.nzdl.org/Kea/description.html

## Training data:
- Only jobs containing "data"
- Keywords retrieved from jobscan.co

## Train the model:
java -Xmx1024m -jar maui-standalone-1.1-SNAPSHOT.jar train -l data/jobscanManualClean/train -m data/models/keyword_extraction_model -v ACMTaxonomySkos.rdf -f skos -o 1


## Test the model and generate keywords:
java -Xmx1024m -jar maui-standalone-1.1-SNAPSHOT.jar test -l data/jobscanManualClean/ -m data/models/keyword_extraction_model -v ACMTaxonomySkos.rdf -f skos -n 40

## TO DO:
- Add vocabulary to improve accuracy
- Maybe add more training data
- Manually tag keywords


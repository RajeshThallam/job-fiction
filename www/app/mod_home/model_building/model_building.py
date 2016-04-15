#!/usr/bin/python

# read each job post
# tokenize sentences
# remove non-ascii characters and punctuations
# tokenize words
# form bi-grams and tri-grams

import logging
import re
import os

# text pre-processing
import nltk
from nltk.tokenize import sent_tokenize
from nltk.stem.snowball import SnowballStemmer
from string import punctuation, maketrans, translate

# stopwords
import stop_words

# gensim corpus and models
import gensim
from gensim import utils
from gensim import corpora, models, similarities
from gensim.models import Phrases

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.CRITICAL)

DATA_DIR = os.path.join("/home", "rt", "wrk", "jobs", "data")
MODEL_DIR = os.path.join("/home", "rt", "wrk", "jobs", "models")

dictionary = corpora.Dictionary.load(os.path.join(MODEL_DIR, "train.dict"))
corpus = corpora.MmCorpus(os.path.join(MODEL_DIR, "train_jobs.mm"))

# Project to LDA space
NUM_TOPICS = 30
lda = gensim.models.LdaModel(
    corpus=corpus, 
    id2word=dictionary, 
    num_topics=NUM_TOPICS, 
    chunksize=20000, 
    passes=20, 
    alpha='auto',
    eval_every=10,
    minimum_probability=0.005
)

lda.save(os.path.join(MODEL_DIR, "train_model.lda"))

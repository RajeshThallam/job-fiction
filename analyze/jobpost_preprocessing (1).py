#!/usr/bin/python

# read each job post
# tokenize sentences
# remove non-ascii characters and punctuations
# tokenize words
# form bi-grams and tri-grams

import logging
import config as cfg
import re

# text pre-processing
import nltk
from nltk.tokenize import sent_tokenize
from string import punctuation, maketrans, translate

# stopwords
import stop_words

# gensim corpus and models
import gensim
from gensim import corpora
from gensim.models import Phrases


class JobCorpus(object):
    def __init__(self, fname):
        self.fname = fname

        # blackist words to be removed from text
        # combines stopwords from nltk, gensim and stop_words package
        self.en_stopwords = set(
            stop_words.get_stop_words('en') +
            nltk.corpus.stopwords.words("english") +
            list(gensim.parsing.preprocessing.STOPWORDS)
        )

        # keep -, +, # in words
        self.punctuation = re.sub("[-+#.]", " ", punctuation)

        # make translation dictionary converting punctuations to white spaces
        self.translate_dict = maketrans(punctuation, ' '*len(punctuation))

        # replace patterns
        self.invalid_char = re.compile(r'[0-9]|\\~|\`|\@|\$|\%|\^|\& \
                |\*|\(|\)|\_|\=|\[|\]|\\|\<|\<|\>|\?|\/|\;|\\.')
        self.url_pattern = re.compile(
            r'(' +
            # Scheme (HTTP, HTTPS, FTP and SFTP):
            r'(?:(https?|s?ftp):\/\/)?' +
            # www:
            r'(?:www\.)?' +
            r'(' +
            # Host and domain (including ccSLD):
            r'(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\.)+)' +
            # TLD:
            r'([A-Z]{2,6})' +
            # IP Address:
            r'|(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' +
            r')' +
            # Port:
            r'(?::(\d{1,5}))?' +
            # Query path:
            r'(?:(\/\S+)*)' +
            r')',
            re.IGNORECASE
        )

        # generator of documents; one element = list of words
        documents = (self.sentence_stream())

        # best bigrams and trigrams
        logging.warning("collecting ngrams")
        self.ngrams = self.best_ngrams(list(documents))
        logging.warning("completed collecting ngrams")

        logging.warning("building dictionary")
        self.dictionary = gensim.corpora.Dictionary(self.tokenize())
        self.dictionary.compactify()
        self.dictionary.save(cfg.DICTIONARY)
        self.dictionary.save_as_text(cfg.DICTIONARY_TXT)
        logging.warning(self.dictionary)
        logging.warning("completed building dictionary")

    def best_ngrams(self, sentences, threshold=10, min_count=100):
        """
        Extract most salient collocations (bigrams and trigrams) from a stream
        of words. Ignore collocations with frequency lower than `min_count`.

        threshold represents a threshold for forming the phrases (higher means
        fewer phrases). A phrase of words a and b is accepted if
        (cnt(a, b) - min_count) * N / (cnt(a) * cnt(b)) > threshold,
        where N is the total vocabulary size.
        """

        bigrams = Phrases(list(sentences),
                          threshold=threshold,
                          min_count=min_count)
        trigrams = Phrases(bigrams[list(sentences)],
                           threshold=threshold,
                           min_count=min_count)

        return trigrams

    def cleanse_text(self, text):
        clean_text = text

        # remove urls from text
        clean_text = self.url_pattern.sub('', clean_text)

        # remove punctuations and other characters
        clean_text = translate(
            self.invalid_char.sub(' ', clean_text),
            self.translate_dict)

        return clean_text

    def split_words(self, document):
        """
        Break text into sentences and each sentence into a list of single words
        Ignore any token that falls into the stopwords set.
        """
        # use sentence tokenizer sent_tokenize from nltk package
        sentences = sent_tokenize(
            document
            .lower()
            .decode('unicode_escape')
            .encode('ascii', 'ignore')
        )

        for sentence in sentences:
            words = [
                        word for word in gensim.utils.tokenize(
                            self.cleanse_text(sentence))
                        if word not in self.en_stopwords
                    ]
            yield words

    def tokenize(self):
        """
        Break text (string) into a list of unicode tokens.
        The resulting tokens can be longer phrases (collocations) too,
        e.g. `new_york`, `real_estate` etc.
        """
        for document in open(self.fname):
            post = []
            for sentences in self.split_words(document):
                post.extend(self.ngrams[list(sentences)])
            yield post

    def sentence_stream(self):
        for document in open(self.fname):
            post = []
            for sentences in self.split_words(document):
                post.extend(list(sentences))
            yield post

    def __iter__(self):
        for sentence in self.tokenize():
            yield self.dictionary.doc2bow(sentence)


if __name__ == "__main__":
    jobs_corpus = JobCorpus(cfg.TRAIN_FILE)
    corpora.MmCorpus.serialize(cfg.CORPUS_BOW, jobs_corpus)
    corpus = corpora.MmCorpus(cfg.CORPUS_BOW)
    print corpus

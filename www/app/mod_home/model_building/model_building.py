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
from gensim import corpora
from gensim.models import Phrases

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.CRITICAL)

DATA_DIR = os.path.join("/home", "rt", "wrk", "jobs", "data")
MODEL_DIR = os.path.join("/home", "rt", "wrk", "jobs", "models")
SRC_FILE = os.path.join(DATA_DIR, "train_all_job_desc.txt")
CORPUS = os.path.join(MODEL_DIR, "train_all_jobs.mm")
DICT = os.path.join(MODEL_DIR, "train_all.dict")
MODEL_LDA = os.path.join(MODEL_DIR, "train_model_all.lda") 

class JobCorpus(object):
    def __init__(self, fname, stopwords=False, stemming=False):
        self.fname = fname
        self.remove_stopwords = stopwords
        self.stemming = stemming

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
        self.url_pattern = re.compile(r'(' +
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
              r')', re.IGNORECASE)

        # generator of documents; one element = list of words
        documents = (self.stream_sentences())

        # best bigrams and trigrams
        logging.warning("collecting ngrams")
        self.ngrams = self.best_ngrams(list(documents))
        logging.warning("completed collecting ngrams")

        logging.warning("building dictionary")
        self.dictionary = gensim.corpora.Dictionary(self.stream_tokens())
        #self.dictionary.compactify()
        self.dictionary.save(os.path.join(MODEL_DIR, "train.dict"))
        self.dictionary.save_as_text(os.path.join(MODEL_DIR, "train.dict.txt"))
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
        fourgrams = Phrases(trigrams[list(sentences)],
                           threshold=threshold,
                           min_count=min_count)
        fivegrams = Phrases(fourgrams[list(sentences)],
                           threshold=threshold,
                           min_count=min_count)

        return fivegrams

    def cleanse_text(self, text):
        clean_text = text.encode('ascii', 'ignore')

        # remove urls from text
        clean_text = self.url_pattern.sub('', clean_text)

        # remove punctuations and other characters
        clean_text = translate(
            self.invalid_char.sub(' ', clean_text),
            self.translate_dict)

        return clean_text

    def tokenize(self, document):
        """
        Break text into sentences and each sentence into a list of single words
        Ignore any token that falls into the stopwords set.
        """
        # use sentence tokenizer sent_tokenize from nltk package
        sentences = sent_tokenize(utils.to_unicode(document.lower()))

        # create stemmer of class SnowballStemmer
        stemmer = SnowballStemmer("english")

        for sentence in sentences:
            words = [word
                   for word in utils.tokenize(
                    self.cleanse_text(sentence)
                   )]

            if self.remove_stopwords:
                words = [ 
                         word for word in words 
                         if word not in self.en_stopwords
                        ]

            if self.stemming:
                words = [stemmer.stem(t) for t in words]

            yield words

    def stream_tokens(self):
        """
        Break text (string) into a list of unicode tokens.
        The resulting tokens can be longer phrases (collocations) too,
        e.g. `new_york`, `real_estate` etc.
        """
        for document in open(self.fname):
            post = []
            for sentences in self.tokenize(document):
                post.extend(self.ngrams[list(sentences)])
            yield post

    def stream_sentences(self):
        for document in open(self.fname):
            post = []
            for sentences in self.tokenize(document):
                post.extend(list(sentences))
            yield post
            
    def __iter__(self):
        for sentence in self.stream_tokens():
            yield self.dictionary.doc2bow(sentence)


class JobCorpusKeywords(object):
    def __init__(self, fname, stopwords=False, stemming=False):
        self.fname = fname
        self.remove_stopwords = stopwords
        self.stemming = stemming

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
        self.url_pattern = re.compile(r'(' +
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
              r')', re.IGNORECASE)

        logging.warning("building dictionary")
        self.dictionary = gensim.corpora.Dictionary(self.stream_tokens())
        #self.dictionary.compactify()
        self.dictionary.save(os.path.join(MODEL_DIR, "train.dict"))
        self.dictionary.save_as_text(os.path.join(MODEL_DIR, "train.dict.txt"))
        logging.warning(self.dictionary)
        logging.warning("completed building dictionary")

    def cleanse_text(self, text):
        clean_text = text.encode('ascii', 'ignore')

        # remove urls from text
        clean_text = self.url_pattern.sub('', clean_text)

        # remove punctuations and other characters
        clean_text = translate(
            self.invalid_char.sub(' ', clean_text),
            self.translate_dict)

        return clean_text

    def tokenize(self, document):
        """
        Break text into sentences and each sentence into a list of single words
        Ignore any token that falls into the stopwords set.
        """
        # use sentence tokenizer sent_tokenize from nltk package
        sentences = sent_tokenize(utils.to_unicode(document.lower()))

        # create stemmer of class SnowballStemmer
        stemmer = SnowballStemmer("english")

        for sentence in sentences:
            words = [word
                   for word in utils.tokenize(
                    self.cleanse_text(sentence)
                   )]

            if self.remove_stopwords:
                words = [ 
                         word for word in words 
                         if word not in self.en_stopwords
                        ]

            if self.stemming:
                words = [stemmer.stem(t) for t in words]

            yield words

    def stream_tokens(self):
        """
        Break text (string) into a list of unicode tokens.
        The resulting tokens can be longer phrases (collocations) too,
        e.g. `new_york`, `real_estate` etc.
        """
        for document in open(self.fname):
            keywords = [ ]
            post = []
            for sentences in self.tokenize(document):
                post.extend(self.ngrams[list(sentences)])
            yield post

        # stem_keywords = {}
        # stem_dict = {}

        # for word, score in keywords.iteritems():
        #     stemmed = stemmer.stem(word)
        #     stem_keywords[score] = stemmed
        #     stem_dict[stemmed] = word

        # srt_keywords = sorted(stem_keywords.items(),
        #     key=op.itemgetter(0))[:app.config['TOPN_MUST_KEYWORDS']]
        
        # top_keywords = {stem_dict[k]: v for v, k in srt_keywords}

        # return top_keywords

    def stream_sentences(self):
        for document in open(self.fname):
            post = []
            for sentences in self.tokenize(document):
                post.extend(list(sentences))
            yield post
            
    def __iter__(self):
        for sentence in self.stream_tokens():
            yield self.dictionary.doc2bow(sentence)

if __name__ == "__main__":
    logging.warning("building corpus")
    jobs_corpus = JobCorpus(SRC_FILE, stopwords=True, stemming=False)
    corpora.MmCorpus.serialize(CORPUS, jobs_corpus)
    dictionary = corpora.Dictionary.load(DICT)
    corpus = corpora.MmCorpus(CORPUS)
    logging.warning("corpus build completed!!")

    # Project to LDA space
    logging.warning("running lda")
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
    lda.save(MODEL_LDA)
    logging.warning("lda completed")
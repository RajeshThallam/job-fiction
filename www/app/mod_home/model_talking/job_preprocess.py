from string import punctuation, maketrans, translate
import nltk
import gensim
from gensim import utils
from gensim.corpora import Dictionary
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import sent_tokenize
import stop_words
import re


class JobPreprocess(object):
    def __init__(self, text, dictionary, stopwords=False, stemming=False):
        self.text = text
        self.remove_stopwords = stopwords
        self.stemming = stemming
        self.dictionary = Dictionary.load(dictionary)

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
            words = [
                    word for word in
                    utils.tokenize(self.cleanse_text(sentence))
                    ]

            if self.remove_stopwords:
                words = [
                        word for word in words
                        if word not in self.en_stopwords
                        ]

            if self.stemming:
                words = [stemmer.stem(t) for t in words]

            yield words

    def stream_sentences(self):
        for document in self.text:
            post = []
            for sentences in self.tokenize(document):
                post.extend(list(sentences))
            yield post

    def __iter__(self):
        for sentence in self.stream_sentences():
            yield self.dictionary.doc2bow(sentence)

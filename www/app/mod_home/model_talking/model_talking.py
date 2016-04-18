# gensim corpus and models

from gensim import corpora
from gensim.similarities import Similarity
from gensim.corpora import Dictionary
from gensim.models.ldamodel import LdaModel
import job_preprocess as jp
import operator as op
from app import app
import json

class ModelTalking(object):
    def __init__(self):
        self.dictionary = Dictionary.load(app.config['RCMDR_DICT'])
        self.corpus = corpora.MmCorpus(app.config['RCMDR_CORPUS'])
        self.model = LdaModel.load(app.config['RCMDR_LDA_MODEL'])
        self.index = Similarity.load(app.config['RCMDR_LDA_INDEX'])
        self.job_labels = { 
            int(k):v 
            for k, v in (line.split("=") 
                for line in open(app.config['RCMDR_JOB_LABELS'])
                .read().strip().split('\n')) 
            }

    def sort_dict(self, dict, orderby, reversed=False):
        srt_list = sorted(dict.items(), key=op.itemgetter(orderby), reverse=reversed)
        srt_dict = [(k, str(v)) for k, v in srt_list]
        return srt_dict

    def get_job_recommendations(self, query):
        results = {}

        if 'all_jobs' in query:
            # read all job descriptions
            job_desc = query['all_jobs']

            # clean job descriptions
            query_text = jp.JobPreprocess(
                job_desc, 
                app.config['RCMDR_DICT'], 
                stopwords=True)

            # get bag-of-words for the job descriptions
            query_bow = [bow for bow in query_text]

            # get probable job topics fitting the model
            query_topics = self.model[query_bow]

            # find similar jobs in the indexed jobs
            sim_jobs = self.index[query_topics]

            n = app.config['TOPN_RCMND_JOBS']
            srt_sim_jobs = []
            for sim_job in sim_jobs:
                s = sorted(
                        enumerate(sim_job),
                        key=lambda item: -item[1])[:n]
                srt_sim_jobs.extend(s)

            sim_jobs = sorted(srt_sim_jobs, key=lambda item: -item[1])[:n]

            # get job ids of the recommended results
            all_job_ids = [
                line for line in 
                open(app.config['TRAIN_DOC_IDX']).read().strip().split('\n')
            ]

            sim_job_ids = {}
            for job_id, score in sim_jobs:
                sim_job_ids[all_job_ids[job_id]] = score

            # return results
            results = self.sort_dict(sim_job_ids, 1, True)
            return results
        else:
            return json.dumps({'error': 'invalid_query_string'})
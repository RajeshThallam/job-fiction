# gensim corpus and models

from gensim import corpora
from gensim.similarities import Similarity
from gensim.corpora import Dictionary
from gensim.models.ldamodel import LdaModel
from gensim.models.lsimodel import LsiModel
from gensim.models import TfidfModel
import job_preprocess as jp
import operator as op
import pandas as pd
from app import app
import json

"""
#pre-built files
#training doc-wise topic distribution
fjobtopics = open(os.path.join(MODEL_DIR, "train_jobs_topics.csv"), 'wb')
for doc_id in range(len(corpus)):
    docbow = corpus[doc_id]
    doc_topics = lda.get_document_topics(docbow)
    for topic_id, topic_prob in doc_topics:
        fjobtopics.write("%d\t%d\t%.3f\n" % (doc_id, topic_id, topic_prob))
fjobtopics.close()
"""


class ModelTalking(object):
    def __init__(self):
        self.dictionary = Dictionary.load(app.config['RCMDR_DICT'])
        self.corpus = corpora.MmCorpus(app.config['RCMDR_CORPUS'])
        self.tfidf = TfidfModel.load(app.config['RCMDR_TFIDF_MODEL'])
        self.lda_model = LdaModel.load(app.config['RCMDR_LDA_MODEL'])
        self.lsi_model = LsiModel.load(app.config['RCMDR_LSI_MODEL'])
        self.lda_index = Similarity.load(app.config['RCMDR_LDA_INDEX'])
        self.lsi_index = Similarity.load(app.config['RCMDR_LSI_INDEX'])
        self.job_labels = { 
            int(k):v 
            for k, v in (line.split("=") 
                for line in open(app.config['RCMDR_JOB_LABELS'])
                .read().strip().split('\n')) 
            }

    # sorting dictionary based on list of columns passed
    def sort_dict(self, dict, orderby, top_n=0, reversed=False):
        srt_list = sorted(dict.items(), key=op.itemgetter(orderby), reverse=reversed)[:top_n]
        srt_dict = [(k, str(v)) for k, v in srt_list]
        return srt_dict

    # sorting similarity lists
    def sort_similarities(self, sims):
        srt_sims = []
        sim_jobs = {}

        # append lists
        for sim in sims:
            s = sorted(enumerate(sim), key=lambda item: item[1], reverse=True)
            srt_sims.extend(s)
            #srt_sims = [item for sim in sims for item in sims]
        
        # find max scoring job
        for key, value in srt_sims:
            if sim_jobs.get(key) < value:  # d.get(key) returns None if the key doesn't exist
                sim_jobs[key] = value      # None < float('-inf'), so it'll work

        return sim_jobs

    # sorting query topics by topic probabilities
    def sort_query_topics(self, query_topics, top_n=0):
        all_query_topics = []
        dict_query_topics = {}

        # append lists
        all_query_topics = [item for query_topic in query_topics for item in query_topic]
        
        # find max scoring job
        for key, value in all_query_topics:
            if dict_query_topics.get(key) < value:  # d.get(key) returns None if the key doesn't exist
                dict_query_topics[key] = value      # None < float('-inf'), so it'll work

        list_query_topics = [ topic for topic, score in self.sort_dict(dict_query_topics, 1, top_n, reversed=True) ]
        return list_query_topics

    # get job recommendation results
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
            
            # get tf-idf for the job descriptions against the training corpus
            query_tfidf = self.tfidf[query_bow]

            # get probable job topics fitting the model
            query_topics = self.lda_model[query_bow]
            # get top 3 topics where user job descriptions belong to
            #top_query_topics = sorted(query_topics, key=lambda t: t[1], reverse = True)[:3]
            top_query_topics = self.sort_query_topics(query_topics, 3)
            print query_topics
            print top_query_topics

            # get trained job posts document and topic distribution
            q_tpc_df = pd.read_csv(
                app.config['RCMDR_TRN_TOPIC_DIST'],
                sep="\t",
                names=["doc_id", "topic_id", "topic_prob"],
                skiprows=0)

            # get all jobs where under top user query topics
            q_doc_tpc_idx = q_tpc_df[q_tpc_df['topic_id'].isin(top_query_topics)]

            # find similar jobs in the indexed jobs based on lsi
            lsi_jobs_sims = self.lsi_index[self.lsi_model[query_tfidf]]
            lsi_sim_jobs = self.sort_similarities(lsi_jobs_sims)

            # find similar jobs in the indexed jobs based on lsi
            lda_jobs_sims = self.lda_index[query_topics]
            lda_sim_jobs = self.sort_similarities(lda_jobs_sims)

            # get job ids of the recommended results
            all_job_ids = [
                line for line in 
                open(app.config['TRAIN_DOC_IDX']).read().strip().split('\n')
            ]

            sim_job_ids = {}
            for row in q_doc_tpc_idx.itertuples():
                job_id = row[1]
                topic_relevance_score = row[3] 
                lda_relevance_score = lda_sim_jobs.get(job_id, 1.0)
                lsi_relevance_score = lsi_sim_jobs.get(job_id, 1.0)
                relevance_score = topic_relevance_score * lda_relevance_score * lsi_relevance_score
                sim_job_ids[all_job_ids[job_id]] =  relevance_score

            # return results
            n = app.config['TOPN_RCMND_JOBS']
            results = self.sort_dict(sim_job_ids, 1, n, True)
            return results
        else:
            return json.dumps({'error': 'invalid_query_string'})
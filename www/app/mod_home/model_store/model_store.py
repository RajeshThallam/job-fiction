#!/usr/bin/env python
# encoding: utf-8

# This script stores model results for data science related jobs to 
# elasticsearch store that will be used for retrieving recommended results.
# Master job store on MongoDB stores all the jobs. However for this script we
# are interested only in data science related jobs. A pre-processor script 
# filters non data science related jobs based on exclusion and inclusion 
# patterns.

import config as cfg
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from hashlib import sha1
from datetime import datetime as dt
import math
import transform_doc2bow as d2b
from gensim.models.ldamodel import LdaModel
import pandas as pd
import sys

class ModelStore(object):
    def __init__(self, jobdesc_fname, jobtitle_fname):
        self.es = Elasticsearch([{'host': cfg.ES_HOST, 'port': 9200}])
        self.model = LdaModel.load(cfg.RCMDR_LDA_MODEL)
        self.job_labels = { 
            int(k):v 
            for k, v in (line.split("=") 
                for line in open(cfg.RCMDR_JOB_LABELS)
                .read().strip().split('\n')) 
            }
        self.jobdesc_fname = jobdesc_fname
        self.jobtitle_fname = jobtitle_fname

    def get_doc_topic_details(self):
        # get job title details
        col_names = [
                "doc_id", "job_title", "company", "url", "full_location", 
                "long", "lat", "post_date"]
        job_df = pd.read_csv(self.jobtitle_fname, sep="|",
                   names=col_names,
                   skiprows=0)
        job_df.fillna("", inplace=True)
        job_df["topic_labels"] = ""

        # get topic labels
        doc2bow = d2b.JobPreprocess(
            self.jobdesc_fname, cfg.RCMDR_DICT, stopwords=True)

        # get probable job topics fitting the model
        doc_topics = self.model[doc2bow]

        # get top N topics
        n = cfg.TOPN_JOB_CLASSES

        topics_labels = []
        for doc_id, doc_topic in enumerate(doc_topics):
            topics = sorted(doc_topic, key=lambda t: t[1], reverse = True)[:n]

            # get labels for the topics
            topic_labels = []
            for topic_id, score in topics:
                label = self.job_labels[topic_id]
                topic_labels.append(dict({
                    'topic_id': topic_id, 
                    'label': label, 
                    'score': score}))

            topics_labels.append(topic_labels)

        job_df['topic_labels'] = topics_labels

        print "Formed labels and details " + str(len(job_df))
        return job_df

    def store_results(self):
        print "Getting topic labels"
        job_df = self.get_doc_topic_details()

        # ignore 400 cause by IndexAlreadyExistsException when creating an index
        es_index = cfg.ES_IDX_RESULT
        es_index_type = cfg.ES_IDX_TYPE_RESULT
        es_index_mapping = {
            'results': {
                'properties': {
                    'job_title': {
                        'type': 'string',
                        'index': 'not_analyzed',
                        'null_value': 'NA'
                    },
                    'company': {
                        'type': 'string',
                        'index': 'not_analyzed',
                        'null_value': 'NA'
                    },
                    'url': {
                        'type': 'string',
                        'index': 'not_analyzed',
                        'null_value': 'NA'
                    },
                    'full_location': {'type': 'string', 'index': 'not_analyzed', 'null_value': 'NA'}, 
                    'location': {'type': 'geo_point'},
                    'posted_date': {'type': 'date'},
                    'job_class': {'type' : 'nested'},
                    'keywords': {'type' : 'nested'}
                }
            }
        }

        self.es.indices.create(
                index=es_index,
                body={'settings': {'mappings': es_index_mapping}},
                ignore=400)

        pages = []
        idx = 0

        for row in job_df.itertuples():
            idx += 1

            newpage = {
                '_index': es_index,
                '_type': es_index_type,
                '_id': row[1],
                '_source': {
                    'job_title': row[2],
                    'company': row[3],
                    'url': row[4],
                    'full_location': row[5],
                    'location': row[7] + "," + row[6],
                    'posted_date': row[8],
                    'job_class': row[9],
                    'keywords': {}
                    }
                }
            pages.append(newpage)

            if (idx % 1000 == 0):
                helpers.bulk(self.es, pages, True)
                pages = []

        helpers.bulk(self.es, pages, True)
        return 0

if __name__ == "__main__":
    jobdesc_fname = sys.argv[1]
    jobtitle_fname = sys.argv[2]

    es_results = ModelStore(jobdesc_fname, jobtitle_fname)
    return_code = es_results.store_results()

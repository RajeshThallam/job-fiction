#!/usr/bin/env python
# encoding: utf-8

# This script stores model results for data science related jobs to
# elasticsearch store that will be used for retrieving recommended results.
# Master job store on MongoDB stores all the jobs. However for this script we
# are interested only in data science related jobs. A pre-processor script
# filters non data science related jobs based on exclusion and inclusion
# patterns.

from app.mod_home.extract_keywords import extract_keywords as kw
from gensim.models.ldamodel import LdaModel
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import transform_doc2bow as d2b
#import config as cfg
from app import app
import pandas as pd
import json
import sys


class ModelStore(object):
    def __init__(self, jobdesc_fname, jobtitle_fname):
        self.es = Elasticsearch([{'host': app.config['ES_HOST'], 'port': 9200}])
        self.model = LdaModel.load(app.config['RCMDR_LDA_MODEL'])
        self.job_labels = {
            int(k):v
            for k, v in (line.split("=") for line in open(app.config['RCMDR_JOB_LABELS'])
                    .read().strip().split('\n'))
            }
        self.jobdesc_fname = jobdesc_fname
        self.jobtitle_fname = jobtitle_fname

    def status(self, status):
        with open(os.path.join(app.config['LOG_PATH'], status), 'w') as stsFile:
            stsFile.write(status)
        stsFile.close()

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
        job_df["keywords"] = ""

        # get topic labels
        doc2bow = d2b.JobPreprocess(
            self.jobdesc_fname, app.config['RCMDR_DICT'], stopwords=True)

        # get probable job topics fitting the model
        doc_topics = self.model[doc2bow]


        job_desc_text = { str(doc_id):line
            for doc_id, line in enumerate(open(self.jobdesc_fname)
            .read().strip().split('\n'))
        }

        self.status('Keyword_extraction_starts')
        print "Extracting keywords"
        maui = kw.ExtractKeywords()
        keywords = json.loads(maui.find_keywords(job_desc_text))
        print "Keyword extraction completed!!"
        self.status('Keyword_extraction_completed')

        # get top N topics
        n = app.config['TOPN_JOB_CLASSES']

        topics_labels = []
        docs_keywords = []

        self.status('preparing_data_frame')
        print "Preparing jobs data frame"
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

            docs_keywords.append(keywords[str(doc_id)])
            topics_labels.append(topic_labels)

        self.status('updated_data_frame')
        print "Updating jobs data frame"
        job_df['topic_labels'] = topics_labels
        job_df['keywords'] = docs_keywords

        print "Formed labels and details " + str(len(job_df))
        self.status('labels_formed')
        return job_df

    def store_results(self):
        print "Getting topic labels"
        job_df = self.get_doc_topic_details()

        self.status('elasticsearch_bulk_load_starts')
        print "Elasticsearch bulk load starts"

        # ignore 400 cause by IndexAlreadyExistsException when creating an index
        es_index = app.config['ES_IDX_RESULT']
        es_index_type = app.config['ES_IDX_TYPE_RESULT']
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

            if idx == 1:
                print row[10]

            newpage = {
                '_index': es_index,
                '_type': es_index_type,
                '_id': row[1],
                '_source': {
                    'job_title': row[2].decode('latin1'),
                    'company': row[3].decode('latin1'),
                    'url': row[4],
                    'full_location': row[5].decode('latin1'),
                    'location': str(row[7]) + "," + str(row[6]),
                    'posted_date': row[8],
                    'job_class': row[9],
                    'keywords': row[10]
                    }
                }
            pages.append(newpage)

            if (idx % 1000 == 0):
                print "Inserting record #" + str(idx) + "into Elasticsearch"
                helpers.bulk(self.es, pages, True)
                pages = []

        helpers.bulk(self.es, pages, True)
        print "Elasticsearch bulk load completed!!"
        self.status('elasticsearch_bulk_load_completed')
        return 0

if __name__ == "__main__":
    jobdesc_fname = sys.argv[1]
    jobtitle_fname = sys.argv[2]

    es_results = ModelStore(jobdesc_fname, jobtitle_fname)
    return_code = es_results.store_results()

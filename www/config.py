# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database connections
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Secret key for signing cookies
SECRET_KEY = "j0bf1ct10n"
PERMANENT_SESSION_LIFETIME = 100000000

# Keyword Extraction Variables
EXTRACT_KEYWORDS_DIR = os.path.join(BASE_DIR, "app", "mod_home", "extract_keywords")
MAUI_HOME_PATH = os.path.join(EXTRACT_KEYWORDS_DIR, "maui-standalone-1.1-SNAPSHOT.jar")
MODEL_KEYWORDS_DIR = os.path.join(EXTRACT_KEYWORDS_DIR, "models")
MODEL_KEYWORDS_ID = "keyword_extraction_model"
ACM_EXTENDED_DICT = os.path.join(EXTRACT_KEYWORDS_DIR, "dict", "ACMTaxonomySkosExtended.rdf")
ACM_DICT = os.path.join(EXTRACT_KEYWORDS_DIR, "dict", "ACMTaxonomySkos.rdf")
ACM_TAXONOMY_TEXT = os.path.join(EXTRACT_KEYWORDS_DIR, "dict", "ACMTaxonomyFlat.txt")
ACM_TAXONOMY_PATH = os.path.join(EXTRACT_KEYWORDS_DIR, "dict", "ACMTaxonomyPaths.txt")
TOPN_MUST_KEYWORDS = 20
TOPN_NICE_KEYWORDS = 20

# Recommender Variables
RCMDR_DIR = os.path.join(BASE_DIR, "app", "mod_home", "model_talking")
RCMDR_MODEL_DIR = os.path.join(RCMDR_DIR, "models")
RCMDR_DICT_DIR = os.path.join(RCMDR_DIR, "dict")
RCMDR_LDA_MODEL = os.path.join(RCMDR_MODEL_DIR, 'lda_30_topics.lda')
RCMDR_DICT = os.path.join(RCMDR_DICT_DIR, 'train_no_stem.dict')
RCMDR_CORPUS = os.path.join(RCMDR_DICT_DIR, 'train_no_stem.mm')
RCMDR_LDA_INDEX = os.path.join(RCMDR_MODEL_DIR, 'lda_30_topics.idx')
RCMDR_JOB_LABELS = os.path.join(RCMDR_DICT_DIR, 'job_labels.dict')
TRAIN_DOC_IDX = os.path.join(RCMDR_MODEL_DIR, 'train_documents.idx')
TOPN_JOB_CLASSES = 5
TOPN_RCMND_JOBS = 100

# Model Store Variables
STORE_JOBDESC_FILE = os.path.join("/home/rt", "wrk", "jobs", "data", "train.txt")
STORE_JOBTITLE_FILE = os.path.join("/home/rt", "wrk", "jobs", "data", "get_train_results.sorted.txt")
STORE_MODEL_FILE = os.path.join("/home/rt", "wrk", "jobs", "data", "model_results.txt")
ES_HOST = "50.97.254.20"
ES_IDX_RESULT = 'jobfiction'
ES_IDX_TYPE_RESULT = 'results'
LOG_PATH = os.path.join("/home/rt", "wrk", "jobs", "data")
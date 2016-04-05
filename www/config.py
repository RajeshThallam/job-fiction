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

# Python scripts launched by app
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
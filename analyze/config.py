import os

DATA_DIR = os.path.join("/home", "rt", "wrk", "jobs", "data")
MODEL_DIR = os.path.join("/home", "rt", "wrk", "jobs", "models")
TRAIN_FILE = os.path.join(DATA_DIR, "train.txt")
CORPUS_BOW = os.path.join(MODEL_DIR, "train_jobs.mm")
DICTIONARY = os.path.join(MODEL_DIR, "train.dict")
DICTIONARY_TXT = os.path.join(MODEL_DIR, "train.dict.txt")
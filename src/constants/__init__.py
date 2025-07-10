import os
from datetime import datetime

# for MongoDB connection
DATABASE_NAME = 'Proj1'
COLLECTION_NAME = 'Proj1.data'
MONGODB_URL_KEY = "MONGODB_URL"

# HOW TO SET ENVIRONMENT VARIABLE URL
# $env:MONGODB_URL = 'mongodb+srv://USERNAME:<PASSWORD>'

PIPELINE_NAME: str = ""
ARTIFACT_DIR = "artifact"

MODEL_FILE_NAME = "model.pkl"

TARGET_COLUMN = "Response"
CURRENT_YEAR = datetime.today().year
PREPROCESSING_OBJECT_FILE_NAME = "preprocessing.pkl"

FILE_NAME: str = "data.csv"
TRAIN_FILE_NAME: str = "train.csv"
TEST_FILE_NAME:str = "test.csv"
SCHEMA_FILE_PATH = os.path.join('config','schema.yaml')


# AWS PENDING

'''
Data Ingestion related constant start with DATA_INGESTION VAR NAME
'''
DATA_INGESTION_COLLECTION_NAME: str = "Proj1.data"
DATA_INGESTION_DIR_NAME: str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_store"
DATA_INGESTION_INGESTED_DIR: str = "ingeseted"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO: float = 0.25


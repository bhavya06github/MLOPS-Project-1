import sys
import pandas as pd
import numpy as np
from typing import Optional

from src.configuration.mongodb_connection import MongoDBClient
from src.constants import DATABASE_NAME
from src.exception import MyException

class Proj1Data:
    '''
    A class to export MongoDB records as a pandas dataframe
    '''

    def __init__(self) -> None:
        ''' Initializes the MongoDB client '''
        try:
            # Create a MongoDB client using the default database name
            self.mongo_client = MongoDBClient(database_name= DATABASE_NAME)
        except Exception as e:
            # If there is any error during initialization, raise a custom exception
            raise MyException(e,sys)
        
    def export_collection_as_dataframe(self, collection_name:str, database_name:Optional[str] = None) -> pd.DataFrame:
        '''
        Fetches all records from the specified MongoDB collection and returns them as a pandas DataFrame.
        If database_name is not provided, uses the default database.
        '''
        try:
            # Select the collection from the specified or default database
            if database_name is None:
                print(f"Using default database: {self.mongo_client.database.name}")
                collection = self.mongo_client.database[collection_name]
            else:
                print(f"Using database: {database_name}")
                db_client = getattr(self.mongo_client, "client", None)
                if db_client is None:
                    raise MyException(Exception("MongoDB client is not initialized properly."), sys)
                db = db_client[database_name]
                collection = db[collection_name]
            print(f"Using collection: {collection_name}")
            print('fetching data from mongoDB')
            # Fetch all documents from the collection and convert to DataFrame
            df = pd.DataFrame(list(collection.find()))
            print(f"data fetched with len: {len(df)}")

            # Remove 'id' column if it exists
            if 'id' in df.columns.to_list():
                df = df.drop(columns=['id'], axis=1)
            # Replace any 'na' string values with np.nan
            df.replace({'na':np.nan}, inplace=True)
            return df
        
        except Exception as e:
            # Raise a custom exception if anything goes wrong
            raise MyException(e,sys)
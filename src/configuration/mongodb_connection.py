import os
import sys
import pymongo
import certifi

from src.exception import MyException
from src.logger import  logging #configure_logger # tha toh logging but usme error aayega
from src.constants import DATABASE_NAME, MONGODB_URL_KEY

# This gets the path to the certificate authority file.
# It's needed so MongoDB doesn't complain about security stuff (SSL).
ca = certifi.where()

class MongoDBClient:
    # This is a class variable to hold the MongoDB client connection.
    client = None

    def __init__(self, database_name:str = DATABASE_NAME) -> None:
        # This function runs when you make a new MongoDBClient object.
        try:
            # If we haven't connected to MongoDB yet, do it now.
            if MongoDBClient.client is None:
                # Get the MongoDB URL from environment variables.
                mongo_db_url = os.getenv(MONGODB_URL_KEY)
                if mongo_db_url is None:
                    # If the URL isn't set, throw an error.
                    raise Exception("Environment variable '{MONGODB_URL_KEY} is not set.")
                # Actually connect to MongoDB using the URL and certificate.
                MongoDBClient.client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
            
            # Save the client and database info for this object.
            self.client = MongoDBClient.client
            self.database = self.client[database_name] # type: ignore
            self.database_name = database_name
            # Log that the connection worked.
            logging.info("MongoDB connection successful.")

        except Exception as e:
            # If anything goes wrong, raise a custom exception with details.
            raise MyException(e,sys)
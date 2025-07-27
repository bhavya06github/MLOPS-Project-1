import sys
import numpy as np
import pandas as pd
from imblearn.combine import SMOTEENN
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.compose import ColumnTransformer

from src.constants import TARGET_COLUMN, SCHEMA_FILE_PATH, CURRENT_YEAR
from src.entity.config_entity import DataTransformationConfig
from src.entity.artifact_entity import DataTransformationArtifact, DataIngestionArtifact, DataValidationArtifact
from src.exception import MyException
from src.logger import logging
from src.utils.main_utils import save_object, save_numpy_array_data, read_yaml_file

class DataTransformation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_artifact: DataValidationArtifact,
                 data_transformation_config: DataTransformationConfig) :
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_artifact = data_validation_artifact
            self.data_transformation_config = data_transformation_config
            self.schema_config = read_yaml_file(file_path=SCHEMA_FILE_PATH)

        except Exception as e:
            raise MyException(e,sys) from e
        
    @staticmethod
    def read_data(file_path)-> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise MyException(e,sys) from e
        
    
    def get_data_transformer_object(self) -> Pipeline:
        """
        Creates and returns a data transformer object for the data,
        including gender mapping, dummy variable creation, column renaming,
        feature scaling and type adjustments.
        """
        logging.info("Entered get_data_transformer_object method of DataTransformation class")

        try:
            # Initialize transformers
            numeric_transformer = StandardScaler()
            min_max_scaler = MinMaxScaler()
            logging.info("Transformers Initialized: StandardScaler-MinMaxScaler")

            # Load schema configurations 
            num_features = self.schema_config['num_features']
            mm_columns = self.schema_config['mm_columns']
            logging.info("Cols loaded from schema.")

            # Creating preprocessor pipeline
            preprocessor = ColumnTransformer(
                transformers=[
                    ("StandardScaler", numeric_transformer, num_features),
                    ("MinMaxScaler", min_max_scaler, mm_columns)
                ],
                remainder='passthrough' # leaves other columns as they are
            )

            # wrapping things into a single pipeline
            final_pipeline = Pipeline(steps=[("Preprocessor",preprocessor)])
            logging.info("Final Pipeline Ready!!")
            logging.info("Exited get_data_transformer_object method of DataTransformation class")
            return final_pipeline
        except Exception as e:
            logging.exception("Exception occurred in get_data_transformer_object method of DataTransformation class")
            raise MyException(e,sys) from e
        
    
    def map_gender_column(self, df):
        """
        Map gender column to 0 for FEMALE and 1 for MALE
        """
        logging.info("Mapping 'Gender' column to binary values")
        df['Gender'] = df['Gender'].map({'Female':0, 'Male':1}).astype(int)
        return df
    
    def create_dummy_columns(self, df):
        """
        Create dummy variables for cateforical features.
        """
        logging.info("Creating dummy varuable for categorical features")
        df = pd.get_dummies(df, drop_first = True)
        return df
    
    def  rename_columns(self, df):
        """
        Rename specific columns and ensure integer types for dummy columns
        """
        logging.info("Renaming specific columns and casting to int")
        df = df.rename(columns= {
            "Vehicle_Age_< 1 Year" : "Vehicle_Age_lt_1_Year",
            "Vehicle_Age_> 2 Years" : "Vehicle_Age_gt_2_Years"
        })
        for col in ["Vehicle_Age_lt_1_Year", "Vehicle_Age_gt_2_Years", "Vehicle_Damage_Yes"]:
            if col in df.columns:
                df[col] = df[col].astype('int')
                return df
            
    def drop_id_columns(self, df):
        """
        Drop the 'id' column if it exists
        """
        logging.info("Dropping 'id' column")
        drop_col = self.schema_config['drop_columns']
        if drop_col in df.columns:
            df = df.drop(drop_col, axis= 1)
            return df 
        
    
    def initiate_data_transformation(self)-> DataTransformationArtifact:
        """
        Initiates the data transformation component for the pipeline
        """
        try:
            logging.info("Data Transformation Started !!!!!")
            if not self.data_validation_artifact.validation_status:
                raise Exception(self.data_validation_artifact.errror_message)
            train_df = self.read_data(file_path=self.data_ingestion_artifact.trained_file_path)
            test_df = self.read_data(file_path=self.data_ingestion_artifact.test_file_path)
            logging.info("Train-Test data loaded")

            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN],axis=1)
            target_feature_train_df = train_df[TARGET_COLUMN]
            
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN],axis=1)
            target_feature_test_df = test_df[TARGET_COLUMN]

            input_feature_train_df = self.map_gender_column(input_feature_train_df)
            input_feature_train_df = self.drop_id_columns(input_feature_train_df)
            input_feature_train_df = self.create_dummy_columns(input_feature_train_df)
            input_feature_train_df = self.rename_columns(input_feature_train_df)

            input_feature_test_df = self.map_gender_column(input_feature_test_df)
            input_feature_test_df = self.drop_id_columns(input_feature_test_df)
            input_feature_test_df = self.create_dummy_columns(input_feature_test_df)
            input_feature_test_df = self.rename_columns(input_feature_test_df)
            logging.info("Custom transformations applied to train and test data")

            logging.info("Starting data transformation")
            preprocessor = self.get_data_transformer_object()
            logging.info("Got the preprocessor object")
            
            logging.info("Initializing transformation for Training-data")
            input_feature_train_arr = preprocessor.fit_transform(input_feature_train_df) # pyright: ignore[reportArgumentType]
            logging.info("Initializing transformation for test-data")
            input_feature_test_arr = preprocessor.transform(input_feature_test_df) # pyright: ignore[reportArgumentType]
            logging.info("Transformation done end to end to train-test df.")

            logging.info("Applying SMOTEENN for handling imbalanced dataset.")
            smt = SMOTEENN(sampling_strategy="minority")
            resampled_train = smt.fit_resample(input_feature_train_arr, target_feature_train_df)
            input_feature_train_final, target_feature_train_final = resampled_train[0], resampled_train[1]
            resampled_test = smt.fit_resample(input_feature_test_arr, target_feature_test_df)
            input_feature_test_final, target_feature_test_final = resampled_test[0], resampled_test[1]
            logging.info("SMOTEEN applied to train-test df.")

            train_arr = np.c_[input_feature_train_final, np.array(target_feature_train_final)]
            test_arr = np.c_[input_feature_test_final, np.array(target_feature_test_final)]
            logging.info("Feature-target concatenation done for train-test df.")
            save_object(self.data_transformation_config.transformed_object_file_path, preprocessor)
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array=train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array=test_arr)
            logging.info("Saving transformation object and transformed files.")

            logging.info("Data transformation completed successfully")
            return DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )
        
        except Exception as e:
            raise MyException(e,sys) from e
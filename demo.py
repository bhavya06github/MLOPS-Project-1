# from src.logger import logging
# from src.exception import MyException
# import sys

# try: 
#     a = 1 +'s'
# except Exception as e:
#     logging.info(e)
#     raise MyException(e,sys) from e


from src.pipeline.training_pipeline import TrainPipeline
pipeline = TrainPipeline()
pipeline.run_pipeline()
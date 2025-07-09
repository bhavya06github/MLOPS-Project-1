import sys
import logging

def error_message_detail(error: Exception, error_detail) -> str:
    # Extract traceback object from error_detail
    _, _, exc_tb = error_detail.exc_info()

    # Get the file name where the exception occurred
    file_name = exc_tb.tb_frame.f_code.co_filename
    
    # Get the line number where the exception occurred
    line_number = exc_tb.tb_lineno

    # Format the error message with file name, line number, and error details
    error_message = f"Error occurred in python script: [{file_name}] at line number [{line_number}]: {str(error)}"

    # Log the error message
    logging.error(error_message)

    return error_message

# Custom exception class for handling errors with detailed messages
class MyException(Exception):

    def __init__(self, error_message: Exception, error_detail):
        # Initialize the base Exception class
        super().__init__(error_message)

        # Generate and store the detailed error message
        self.error_message = error_message_detail(error_message, error_detail)

    def __str__(self) -> str:
        # Return the detailed error message when the exception is printed
        return self.error_message
    

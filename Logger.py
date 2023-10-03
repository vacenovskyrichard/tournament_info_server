import logging

class CustomLogger:
    logger: logging.Logger
    file_handler: logging.FileHandler
    stdout_handler: logging.StreamHandler
    def __init__(self):
        # Remove the default StreamHandler from the root logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

        # Create a logger
        self.logger = logging.getLogger('main_logger')
        self.logger.setLevel(logging.INFO)

        # Create a formatter for log messages
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Create a handler for writing log messages to a file
        self.file_handler = logging.FileHandler('./logging/main.log')
        self.file_handler.setLevel(logging.INFO)
        self.file_handler.setFormatter(formatter)

        # Create a handler for writing log messages to stdout
        self.stdout_handler = logging.StreamHandler()
        self.stdout_handler.setLevel(logging.INFO) 
        self.stdout_handler.setFormatter(formatter)

        # Add the handlers to the logger
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.stdout_handler)
        
    def change_formater(self,format):
        new_formatter = logging.Formatter(format)
        self.stdout_handler.setFormatter(new_formatter)
        self.file_handler.setFormatter(new_formatter)
        
    def get_current_formater(self):
        return self.logger.handlers[0].formatter._fmt
    
    def info_message_only(self,message:str):
        current_formater = self.get_current_formater()
        self.change_formater("%(message)s")
        self.logger.info(message)
        self.change_formater(current_formater)
        
    def log_delimiter(self):
        self.info_message_only("---------------------------------------------------------------------")
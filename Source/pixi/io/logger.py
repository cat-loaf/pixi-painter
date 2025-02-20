import logging
import sys

class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self, name: str = 'default', level: int = logging.INFO, output: str = 'stdout'):
        if not hasattr(self, 'initialized'):
            self.logger = logging.getLogger(name)
            self.logger.setLevel(level)
            self._setup_handler(output)
            self.initialized = True

    def _setup_handler(self, output: str):
        if output == 'stdout':
            handler = logging.StreamHandler(sys.stdout)
        elif output == 'stderr':
            handler = logging.StreamHandler(sys.stderr)
        else:
            handler = logging.FileHandler(output)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)
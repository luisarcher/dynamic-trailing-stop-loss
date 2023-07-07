import logging
import time
import yaml
import os
import sys


project_root_path = os.path.normpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
)
sys.path.insert(1, os.path.join(project_root_path, 'config'))


class Config:
    """Class representing a configuration object."""

    DEFAULT_CONFIG_FILENAME = 'config.yml'
    __instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensures the class has only one instance by returning the existing instance if it exists or creating a new one.
        """
        if cls.__instance is None:
            cls.__instance = super(Config, cls).__new__(cls)
        return cls.__instance

    def __init__(self, config_filename=None):
        """Initialize the Config object.

        Args:
            config_filename (str, optional): Filename of the configuration file.
                If not provided, the default configuration filename will be used.
        """
        if config_filename is None:
            config_filename = self.DEFAULT_CONFIG_FILENAME
        self.config = self.load_config(project_root_path + '/config/' + config_filename)

        # Sets up the Logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logging.basicConfig(filename=project_root_path + '/log/' + time.strftime("%Y_%m_%d-%H_%M_%S") + '.log',
                            level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s',
                            filemode="w")
        
        # Create console handler and set its level to INFO
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Create formatter and add it to the console handler
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)

        # Add the console handler to the logger
        logger.addHandler(console_handler)

        self.__instance = self
        
    @staticmethod
    def get_instance():
        """
        Static method to get the instance of the class.
        """
        if Config.__instance is None:
            Config(Config.DEFAULT_CONFIG_FILENAME)
        return Config.__instance

    def load_config(self, config_filename):
        """Load the configuration from a YAML file.

        Args:
            config_filename (str): Filename of the configuration file.

        Returns:
            dict: Dictionary containing the configuration.

        Raises:
            FileNotFoundError: If the configuration file is not found.
        """
        with open(config_filename, 'r') as file:
            config = yaml.safe_load(file)
        return config

    def get_config_value(self, key: str):
        """Get the value of a configuration option.

        Args:
            key (str): Key corresponding to the configuration option.

        Returns:
            Any: Value of the configuration option, or None if not found.
        """
        return self.config.get(key)

    # Example method
    def print_config(self):
        """Print the configuration values."""
        for key, value in self.config.items():
            print(f"{key}: {value}")

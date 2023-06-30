import yaml
import os
import sys


project_root_path = os.path.normpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
)
sys.path.insert(1, os.path.join(project_root_path, 'config'))


class Config:
    """Class representing a configuration object."""

    DEFAULT_CONFIG_FILENAME = project_root_path + '/config/config.yml'

    def __init__(self, config_filename=None):
        """Initialize the Config object.

        Args:
            config_filename (str, optional): Filename of the configuration file.
                If not provided, the default configuration filename will be used.
        """
        if config_filename is None:
            config_filename = self.DEFAULT_CONFIG_FILENAME
        self.config = self.load_config(project_root_path + '/config/' + config_filename)

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

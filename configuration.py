from configparser import RawConfigParser
from os import path

from PyQt5.QtCore import pyqtSignal, QObject


class AppConfiguration(QObject):
    confNotExists = pyqtSignal()

    def __init__(self):
        super().__init__()

    def _load_config(self, conf_file: str, config: RawConfigParser):
        """
        Loads the configuration from the config file.
        """
        try:
            with open(conf_file, 'r') as conf_file:
                config.read_file(conf_file)
        except FileNotFoundError as err:
            print(err)
            self.confNotExists.emit()

    def check_load_config(self, conf_file):
        # Check and load the config files
        # Load the main app config file
        main_app_conf_file = path.abspath(conf_file)

        app_conf = RawConfigParser()
        self._load_config(main_app_conf_file, app_conf)

        return app_conf

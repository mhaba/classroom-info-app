from configparser import RawConfigParser, MissingSectionHeaderError
from os import path, makedirs

from PyQt5.QtCore import pyqtSignal, QObject

main_config = RawConfigParser()
CONF_PATH = '../config/classroom_info.conf'


class AppConfiguration(QObject):
    confError = pyqtSignal()

    def __init__(self):
        super().__init__()

    def _load_config(self, conf_file: str, config: RawConfigParser):
        """
        Loads the configuration from the config file.
        """
        try:
            with open(conf_file, 'r') as file:
                config.read_file(file)
        except FileNotFoundError as err:
            print('load_config1 ', err)
            self.confError.emit()
        except MissingSectionHeaderError as err:
            print('load_config2 ', err)
            self.confError.emit()

    def check_load_config(self, conf_file):
        # Check and load the config files
        # Load the main app config file
        main_app_conf_file = path.abspath(conf_file)

        self._load_config(main_app_conf_file, main_config)
        return main_config

    def make_conf_file(self):
        def create_conf_file():
            try:
                # Create dir only if not exists, otherwise will not throw error and pass
                makedirs("../config", exist_ok=True)
                with open(CONF_PATH, 'w') as file:
                    file.write('[classroom_info]')
            except Exception as err:
                print(f'[conf_file_exists] {err}')

        if path.exists(CONF_PATH) and path.getsize(CONF_PATH) > 0:
            if 'classroom_info' in main_config.sections():
                return True
            else:
                create_conf_file()
        else:
            create_conf_file()

        return True

    def add_section_value(self, section: str, option: str, value: str):
        try:
            with open(CONF_PATH, 'w') as file:
                file.write(section)
                file.write(f'\n{option} = {value}')

        except Exception as err:
            print(f'add_section_value {err}')
            exit(1)

    def get_classroom_code(self):
        try:
            return main_config.get('classroom_info', 'code')
        except Exception as err:
            print(f'[get_classroom_code] {err}')
            self.confError.emit()

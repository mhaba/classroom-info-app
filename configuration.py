from configparser import RawConfigParser, MissingSectionHeaderError
from os import path, makedirs, remove

from PyQt5.QtCore import pyqtSignal, QObject

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
            print(err)
            self.confError.emit()
        except MissingSectionHeaderError as err:
            print(err)
            remove(conf_file)
            self.make_conf_file(config)
            self._load_config(conf_file, config)

    def check_load_config(self, conf_file):
        # Check and load the config files
        # Load the main app config file
        main_app_conf_file = path.abspath(conf_file)

        app_conf = RawConfigParser()
        self._load_config(main_app_conf_file, app_conf)
        return app_conf

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
            config = self.check_load_config(CONF_PATH)
            # if '[classroom_info] in config.sections():
            if 'classroom_info' in config.sections():
                return True
            else:
                create_conf_file()
        else:
            create_conf_file()

        return True

    def add_section_value(self, section: str, option: str, value: str):
        old_conf = self.check_load_config(CONF_PATH)
        try:
            old_conf.set(section, option, value)
            with open(CONF_PATH, 'w') as file:
                old_conf.write(file)
                print(f'add_section {section} {option} {value}')

        except Exception as err:
            with open(conf_file, 'w') as file:
                file.write(section)
                file.write(f'{option} = {value}')
                print('Hola', option, value)
            print(f'[add_section_value] {err}')

    def get_classroom_code(self):
        try:
            config = self.check_load_config(CONF_PATH)
            return config.get('classroom_info', 'code')
        except Exception as err:
            print(f'[get_classroom_code] {err}')
            self.confError.emit()

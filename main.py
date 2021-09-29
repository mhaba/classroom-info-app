from sys import argv
import icalendar

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu

from presenter import Presenter
from views import Window, IdDialog
from configuration import AppConfiguration

from UPV.videoapuntes_client import VideoApuntesClient


videoapuntes_client = None
main_config = None


class AppWindow(QMainWindow):
    def __init__(self, application, config, parent=None):
        super(AppWindow, self).__init__(parent)

        self.setFixedSize(500, 525)
        self.setWindowIcon(QIcon("../../schoolroom-info/src/resources/logo_asic.jpg"))

        self.app = application
        self.win = Window()
        self.configuration = config
        self.configuration.confError.connect(self.handle_configuration_error)

        # App icon on windows toolbar
        self.tray_icon = QSystemTrayIcon(QIcon("../../schoolroom-info/src/resources/logo_asic.jpg"), self)
        # Context menu
        self.menu = QMenu()
        # Maximize action
        self.maximize_action = self.menu.addAction("Maximize")
        # Exit action
        self.exit_action = self.menu.addAction("Exit")
        self.use_system_tray()

        self.dialog = IdDialog()

        self.presenter = Presenter(self.win, self.configuration, self.dialog)

        self.setWindowTitle("Classroom info app")
        self.setCentralWidget(self.win)
        global main_config
        main_config = self.configuration.check_load_config("../config/classroom_info.conf")

    def use_system_tray(self):
        self.tray_icon.setToolTip("Galicaster info app")
        self.tray_icon.show()

        self.maximize_action.triggered.connect(self.show)
        self.menu.addSeparator()

        self.exit_action.triggered.connect(quit_app)
        self.tray_icon.setContextMenu(self.menu)

    def handle_configuration_error(self):
        self.configuration.make_conf_file()
        self.dialog.exec_()

        global main_config
        main_config = self.configuration.check_load_config("../config/classroom_info.conf")

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def showEvent(self, event):
        self.presenter.handle_refresh()
        event.accept()

    def get_configuration(self):
        return self.configuration


def quit_app():
    exit(0)


def get_qapplication_instance():
    if QApplication.instance():
        app = QApplication.instance()
    else:
        app = QApplication(argv)
    return app


def get_classroom(configuration):
    all_classrooms = videoapuntes_client.get_schoolrooms().get('value')
    classroom_code = configuration.get_classroom_code(main_config)

    classroom = next((classroom for classroom in all_classrooms if classroom.get('space') == classroom_code), None)

    return classroom


def main():
    app = get_qapplication_instance()
    configuration = AppConfiguration()

    app_window = AppWindow(app, configuration)
    app_window.show()

    global videoapuntes_client
    server_conf = '../config/servers.conf'
    videoapuntes_client = VideoApuntesClient(server_conf)

    classroom = get_classroom(configuration)
    if not classroom:
        app_window.handle_configuration_error()

    classroom_code = classroom.get('_id')
    configuration.add_section_value('../config/classroom_info.conf', 'classroom_info', 'id', classroom_code)

    exit(app.exec())


if __name__ == '__main__':
    main()

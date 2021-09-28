from sys import argv

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu

from presenter import Presenter
from views import Window, IdDialog
from configuration import AppConfiguration


class AppWindow(QMainWindow):
    def __init__(self, application, parent=None):
        super(AppWindow, self).__init__(parent)

        self.setFixedSize(500, 525)

        self.app = application
        self.win = Window()
        self.configuration = AppConfiguration()
        self.configuration.confNotExists.connect(self.handle_configuration_not_exists)

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

        self.main_config = self.configuration.check_load_config("../config/classroom_info.conf")

    def use_system_tray(self):
        self.tray_icon.setToolTip("Galicaster info app")
        self.tray_icon.show()

        self.maximize_action.triggered.connect(self.show)
        self.menu.addSeparator()

        self.exit_action.triggered.connect(quit_app)
        self.tray_icon.setContextMenu(self.menu)

    def handle_configuration_not_exists(self):
        self.dialog.exec_()

        self.main_config = self.configuration.check_load_config("../config/classroom_info.conf")

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def showEvent(self, event):
        self.presenter.handle_refresh()
        event.accept()


def quit_app():
    exit(0)


def get_qapplication_instance():
    if QApplication.instance():
        app = QApplication.instance()
    else:
        app = QApplication(argv)
    return app


if __name__ == '__main__':
    app = get_qapplication_instance()

    app_window = AppWindow(app)
    app_window.show()

    exit(app.exec())

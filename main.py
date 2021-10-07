from sys import argv
from datetime import datetime, timedelta

from PyQt5.QtCore import QThread, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu

from presenter import Presenter
from views import Window, IdDialog
from configuration import AppConfiguration
from worker import Worker

from UPV.videoapuntes_client import VideoApuntesClient


videoapuntes_client = None
server_conf = '../config/servers.conf'
main_config = None


class AppWindow(QMainWindow):
    def __init__(self, application, config, parent=None):
        super(AppWindow, self).__init__(parent)

        global videoapuntes_client
        videoapuntes_client = VideoApuntesClient(server_conf)

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

        self.presenter = Presenter(self.win,  self.dialog, self.configuration)

        self.setWindowTitle("Classroom info app")
        self.setCentralWidget(self.win)

        global main_config
        main_config = self.configuration.check_load_config("../config/classroom_info.conf")

        self._classroom_code = self.configuration.get_classroom_code()
        self._next_recordings = None

        # Thread work
        self._worker = None
        self._worker_thread = QThread()
        # self._win_thread = QThread(self.win)
        # self._win_thread.started.connect(self.presenter.handle_refresh)
        self._timer = QTimer()
        # Videoapuntes general parameters (if changed will refresh at application's reload)
        self._parameters = videoapuntes_client.get_parameters()
        self.status_refresh_rate = self._parameters.get('status')
        # Reload calendar and status info
        # self._reload_calendar()
        # self._reload_status()
        # Create threads
        self._create_status_thread()

    def _stop_thread(self):
        self._timer.stop()
        self._worker_thread.quit()

    def _reload_parameters(self):
        # Reloads videoapuntes given parameters
        self._parameters = videoapuntes_client.get_parameters()
        if self.status_refresh_rate != self._parameters.get('status'):
            self.status_refresh_rate = self._parameters.get('status')

            self._stop_thread()
            self._worker.moveToThread(self._worker_thread)
            # self._worker_thread.start()
            self._timer.timeout.connect(self._reload_status)
            self._timer.start(self.status_refresh_rate)

    def _reload_status(self):
        self._classroom_code = self.configuration.get_classroom_code()
        recs = videoapuntes_client.get_icalendar(self._classroom_code)
        print(f'_reload_status (classroom code): {self._classroom_code}')

        self._reload_parameters()

        self._worker = Worker(recs)

        self._worker_thread.start()

        print(f'_reload_status (recordings): {recs}')

    def _create_status_thread(self):
        self._classroom_code = self.configuration.get_classroom_code()
        recs = videoapuntes_client.get_icalendar(self._classroom_code)
        self._worker = Worker(recs)

        self._worker.moveToThread(self._worker_thread)
        self._worker_thread.started.connect(self._worker.work)

        self._timer.timeout.connect(self._reload_status)
        self._timer.start(self.status_refresh_rate)

        # Call _spinning functions when worker.refreshing or worker.refreshed are emitted
        self._worker.refreshing.connect(self.presenter.handle_refresh)
        # self._worker.refreshing.connect(self.win.start_spinning)
        self._worker.refreshed.connect(self.presenter.handle_stop_refresh)
        # self._worker.refreshed.connect(self.win.stop_spinning)
        # Call when worker.recording, .noRecording, willRec are emitted
        self._worker.recording.connect(self.win.recording)
        self._worker.noRecording.connect(self.win.no_recording)
        self._worker.willRec.connect(self.win.will_record)

        self._worker_thread.start()

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


def main():
    app = get_qapplication_instance()
    configuration = AppConfiguration()

    app_window = AppWindow(app, configuration)
    app_window.show()

    exit(app.exec())


if __name__ == '__main__':
    main()

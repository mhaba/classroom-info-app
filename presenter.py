from time import sleep
from os import makedirs

from PyQt5.QtCore import QThread, QTimer, QObject, pyqtSignal


class Presenter(object):
    # pass the view and model into the presenter
    # def __init__(self, window, config, id_dlg):
    def __init__(self, window, config, dlg):
        self._refreshed = False

        self.win = window
        self.configuration = config
        self.dialog = dlg

        self._thread = QThread(self.win)
        self._worker = Worker()
        # worker will run in another thread
        self._worker.moveToThread(self._thread)
        # timer will refresh status
        self._timer = QTimer()
        self._timer.timeout.connect(self._auto_refresh)

        self._timer.start()

        # Call _stop_spinning when worker.refreshed is emitted
        self._worker.refreshing.connect(self.win.start_spinning)
        self._worker.refreshed.connect(self.win.stop_spinning)
        # Call worker.doWork when the thread starts
        self._thread.started.connect(self._worker.do_refresh)

        # Call handle_refresh when button 'refresh' is pressed.
        self.win.doRefresh.connect(self.handle_refresh)
        self.win.refreshStopped.connect(self.handle_stop_refresh)

        self.dialog.acceptDialog.connect(self.handle_btn_accept)

    # handle dialog signals
    def handle_btn_accept(self):
        dlg_text, dialog = self.dialog.get_text()

        try:
            # Create dir only if not exists, otherwise will not throw error and pass
            makedirs("../config", exist_ok=True)
            with open('../config/classroom_info.conf', 'w') as config_file:
                config_file.write('[classroom_info]\n')
                config_file.write(f'id = {dlg_text}')
                dialog.close()
        except Exception as err:
            print(f'Error at handle_configuration: {err}')

    # handle view signals
    def handle_refresh(self):
        refresh_btn = self.win.get_button()
        # Start the thread (and run do_work)
        refresh_btn.setEnabled(False)
        self._thread.start()

    def handle_stop_refresh(self):
        refresh_btn = self.win.get_button()
        self._thread.quit()
        refresh_btn.setEnabled(True)

    def _auto_refresh(self):
        # First refresh at app start, then update every 5 minutes
        if not self._refreshed:
            self._timer.setInterval(300000)
            self._refreshed = True
        else:
            self.handle_refresh()


class Worker(QObject):
    refreshing = pyqtSignal()
    refreshed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def do_refresh(self):
        self.refreshing.emit()
        sleep(5)
        self.refreshed.emit()

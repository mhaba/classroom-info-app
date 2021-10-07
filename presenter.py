from time import sleep
from os import makedirs

from PyQt5.QtCore import QThread, QTimer

from worker import Worker


class Presenter(object):
    # pass the view and model into the presenter
    # def __init__(self, window, config, id_dlg):
    def __init__(self, window, dlg, config):
        self._refreshed = False

        self.win = window
        self.configuration = config
        self.dialog = dlg

        self._thread = QThread(self.win)
        self._worker = Worker()
        # worker will run in another thread
        self._worker.moveToThread(self._thread)
        # timer will refresh status
        # self._timer = QTimer()
        # self._timer.timeout.connect(self._auto_refresh)

        # self._timer.start()
        # self._thread.start()

        ## Call _spinning functions when worker.refreshing or worker.refreshed are emitted
        #self._worker.refreshing.connect(self.win.start_spinning)
        #self._worker.refreshed.connect(self.win.stop_spinning)
        ## Call when worker.recording, .noRecording, willRec are emitted
        #self._worker.recording.connect(self.win.recording)
        #self._worker.noRecording.connect(self.win.no_recording)
        ## self._worker.willRec.connect(self.win.will_record)
        #self._worker.willRec.connect(self.hola)
#
        ## self._thread.start()
#
        ## Call handle_refresh when button 'refresh' is pressed.
        #self.win.doRefresh.connect(self.handle_refresh)
        #self.win.refreshStopped.connect(self.handle_stop_refresh)

        self.dialog.acceptDialog.connect(self.handle_btn_accept)

    def hola(self):
        print('Presenter dice hola')

    # handle dialog signals
    def handle_btn_accept(self):
        dlg_text, dialog = self.dialog.get_text()
        if self.configuration.make_conf_file():
            self.configuration.add_section_value('classroom_info', 'code', dlg_text)
            print(f'Btn accept: {dlg_text}')
            dialog.close()

    # handle view signals
    def handle_refresh(self):
        print('presenter handle_refresh')
        refresh_btn = self.win.get_button()
        # Start the thread (and run do_work)
        refresh_btn.setEnabled(False)
        # self._thread.start()
        self.win.start_spinning()

    def handle_stop_refresh(self):
        print('presenter handle_stop_refresh')
        refresh_btn = self.win.get_button()
        # self._thread.quit()
        refresh_btn.setEnabled(True)
        self.win.stop_spinning()

    def _auto_refresh(self):
        # First refresh at app start, then update every 5 minutes
        if not self._refreshed:
            self._timer.setInterval(300000)
            self._refreshed = True
        else:
            self.handle_refresh()

    def smith_status(self):
        status = self.configuration.get_status()

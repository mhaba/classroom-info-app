from PyQt5.QtCore import QThread

from worker import Worker


class Presenter(object):
    # pass the view and model into the presenter
    def __init__(self, window, dlg, config):
        self._refreshed = False

        self.win = window
        self.configuration = config
        self.dialog = dlg

        self._thread = QThread(self.win)
        self._worker = Worker()
        # worker will run in another thread
        self._worker.moveToThread(self._thread)

        self.dialog.acceptDialog.connect(self.handle_btn_accept)

    # handle dialog signals
    def handle_btn_accept(self):
        dlg_text, dialog = self.dialog.get_text()
        if self.configuration.make_conf_file():
            self.configuration.add_section_value('[classroom_info]', 'code', dlg_text)
            print(f'Btn accept: {dlg_text}')
            dialog.close()

    # handle view signals
    def handle_refresh(self):
        self.win.start_spinning()

    def handle_stop_refresh(self):
        self.win.stop_spinning()

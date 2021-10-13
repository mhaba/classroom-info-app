from datetime import datetime
from time import sleep

from PyQt5.QtCore import QObject, pyqtSignal


RECORDING_STATUS = 'recording'
WILL_RECORD_STATUS = 'willRecord'
NO_RECORDING = 'noRecording'


class Worker(QObject):
    refreshing = pyqtSignal()
    refreshed = pyqtSignal()

    recording = pyqtSignal()
    noRecording = pyqtSignal()
    willRec = pyqtSignal()

    def __init__(self, recordings=None, parent=None):
        super().__init__(parent)
        self._recordings = recordings

    def work(self):
        print(self._recordings)
        time_tuple = get_time_to_start(self._recordings)

        will_rec = time_tuple[0]
        time_to_record = time_tuple[1]

        self.refreshing.emit()
        sleep(5)
        # Is recording now
        if will_rec and time_to_record == 0:
            print('recording')
            self.recording.emit()
        # Won't record (more) today
        elif not will_rec and time_to_record == -1:
            print('no recording')
            self.noRecording.emit()
        # Will record at any time
        else:
            # Not using this signal for now
            print('will record')
            self.willRec.emit()


def get_status(recording):
    if 'recordedStatus' not in recording.keys():
        return WILL_RECORD_STATUS
    elif 'recording' in recording.get('recordedStatus'):
        return RECORDING_STATUS
    else:
        return NO_RECORDING


def get_time_to_start(recordings):
    next_recording = None
    date_now = datetime.now()

    for recording in recordings.get('value'):
        rec = recording.get('startRecord')
        rec_status = get_status(recording)

        if rec_status == RECORDING_STATUS:
            return True, 0

        if '.' in rec:
            rec = rec.split('.')[0]
        recording_date = datetime.strptime(rec, '%Y-%m-%dT%H:%M:%S')

        # next recording will be on the future, so it will be at a greater time
        if recording_date > date_now:
            next_recording = recording_date
            break
        else:
            continue

    # TODO: Remove, it is an example to test
    next_recording = datetime.strptime('2021-10-30T17:30:00', '%Y-%m-%dT%H:%M:%S')

    if not next_recording:
        return False, -1

    time_to_start = next_recording - date_now
    return True, time_to_start.total_seconds()

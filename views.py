from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QDialog


class Window(QWidget):
    doRefresh = pyqtSignal()
    refreshStopped = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        with open("../../schoolroom-info/src/styles/styles.css") as f:
            self.setStyleSheet(f.read())

        self._refreshed = False

        self.setObjectName("window")
        self.setWindowTitle("Galicaster info App")
        self.setFixedSize(500, 500)

        self.dialog = IdDialog()

        # Label at the window's top. Text info (status and refreshing)
        self._info_label = QLabel()
        self._info_label.setObjectName("info_text")
        self._info_label.setText("Unknown")

        # Image / gif at the window's middle. Visual info (status and refreshing)
        # Color circle image
        self._image = QPixmap("../../schoolroom-info/src/resources/grey.png").scaled(250, 250)
        self._info_circle = QLabel(self)
        self._info_circle.setObjectName("info_circle")
        self._info_circle.setPixmap(self._image)
        # Loading gif
        self._loading_spinner = QLabel(self)
        self._loading_spinner.setObjectName("loading_spinner")
        self._loading_spinner.setGeometry(QRect(25, 25, 200, 200))
        self._loading_spinner.resize(50, 50)
        self._loading_gif = QMovie("../../schoolroom-info/src/resources/loading.gif")

        # Refresh button
        self._refresh_btn = QPushButton("Refresh", self)
        self._refresh_btn.setObjectName("refresh_btn")
        self._refresh_btn.setFixedSize(100, 25)
        # Button box
        self._btn_hbox = QHBoxLayout()
        self._btn_hbox.addWidget(self._refresh_btn)
        # Refreshing functionality
        self._refresh_btn.clicked.connect(self.refresh)

        self._vbox = QVBoxLayout()
        self._vbox.setObjectName("loader_box")
        self._vbox.addWidget(self._info_label)
        self._vbox.addStretch(1)
        self._vbox.addWidget(self._info_circle)
        self._vbox.addStretch(1)
        self._vbox.addLayout(self._btn_hbox)

        self._info_label.setAlignment(Qt.AlignCenter)
        self._vbox.setAlignment(Qt.AlignCenter)

        self.setLayout(self._vbox)

    def start_spinning(self):
        self._info_label.setText("Refreshing...")
        self._info_circle.setMovie(self._loading_gif)

        self._loading_gif.start()

    def stop_spinning(self):
        if True:
            self._image = QPixmap("../../schoolroom-info/src/resources/red.png").scaled(250, 250)
            self._info_label.setText("Recording")
        else:
            self._info_label.setText("No recording")
            self._image = QPixmap("../../schoolroom-info/src/resources/grey.png").scaled(250, 250)

        self._loading_gif.stop()
        self._info_circle.setPixmap(self._image)
        self.refreshStopped.emit()

    def refresh(self):
        self.doRefresh.emit()

    def get_button(self):
        return self._refresh_btn


class IdDialog(QDialog):
    exitDialog = pyqtSignal()
    acceptDialog = pyqtSignal()

    def __init__(self):
        super(IdDialog, self).__init__()

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setEnabled(True)
        # self.resize(400, 150)
        self.setFixedSize(400, 150)
        self.setWindowTitle("No se encontró el código de aula")
        self.setModal(True)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(40, 110, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(20, 20, 361, 16))
        self.label.setObjectName("label")
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setGeometry(QtCore.QRect(20, 50, 361, 21))
        self.lineEdit.setObjectName("lineEdit")
        self.label.setText("Introduzca el código de aula: ")

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def closeEvent(self, event):
        if self.lineEdit.text():
            event.accept()
        else:
            event.ignore()

    # Cancel button
    def reject(self):
        self.exitDialog.emit()

    # Accept button
    def accept(self):
        self.acceptDialog.emit()

    def get_text(self):
        return self.lineEdit.text(), self

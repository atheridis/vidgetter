import json
import os
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QProgressBar,
)
from yt_dlp import YoutubeDL


class Downloader(QObject):
    download_percent = pyqtSignal(int)

    def progress(self, d):
        if d["status"] == "downloading":
            try:
                p = d["_percent_str"].split()[1]
            except IndexError:
                print(f"ind: {d['_percent_str'].split()}")
                self.download_percent.emit(100)
                return
            p = p[: p.find("%")]
            self.download_percent.emit(int(float(p)))

    def download_video(self, ydl_opts):
        print("hi")
        url, ydl_opts = ydl_opts.split(";")
        ydl_opts = json.loads(ydl_opts)
        ydl_opts["progress_hooks"] = [self.progress]
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)


class MainWindow(QMainWindow):
    download_options = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vid Saver")
        self.url_label = QLabel("Video Link")
        self.url_text = QLineEdit(self)

        self.browse_save_dir_button = QtWidgets.QPushButton("Browse")
        self.browse_save_dir_button.clicked.connect(self.open_file_dialog)
        self.dir_text = QLineEdit(self)
        self.dir_text.setReadOnly(True)

        self.progress_bar = QProgressBar()

        self.download_button = QtWidgets.QPushButton("Download")
        self.download_button.clicked.connect(self.send_download_signal)

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.grid_layout = QtWidgets.QGridLayout(self.central_widget)
        self.grid_layout.addWidget(self.url_label, 0, 0, 1, 1)
        self.grid_layout.addWidget(self.url_text, 0, 1, 1, 1)
        self.grid_layout.addWidget(self.browse_save_dir_button, 1, 0, 1, 1)
        self.grid_layout.addWidget(self.download_button, 2, 0, 1, 2)
        self.grid_layout.addWidget(self.dir_text, 1, 1, 1, 1)
        self.grid_layout.addWidget(self.progress_bar, 3, 0, 1, 2)

        self.downloader = Downloader()
        self.downloader_thread = QThread()
        self.downloader.moveToThread(self.downloader_thread)

        self.downloader.download_percent.connect(self.update_download_percent)
        self.download_options.connect(self.downloader.download_video)

        self.downloader_thread.start()

    def open_file_dialog(self):
        self.dir_text.setText(
            QFileDialog.getExistingDirectory(
                None,
                "Test Dialog",
                os.getcwd(),
            )
        )

    def send_download_signal(self):
        ydl_opts = self.url_text.text() + ";"
        ydl_opts += json.dumps(self.ydl_opts)
        self.download_options.emit(ydl_opts)

    def update_download_percent(self, percent):
        print(percent)
        self.progress_bar.setValue(percent)

    @property
    def ydl_opts(self):
        return {"outtmpl": os.path.join(self.dir_text.text(), "%(title)s.%(ext)s")}


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

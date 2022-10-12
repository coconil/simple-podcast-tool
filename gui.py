import sys

from PySide6.QtCore import Qt, Slot, QTimer, QStringListModel,QUrl
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtMultimedia import QMediaPlayer,QAudioOutput
from PySide6.QtWidgets import QVBoxLayout, QWidget, QSlider, QHBoxLayout, QLabel, QFrame, QListView, QPushButton, \
    QAbstractItemView, QDialog, QLineEdit
import podcast


def time_string(sec):
    hour = sec // 60 // 60 % 24
    min = sec // 60 % 60
    sec = sec % 60
    return '{}:{}:{}'.format(hour, min, sec)


class SearchDialog(QDialog):
    def __init__(self,subscribe,search):
        super().__init__()
        self.podcast=podcast
        self.setWindowTitle("Search a podcast")
        self.edit = QLineEdit()
        self.result_list = QListView()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.result_list)
        self.setLayout(self.layout)

        self.edit.returnPressed.connect(search)
        self.result_list.doubleClicked.connect(subscribe)
        self.result_list.setEditTriggers(QAbstractItemView.NoEditTriggers)

class MyWidget(QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.content_layout = QHBoxLayout()
        self.podcasts_list = QListView()
        self.item_list = QListView()
        self.item_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.podcasts_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.duration = 0
        self.playtime_label = QLabel()
        self.duration_label = QLabel()
        self.playtime_label.setTextFormat(QtCore.Qt.PlainText)
        self.duration_label.setTextFormat(QtCore.Qt.PlainText)
        self.playtime_label.setText("00:00:00")
        self.playtime_label.setFixedHeight(20)
        self.duration_label.setText("00:00:00")
        self.duration_label.setFixedHeight(20)

        self.progress_bar = QSlider(QtCore.Qt.Horizontal)

        self.content_layout.addWidget(self.podcasts_list)
        self.content_layout.setStretch(0, 2)
        self.content_layout.addWidget(self.item_list)
        self.content_layout.setStretch(1, 8)
        self.download_button = QPushButton("Download")
        self.play_button = QPushButton("Play")

        self.status_layout = QHBoxLayout()
        self.status_layout.addWidget(self.playtime_label)
        self.status_layout.addWidget(self.progress_bar)
        self.status_layout.addWidget(self.duration_label)
        self.status_layout.addWidget(self.play_button)
        self.status_layout.addWidget(self.download_button)

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.content_layout)
        self.layout.addLayout(self.status_layout)

        self.setLayout(self.layout)

    def update_podcasts_list(self, names):
        model = QStringListModel(names)
        self.podcasts_list.setModel(model)

    def update_items_list(self, names):
        model = QStringListModel(names)
        self.item_list.setModel(model)

    def set_progress(self, progress):
        self.progress_bar.setValue(progress)
        self.playtime_label.setText(time_string(progress))

    def set_duration(self, duration):
        self.duration = duration
        self.progress_bar.setRange(0, duration)
        self.duration_label.setText(time_string(duration))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, widget, data):
        # super().__init__()

        QtWidgets.QMainWindow.__init__(self)

        self.setWindowTitle("Simple Podcast Utility")
        self.widget = widget
        self.podcast = podcast
        self.items = None
        self.setCentralWidget(widget)
        self.player = QMediaPlayer()
        self.audioOutput=QAudioOutput()
        self.media = None
        # Menu
        self.menu = QtWidgets.QMenuBar()  #
        self.menu = self.menuBar()
        self.menu.setNativeMenuBar(False)
        self.setMenuBar(self.menu)
        self.file_menu = self.menu.addMenu("File")

        add_action = QtGui.QAction("Add", self)
        exit_action = QtGui.QAction("Exit", self)
        self.file_menu.addAction(add_action)
        self.file_menu.addAction(exit_action)
        add_action.triggered.connect(self.add_podcast)
        exit_action.triggered.connect(self.exit_app)
        names = self.get_podcast_name_list(self.podcast.get_subscribe())
        self.widget.update_podcasts_list(names)

        self.widget.podcasts_list.clicked.connect(self.update_item_list)
        self.widget.item_list.doubleClicked.connect(self.start_play_item)
        self.widget.play_button.clicked.connect(self.toggle_play)
        self.widget.progress_bar.sliderPressed.connect(
            self.on_select_progress_begin)
        self.widget.progress_bar.sliderReleased.connect(
            self.on_select_progress_end)
        self.widget.progress_bar.sliderMoved.connect(
            self.on_select_progress_move)

        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(1000)

        self.begin_seek = False
        self.play_url = None

    @Slot()
    def on_select_progress_begin(self):
        self.begin_seek = True

    @Slot()
    def on_select_progress_move(self, value):
        self.widget.playtime_label.setText(time_string(value))

    @Slot()
    def on_select_progress_end(self):
        if self.player.isSeekable():
            value = self.widget.progress_bar.value()
            self.player.setPosition(value * 1000)
            self.begin_seek = False
        else:
            print('not seekable')

    @Slot()
    def on_timer(self):
        player = self.player
        if not self.begin_seek:
            if player.playbackState() == QMediaPlayer.PlayingState:
                playtime = player.position() // 1000
                self.widget.set_progress(playtime)
    def do_play(self,i):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.stop()

        self.begin_seek = False
        self.play_url = self.items[i]['url']
        self.media = QUrl(self.items[i]['url'])
        self.player.setAudioOutput(self.audioOutput)
        self.player.setSource(self.media)
        self.player.play()
        self.widget.set_duration(self.items[i]['duration'])
        self.widget.play_button.setText('Pause')
    @Slot()
    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.widget.play_button.setText('play')
        elif self.player.playbackState() == QMediaPlayer.PausedState:
            self.player.play()
            self.widget.play_button.setText('Pause')
        else:
            indexs=self.widget.item_list.selectedIndexes()
            self.do_play(indexs[0].row())

    @Slot()
    def start_play_item(self, index):
        i = index.row()
        self.do_play(i)



    @Slot()
    def update_item_list(self, index):
        i = index.row()
        feed_url = self.podcast.podcasts[i]['feedUrl']
        self.items = podcast.get_feed(feed_url)
        names = self.get_item_name_list(self.items)
        self.widget.update_items_list(names)

    @Slot()
    def subscribe(self, index):
        i = index.row()
        self.podcast.subscribe(self.search_r[i])
        names = self.get_podcast_name_list(self.podcast.get_subscribe())
        self.widget.update_podcasts_list(names)

    @Slot()
    def search(self):
        self.search_r = self.podcast.search(self.dialog.edit.text())
        names = []
        if self.search_r:
            for i in self.search_r:
                names.append(i['collectionName'])
            model = QStringListModel(names)
            self.dialog.result_list.setModel(model)

    def get_item_name_list(self, items):
        names = []
        for item in items:
            names.append(item['title'])
        return names

    def get_podcast_name_list(self, podcasts):
        names = []
        for item in podcasts:
            names.append(item['collectionName'])
        return names

    @Slot()
    def add_podcast(self, checked):
        self.dialog = SearchDialog(self.subscribe,self.search)
        self.dialog.exec()
        self.dialog=None

    @Slot()
    def exit_app(self, checked):
        print('exit app')
        QtWidgets.QApplication.quit()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    podcast = podcast.Podcast()
    widget = MyWidget()
    window = MainWindow(widget, podcast)
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())

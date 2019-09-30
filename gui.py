import sys

from PySide2.QtCore import Qt, Slot, QTimer, QStringListModel
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import QVBoxLayout, QWidget, QSlider, QHBoxLayout, QLabel, QFrame, QListView, QPushButton
import player
import json
import podcast

class MyWidget(QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.content_layout = QHBoxLayout()
        self.podcasts_list = QListView()
        self.item_list = QListView()

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
        self.download_button = QPushButton("&Download")
        self.play_botton = QPushButton("&Play")

        self.status_layout = QHBoxLayout()
        self.status_layout.addWidget(self.playtime_label)
        self.status_layout.addWidget(self.progress_bar)
        self.status_layout.addWidget(self.duration_label)
        self.status_layout.addWidget(self.play_botton)
        self.status_layout.addWidget(self.download_button)

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.content_layout)
        self.layout.addLayout(self.status_layout)

        self.setLayout(self.layout)


    def update_podcasts_list(self, names):
        model = QStringListModel(names)
        self.podcasts_list.setModel(model)
    def update_items_list(self,names):
        model = QStringListModel(names)
        self.item_list.setModel(model)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, widget, data):
        # super().__init__()

        QtWidgets.QMainWindow.__init__(self)

        self.setWindowTitle("SimplePlayer")
        self.widget = widget
        self.data = data
        self.setCentralWidget(widget)

        # Menu
        self.menu = QtWidgets.QMenuBar()  #
        self.menu = self.menuBar()
        self.menu.setNativeMenuBar(False)
        self.setMenuBar(self.menu)
        self.file_menu = self.menu.addMenu("File")

        add_action = QtWidgets.QAction("Add", self)
        exit_action = QtWidgets.QAction("Exit", self)
        self.file_menu.addAction(add_action)
        self.file_menu.addAction(exit_action)
        add_action.triggered.connect(self.add_podcast)
        exit_action.triggered.connect(self.exit_app)
        names = self.get_podcast_name_list(self.data)
        self.widget.update_podcasts_list(names)

        self.widget.podcasts_list.clicked.connect(self.update_item_list)
    @Slot()
    def update_item_list(self,index):
        i=index.row()
        feedUrl=self.data[i]['feedUrl']
        items=podcast.get_feed(feedUrl)
        names=self.get_item_name_list(items)
        self.widget.update_items_list(names)
    def get_item_name_list(self,items):
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
        pass

    @Slot()
    def exit_app(self, checked):
        print('exit app')
        QtWidgets.QApplication.quit()





if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    podcasts = podcast.get_subscribe()
    widget = MyWidget()
    window = MainWindow(widget, podcasts)
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
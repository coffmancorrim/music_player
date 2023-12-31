from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget, QGridLayout

class TrackInfoWidget(QWidget):
    def __init__(self, track_number, name_of_track, track_length, song_path):
        super().__init__()
        self.track_number = track_number
        self.name_of_track = name_of_track
        self.track_length = track_length
        self.song_path = song_path
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(15)

        text_layout = QGridLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(10)

        track_number_label = QLabel(f"{self.track_number}")
        track_number_label.setStyleSheet("font-size: 14px; color: #666; font-weight: bold;")

        track_name_label = QLabel(self.name_of_track)
        track_name_label.setStyleSheet("font-size: 14px; color: #333;")

        track_length_label = QLabel(self.track_length)
        track_length_label.setStyleSheet("font-size: 14px; color: #333;")

        text_layout.addWidget(track_number_label, 0,0, alignment=Qt.AlignLeft)
        text_layout.addWidget(track_name_label, 0,1, alignment=Qt.AlignCenter)
        text_layout.addWidget(track_length_label, 0,2, alignment=Qt.AlignRight)

        text_widget = QWidget()
        text_widget.setLayout(text_layout)
    
        main_layout.addWidget(text_widget, Qt.AlignTop)

        self.setLayout(main_layout)

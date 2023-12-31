import os, random, sys, pygame, eyed3
from functools import partial
from PySide6.QtCore import Qt, QSettings, QTimer
from PySide6.QtGui import QIcon, QKeySequence, QShortcut, QPixmap
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog, QHBoxLayout, QLabel, QMainWindow, QPushButton, QSlider, QVBoxLayout, QWidget, QListWidget, QListWidgetItem, QGraphicsBlurEffect, QStyle
from album import Album
from get_directory_names import *
from input_dialog import InputDialog
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.wavpack import WavPack
from settings_dialog import SettingsDialog
from song import Song
from track_info_widget import TrackInfoWidget

current_dir = os.path.dirname(os.path.abspath(__file__))
background_directory = os.path.join(current_dir, 'Assets', 'background.jpg')
current_dir = os.path.dirname(os.path.abspath(__file__))
stylesheet_directory = os.path.join(current_dir, 'Assets', 'stylesheet.qss')

class FrostedGlassEffect(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(50)  
        self.background_pixmap = QPixmap(background_directory) 
        self.initUI()

    def initUI(self):
        self.background_label = QLabel(self)
        self.background_label.setGraphicsEffect(self.blur_effect)
        self.background_label.setAlignment(Qt.AlignCenter)

        self.overlay = QWidget(self)
        self.overlay.setStyleSheet("background-color: rgba(255, 255, 255, 150);")

        self.resize_background(self.size())

    def resize_background(self, size):
        scaled_pixmap = self.background_pixmap.scaled(size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.background_label.setPixmap(scaled_pixmap)
        self.background_label.setGeometry(0, 0, size.width(), size.height())
        self.overlay.setGeometry(0, 0, size.width(), size.height())

    def resizeEvent(self, event):
        self.resize_background(event.size())
        super().resizeEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        pygame.mixer.init()
        self.settings = QSettings("YourOrganization", "MusicPlayer")
        self.music_dir = self.settings.value("musicDir", "")
        self.saved_album = self.settings.value("album", "")
        self.saved_artist = self.settings.value("artist", "")
        self.track_numbers = []
        self.is_paused = False
        self.current_song = None
        self.shuffle = False
        self.shuffle_index = 0
        self.shuffled_list = []
        self.repeat = False
        self.play = True
        self.current_pos = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_slider)
        
        with open(stylesheet_directory, "r") as f:
            self.setStyleSheet(f.read())

        if not self.music_dir:
            self.select_music_dir()

        if not self.saved_album and self.saved_album:
            input = InputDialog()
            input.exec()
            
            user_artist, user_album = input.get_user_input()
            self.main(user_artist, user_album)
        else:
            self.main(self.saved_album, self.saved_artist)
            self.setGeometry(100, 100, 800, 600)

    def main(self, album, artist):
        self.settings.setValue("album", album)
        self.settings.setValue("artist", artist)

        central_widget = FrostedGlassEffect(self)
        central_layout = QHBoxLayout()
        central_widget.setLayout(central_layout)

        side_menu_widget = self.create_side_menu()
        side_menu_widget.setStyleSheet("background-color: white; border: none; margin: 0, 10, 0, 0; border-radius: 10px;")
        central_layout.addWidget(side_menu_widget)

        album_menu_widget = self.create_album_menu(album, artist)
        central_layout.addWidget(album_menu_widget)

        self.setWindowTitle('Album Player')
        self.setCentralWidget(central_widget)

        self.playlist.setStyleSheet("QListWidget {border: none;} ")

        for number in self.track_numbers:
            num_string = str(number)
            if num_string == "10":
                num_string = "0"
            elif 11 <= int(number) <= 20:
                second_number = str(number)[-1]
                num_string = f"Ctrl+{second_number}"
            elif 1 <= int(number) <= 9:
                if num_string.startswith("0"):
                    num_string = num_string.lstrip("0")
            else:
                num_string = "Unknown Key"  # Placeholder for track numbers above 20
            shortcut = QShortcut(QKeySequence(num_string), self.playlist)
            shortcut.activated.connect(partial(self.connect_shortcut_to_widget, number))
                
    def connect_shortcut_to_widget(self, number):
        num = int(number)
        item = self.playlist.item(num - 1)
        previous_item = self.playlist.currentItem()
        if previous_item == item or previous_item == None:
            self.playlist.setCurrentItem(item)
            self.play_pause_control()
        else:
            self.playlist.setCurrentItem(item)
            self.play_pause_control("play")

    def create_album_menu(self, user_artist, user_album):
        album_main_widget = QWidget()
        album_layout = QVBoxLayout()
        album_main_widget.setLayout(album_layout)

        self.create_playlist()

        album = self.load_dir(
            self.music_dir,
            user_artist,
            user_album
            )

        main_album_display_widget = self.create_layout(album)
        album_layout.addWidget(main_album_display_widget)

        wrapper_layout = QVBoxLayout()
        wrapper_widget = QWidget()
        wrapper_widget.setLayout(wrapper_layout)
        wrapper_layout.addWidget(self.playlist)
        wrapper_widget.setObjectName("wrapperWidget")
        wrapper_widget.setStyleSheet("QWidget#wrapperWidget { border-radius: 10px; background-color: white; padding: 5px; }")

        self.playlist.setStyleSheet("")
        album_layout.addWidget(wrapper_widget)

        return album_main_widget

    def create_square_widget(self, album_art_path, width, height):
        if album_art_path:
            print("Album art found in tags")
            audio_file = eyed3.load(album_art_path)
            album_art_data = audio_file.tag.images[0].image_data
        else:
            print("No album art found in tags")
            album_art_data = ""

        square_widget = QLabel()

        if album_art_data:
            print("Album art data found")
            pixmap = QPixmap()
            pixmap.loadFromData(album_art_data)
            scaled_pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio)
            square_widget.setPixmap(scaled_pixmap)
        else:
            print("No album art data found, creating a grey square")
            square_widget = QWidget()
            square_widget.setFixedSize(width, height)
            square_widget.setStyleSheet("background-color: grey;")

        return square_widget

    def create_layout(self, album):
            main_widget = QWidget()
            main_widget.setStyleSheet("background-color: transparent;") 

            square_width = 225
            square_height = 225
            album_art = self.create_square_widget(album.album_art_path, square_width, square_height)

            vertical_layout = QVBoxLayout()
            album_title = QLabel(album.title)
            artist = QLabel(album.artist)
            genre = QLabel(album.genre)
            release_date = QLabel(album.year)

            album_title.setStyleSheet("font-weight: bold; font-size: 30px; margin-left:5px;")  
            artist.setStyleSheet("font-weight: bold; font-size: 20px; margin-left:10px;")  
            genre.setStyleSheet("font-size: 20px; margin-left:10px;") 
            release_date.setStyleSheet("font-size: 20px; margin-left:10px;")

            text_labels = [album_title, artist, genre, release_date]
            for text in text_labels:
                vertical_layout.addWidget(text)
            vertical_layout.setAlignment(Qt.AlignCenter)

            horizontal_layout = QHBoxLayout()
            horizontal_layout.setAlignment(Qt.AlignCenter)
            horizontal_layout.addWidget(album_art)
            horizontal_layout.addLayout(vertical_layout)

            main_widget.setLayout(horizontal_layout)

            return main_widget

    def create_playlist(self):
        self.playlist = QListWidget(self)

    def select_music_dir(self):
        dir = QFileDialog.getExistingDirectory(self, "Select Music Directory")
        if dir:
            self.music_dir = dir
            self.settings.setValue("musicDir", dir)
            write_albums_and_artists_to_files(dir)

    def load_dir(self, directory, user_artist, user_album):
        album_holder = Album()
        self.playlist.clear()
        self.track_numbers.clear()

        if not user_artist or not user_album:
            return album_holder

        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file.lower().endswith(('.mp3')):
                    if file.lower().endswith('.mp3'):
                        audio = EasyID3(file_path)
                        length = MP3(file_path).info.length
                        length = self.format_time(length)

                    title = audio.get('title', [''])[0]
                    artist = audio.get('artist', [''])[0]
                    album = audio.get('album', [''])[0]
                    track_number = audio.get('tracknumber', [''])[0]
                    genre = audio.get('genre', [''])[0]
                    year = audio.get('date', [''])[0]
                    if (length is None):
                        length = 'UNKNOWN'
                    
                    if not (self.compare_strings(user_artist, artist) and self.compare_strings(user_album, album)):
                        continue

                    song = Song(
                        title,
                        artist,
                        album,
                        track_number,
                        genre,
                        year,
                        length,
                        file_path
                    )
                    album_holder.add_song(song)

        album_holder.sort_track_list()

        for song in album_holder.get_track_list():
            widget_item = QListWidgetItem(self.playlist)
            widget = TrackInfoWidget(song.track_number, song.title, song.length, song.file_path)
            self.track_numbers.append(song.track_number)
            widget.setStyleSheet("background-color:transparent;")
            widget_item.setSizeHint(widget.sizeHint())
            self.playlist.setItemWidget(widget_item, widget)
        
        if self.playlist.count() == 0:
            print("No music files found in the selected directory.")
        
        return album_holder
        
    def compare_strings(self, string1, string2):
        edited_string1 = string1.replace(' ', '').lower()
        edited_string2 = string2.replace(' ', '').lower()
        return edited_string1 == edited_string2
    
    def format_time(self, seconds):
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"

    def create_side_menu(self):
        side_menu_widget = QWidget()
        side_menu_layout = QVBoxLayout(side_menu_widget)
    
        menu_list = QListWidget()
        menu_list.setStyleSheet('font-size: 20px;')
        menu_list.addItem('Home')
        menu_list.addItem('Swap Album')
        menu_list.addItem('Settings')
        menu_list.addItem('Help')
        side_menu_layout.addWidget(menu_list)

        menu_list.itemClicked.connect(self.side_menu_clicked)
        shortcut = QShortcut(QKeySequence("Ctrl+S"), side_menu_widget)
        shortcut.activated.connect(self.swap_album)

        self.create_playback_controls(side_menu_layout)
        self.create_progress_controls(side_menu_layout)

        side_menu_widget.setFixedWidth(260)
        return side_menu_widget
    
    def swap_album(self):
        input = InputDialog()
        main_window_position = self.mapToGlobal(self.rect().center())
        x = main_window_position.x() - (input.width() // 2) + 275
        y = main_window_position.y() - (input.height() // 2) + 100
        input.move(x, y)
        input.exec()
        user_artist, user_album = input.get_user_input()
        self.main(user_artist, user_album)
    
    def side_menu_clicked(self, item):
        if item.text() == 'Swap Album':
            input = InputDialog()
            main_window_position = self.mapToGlobal(self.rect().center())
            x = main_window_position.x() - (input.width() // 2) + 275
            y = main_window_position.y() - (input.height() // 2) + 100
            input.move(x, y)
            input.exec()
            user_artist, user_album = input.get_user_input()
            self.main(user_artist, user_album)
        if item.text() == 'Settings':
            self.show_settings()
        if item.text() == 'Help':
            self.show_help()
    
    def show_help(self):
        help_dialog = QDialog() 
        layout = QVBoxLayout()
        help_dialog.setLayout(layout)

        title = QLabel("<h1>Help Window</h1>")
        space_text = QLabel("")
        help_header1 = QLabel("<h2>Shortcuts</h2>")
        shortcut1 = QLabel("Ctrl+S: Swap Albums, auto-complete when typing in swap menu, cycle through auto-complete options while in swap menu")
        shortcut2 = QLabel("SpaceBar: Play, and pause music")
        shortcut3 = QLabel("NumberKeys(1,2,3,4,5...,0): the same number will play the associated track number, and also pause it")
        shortcut4 = QLabel("Ctrl+NumberKeys(1,2,3,4,5...0): same as above but for track numbers 11 - 20")
        help_header2 = QLabel("<h2>Tips</h2>")
        help_text1 = QLabel("Press Ctrl+S to open a popup to swap albums.")
        help_text2 = QLabel("If you press Ctrl+S in the Swap menu while typing something, it will auto complete what you have typed with available options from your library. Press Ctrl+S again to cycle through the options. Clear the input box, or erase some letters and type something new to get new options with Ctrl+S.")
        help_text3 = QLabel("The play button is also the pause button, after selecting a song press the play button to play it, then press it again to pause it.")
        help_text4 = QLabel("You can also press the SpaceBar instead of pressing the play button to play and pause the music.")
        help_text5 = QLabel("The number keys are associated with each track number. So pressing the number 1 key will play the first track and pressing it again will pause it. Pressing the 0 key will play the 10th track, and anything from 11 - 20 you press Ctrl+# to play. For example Ctrl+5 it will play the 15th track.")
        widgets = [
            title, space_text, help_header1, shortcut1, shortcut2, shortcut3, shortcut4,
            help_header2, help_text1, help_text2, help_text3, help_text4, help_text5
            ]

        for widget in widgets:
            layout.addWidget(widget)
            widget.setWordWrap(True)
        
        help_dialog.setFixedWidth(400)
        help_dialog.setWindowTitle("Help")
        main_window_position = self.mapToGlobal(self.rect().center())
        x = main_window_position.x() - (help_dialog.width() // 2)
        y = main_window_position.y() - (help_dialog.height() // 2)
        help_dialog.move(x, y)

        help_dialog.exec()


#-----PLAYBACK & PROGRESS CONTROLS ------------------------------------------------------------------------
    def create_playback_controls(self, layout):
        playback_layout = QHBoxLayout()

        self.shuffle_button = QPushButton(self)
        self.shuffle_button.setText("SHUFFLE")
        self.shuffle_button.setCheckable(True)
        playback_layout.addWidget(self.shuffle_button)

        self.repeat_button = QPushButton(self)
        self.repeat_button.setText("REPEAT")
        self.repeat_button.setCheckable(True)
        playback_layout.addWidget(self.repeat_button)

        self.backwards_button = QPushButton(self)
        self.backwards_button.setText("<-")
        playback_layout.addWidget(self.backwards_button)

        self.play_pause_button = QPushButton(self)
        self.play_pause_button.setText("PLAY")
        self.play_pause_button.setFixedWidth(50)
        playback_layout.addWidget(self.play_pause_button)

        self.forwards_button = QPushButton(self)
        self.forwards_button.setText("->")
        playback_layout.addWidget(self.forwards_button)

        self.play_pause_button.clicked.connect(self.play_pause_control)
        self.shuffle_button.clicked.connect(self.toggle_shuffle)
        self.repeat_button.clicked.connect(self.toggle_repeat)
        self.backwards_button.clicked.connect(self.prev_song)
        self.forwards_button.clicked.connect(self.next_song)

        shortcut = QShortcut(QKeySequence("Space"), self)
        shortcut.activated.connect(self.play_pause_control)

        layout.addLayout(playback_layout)

        volume_layout = QHBoxLayout()
        volume_label = QLabel("VOL.")
        self.volume_slider = QSlider(Qt.Horizontal, self)
        self.volume_slider.sliderMoved.connect(self.set_volume)
        current_volume = pygame.mixer.music.get_volume() * 100
        self.volume_slider.setValue(current_volume)
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        layout.addLayout(volume_layout)

        self.shuffle_button.setStyleSheet("""
    QPushButton {
        border: 1px solid #CCCCCC;
        background-color: #F5F5F5;
        padding: 5px;
        border-radius: 4px;
        color: #333333;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #000000;
        color: #FFFFFF;
    }
    QPushButton:pressed {
        background-color: #5CB1FF;
    }
""")
        self.repeat_button.setStyleSheet("""
    QPushButton {
        border: 1px solid #CCCCCC;
        background-color: #F5F5F5;
        padding: 5px;
        border-radius: 4px;
        color: #333333;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #000000;
        color: #FFFFFF;
    }
    QPushButton:pressed {
        background-color: #5CB1FF;
    }
""")
        self.play_pause_button.setStyleSheet("""
    QPushButton {
        border: 1px solid #CCCCCC;
        background-color: #F5F5F5;
        padding: 5px;
        border-radius: 4px;
        color: #333333;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #000000;
        color: #FFFFFF;
    }
    QPushButton:pressed {
        background-color: #5CB1FF;
    }
""")
        self.forwards_button.setStyleSheet("""
    QPushButton {
        border: 1px solid #CCCCCC;
        background-color: #F5F5F5;
        padding: 5px;
        border-radius: 4px;
        color: #333333;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #000000;
        color: #FFFFFF;
    }
    QPushButton:pressed {
        background-color: #5CB1FF;
    }
""")
        self.backwards_button.setStyleSheet("""
    QPushButton {
        border: 1px solid #CCCCCC;
        background-color: #F5F5F5;
        padding: 5px;
        border-radius: 4px;
        color: #333333;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #000000;
        color: #FFFFFF;
    }
    QPushButton:pressed {
        background-color: #5CB1FF;
    }
""")

    def create_progress_controls(self, layout):
        progress_layout = QHBoxLayout()
        self.current_time_label = QLabel("0:00", self)
        self.slider = QSlider(Qt.Horizontal, self)
        self.total_time_label = QLabel("0:00", self)
        progress_layout.addWidget(self.current_time_label)
        progress_layout.addWidget(self.slider)
        progress_layout.addWidget(self.total_time_label)
        self.slider.sliderReleased.connect(self.slider_released)
        layout.addLayout(progress_layout)


#-----PLAYBACK & PROGRESS CONTROLS LOGIC------------------------------------------------------------------------
    def set_volume(self, value):
        pygame.mixer.music.set_volume(value / 100)

    def toggle_mute(self, checked):
        if checked:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(self.volume_slider.value() / 100)

    def toggle_repeat(self, checked):
        self.repeat = checked
        if self.repeat:
            self.repeat_button.setStyleSheet("""
    QPushButton {
        border: 1px solid #CCCCCC;
        background-color: #5CB1FF;
        padding: 5px;
        border-radius: 4px;
        color: #333333;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #000000;
        color: #FFFFFF;
    }
    QPushButton:pressed {
        background-color: #5CB1FF;
    }
""")
        else:
             self.repeat_button.setStyleSheet("""
    QPushButton {
        border: 1px solid #CCCCCC;
        background-color: #F5F5F5;
        padding: 5px;
        border-radius: 4px;
        color: #333333;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #000000;
        color: #FFFFFF;
    }
    QPushButton:pressed {
        background-color: #5CB1FF;
    }
""")
             
    def toggle_shuffle(self, checked):
        self.shuffle = checked
        if self.shuffle:
            self.reset_shuffle()
            self.shuffle_button.setStyleSheet("""
    QPushButton {
        border: 1px solid #CCCCCC;
        background-color: #5CB1FF;
        padding: 5px;
        border-radius: 4px;
        color: #333333;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #000000;
        color: #FFFFFF;
    }
    QPushButton:pressed {
        background-color: #5CB1FF;
    }
""")
        else:
             self.shuffle_button.setStyleSheet("""
    QPushButton {
        border: 1px solid #CCCCCC;
        background-color: #F5F5F5;
        padding: 5px;
        border-radius: 4px;
        color: #333333;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #000000;
        color: #FFFFFF;
    }
    QPushButton:pressed {
        background-color: #5CB1FF;
    }
""")

    def play_pause_control(self, override=""):
        self.play_pause_button.setText("PAUSE")
        self.play_pause_button.setStyleSheet("""
        QPushButton {
            border: 1px solid #CCCCCC;
            background-color: #5CB1FF;
            padding: 5px;
            border-radius: 4px;
            color: #333333;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #000000;
            color: #FFFFFF;
        }
        QPushButton:pressed {
            background-color: #5CB1FF;
        }
    """)
        widget = self.playlist.itemWidget(self.playlist.currentItem())
        if override == "play" or (isinstance(self.sender(), QPushButton) and self.current_song !=  widget.song_path):
            self.play_selected()
        elif not pygame.mixer.music.get_busy():
            self.play_selected()
        elif pygame.mixer.music.get_busy():
            self.pause_music()
            self.play_pause_button.setText("PLAY")
            self.play_pause_button.setStyleSheet("""
        QPushButton {
            border: 1px solid #CCCCCC;
            background-color: #F5F5F5;
            padding: 5px;
            border-radius: 4px;
            color: #333333;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #000000;
            color: #FFFFFF;
        }
        QPushButton:pressed {
            background-color: #5CB1FF;
        }
    """)

    def play_selected(self):
        current_item = self.playlist.currentItem()
        
        if not current_item:
            return

        widget = self.playlist.itemWidget(current_item)
        if not widget:
            return

        song_path = widget.song_path 
        self.audio = MP3(song_path)
        self.timer.start(1000)
        self.total_time_label.setText(self.format_time(self.audio.info.length))

        if self.is_paused:
            if song_path == self.current_song:
                pygame.mixer.music.unpause()
                self.is_paused = False
                return
            else:
                pygame.mixer.music.stop()
                self.current_pos = 0
                self.is_paused = False

        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        self.current_song = song_path
        self.current_pos = 0

    def pause_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.is_paused = True

    def stop_music(self):
        pygame.mixer.music.stop()
        self.is_paused = False
        self.current_song = None

    def reset_shuffle(self):
        self.shuffled_list.clear()
        self.shuffle_index = 0

        current_index = self.playlist.currentRow()
        if not (current_index == -1 or current_index == self.playlist.count()):
            temp_list = []
            temp_list.append(self.track_numbers[current_index])
            temp_list_2 = self.track_numbers.copy()
            del temp_list_2[current_index]
            random.shuffle(temp_list_2)
            self.shuffle_list = temp_list + temp_list_2
        else:
            self.shuffle_list = self.track_numbers.copy()
            random.shuffle(self.shuffle_list)

    def next_song(self):
        if self.is_paused:
            self.is_paused = False

        current_index = self.playlist.currentRow()
        
        if current_index == -1 or current_index == self.playlist.count() - 1:
            next_index = 0
        else:
            next_index = current_index + 1

        if self.repeat:
            self.playlist.setCurrentRow(current_index)
            self.play_selected()
        elif self.shuffle:
            count = len(self.shuffle_list)
            count = count - 1
            if self.shuffle_index == -1 or self.shuffle_index == count:
                self.shuffle_index = 0
            else:
                self.shuffle_index = self.shuffle_index + 1
            
            converted_index = int(self.shuffle_list[self.shuffle_index]) - 1
            self.playlist.setCurrentRow(converted_index)
            self.play_selected()
        else:
            self.playlist.setCurrentRow(next_index)
            self.play_selected()

    def prev_song(self):
        if self.is_paused:
            self.is_paused = False
            
        current_index = self.playlist.currentRow()
        
        if current_index <= 0:
            prev_index = self.playlist.count() - 1
        else:
            prev_index = current_index - 1

        if self.repeat:
            self.playlist.setCurrentRow(current_index)
            self.play_selected()
        elif self.shuffle:
            count = len(self.shuffle_list)
            count = count - 1
            if self.shuffle_index == -1:
                self.shuffle_index = count
            else:
                self.shuffle_index = self.shuffle_index - 1
            
            converted_index = int(self.shuffle_list[self.shuffle_index]) - 1
            self.playlist.setCurrentRow(converted_index)
            self.play_selected()
        else:
            self.playlist.setCurrentRow(prev_index)
            self.play_selected()

    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.music_dir_line_edit.setText(self.music_dir)
        dialog.auto_refresh_check_box.setChecked(self.settings.value("autoRefresh", type=bool))
        result = dialog.exec()

        screen = app.primaryScreen().geometry()
        x = (screen.width() - dialog.width()) // 2
        y = (screen.height() - dialog.height()) // 2
        dialog.move(x, y)

        if result == QDialog.Accepted:
            self.music_dir = dialog.music_dir_line_edit.text()
            self.settings.setValue("musicDir", self.music_dir)
            
            auto_refresh = dialog.auto_refresh_check_box.isChecked()
            self.settings.setValue("autoRefresh", auto_refresh)
            
            if auto_refresh:
                self.load_dir(self.music_dir)

    def update_slider(self):
        if pygame.mixer.music.get_busy():
            self.current_pos += 1
            total_length = self.audio.info.length
            if not self.slider.isSliderDown():
                self.slider.setValue(int((self.current_pos / total_length) * 100))
            self.current_time_label.setText(self.format_time(self.current_pos))
        elif not self.is_paused:
            current_index = self.playlist.currentRow()
            last_item_index = self.playlist.count() - 1
            if self.shuffle:
                count = len(self.shuffle_list)
                count = count - 1
                if self.shuffle_index != count:
                    self.next_song()
            else:
                if current_index != last_item_index:
                    self.next_song()

    def slider_released(self):
        total_length = self.audio.info.length
        new_time = (self.slider.value() / 100) * total_length
        pygame.mixer.music.set_pos(new_time)
        self.current_pos = new_time

    def format_time(self, seconds):
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())


from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel
from PySide6.QtGui import QKeySequence, QShortcut
from get_directory_names import artists_text_directory, albums_text_directory

class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.artist = None
        self.album = None

        layout = QVBoxLayout()
        artist_label = QLabel("Artist:")
        self.artist_input = QLineEdit()
        layout.addWidget(artist_label)
        layout.addWidget(self.artist_input)

        album_label = QLabel("Album:")
        self.album_input = QLineEdit()
        layout.addWidget(album_label)
        layout.addWidget(self.album_input)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.handle_ok)
        layout.addWidget(ok_button)

        self.setLayout(layout)
        self.setWindowTitle("Enter Artist and Album")

        shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        shortcut.activated.connect(self.autocomplete_helper)

        self.artists, self.albums = self.read_words()
        self.matching_words = []
        self.current_word_index = 0
        self.past_focused_widget = self.artist_input

    def handle_ok(self):
        self.artist = self.artist_input.text()
        self.album = self.album_input.text()
        self.accept()

    def get_user_input(self):
        return self.artist, self.album

    def read_words(self):
        albums_file_path = albums_text_directory
        artists_file_path = artists_text_directory

        with open(artists_file_path, "r", encoding="utf-8") as file:
            artists = file.read().splitlines()

        with open(albums_file_path, "r", encoding="utf-8") as file:
            albums = file.read().splitlines()

        return artists, albums

    def autocomplete_helper(self):
        focused_widget = QApplication.focusWidget()
        if focused_widget == self.artist_input:
            words = self.artists
            print("artists selected")
        elif focused_widget == self.album_input:
            words = self.albums
            print("albums selected")
        if self.past_focused_widget != focused_widget:
            self.matching_words.clear()
            self.current_word_index = 0
        self.past_focused_widget = focused_widget

        current_text = self.sender().parent().focusWidget().text()
        print("Current text:", current_text)  

        if not current_text in self.matching_words:
            self.matching_words.clear()
            self.current_word_index = 0

        if self.matching_words:
            self.autocomplete_active()
        else:
            self.autocomplete(words, current_text)

    def autocomplete(self, words, current_text):
        if current_text:
            current_text_lower = current_text.lower() 
            self.matching_words = [word for word in words if word.lower().startswith(current_text_lower)]

            print("Matching words:", self.matching_words) 

            if self.matching_words:
                self.sender().parent().focusWidget().setText(self.matching_words[self.current_word_index])
                self.current_word_index = (self.current_word_index + 1) % len(self.matching_words)

                print("Current index:", self.current_word_index)

    def autocomplete_active(self):
        self.sender().parent().focusWidget().setText(self.matching_words[self.current_word_index])
        if self.current_word_index + 1 >= len(self.matching_words):
            self.current_word_index = 0
        else:
            self.current_word_index = self.current_word_index + 1

        print("Current index:", self.current_word_index)  

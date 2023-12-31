from song import convert_time_to_float
from mutagen.id3 import ID3
import eyed3


class Album():

    def __init__(self):
        self.title = ""
        self.artist = ""
        self.genre = ""
        self.year = ""
        self.album_art_path = ""

        self.track_list = []
        self.length = 0.0
        self.track_count = 0

    def get_track_list(self):
        return self.track_list

    def sort_track_list(self):
        self.track_list = sorted(self.track_list, key=lambda song: song.track_number)

    def add_song(self, song):
        self.track_list.append(song)
        self.length = self.length + convert_time_to_float(song.length)
        self.track_count += 1

        if not self.title:
            self.title = song.album
        if not self.artist:
            self.artist = song.artist
        if not self.genre:
            self.genre = song.genre
        if not self.year:
            self.year = song.year
        if not self.album_art_path:
            audiofile = eyed3.load(song.file_path)
            if audiofile.tag and audiofile.tag.images:
                for image in audiofile.tag.images:
                    if image.picture_type == eyed3.id3.frames.ImageFrame.FRONT_COVER:
                        # Album art found, set song path to variable
                        self.album_art_path = song.file_path
                        print("Album art found!")
                        break
                else:
                    print("No album art found in the file.")
            else:
                print("No tags available in the file.")



    def __str__(self):
        track_list_str = "\n".join([f"    {track}\n" for track in self.track_list])
        return (
            f"Title: {self.title}\n"
            f"Artist: {self.artist}\n"
            f"Genre: {self.genre}\n"
            f"Year: {self.year}\n"
            f"Number of Tracks: {self.track_count}\n"
            f"Total Length: {self.length / 60} minutes\n"
            f"Tracks:\n{track_list_str}"
        )
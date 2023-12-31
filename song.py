
class Song():
    def __init__(self, title, artist, album, track_number, genre, year, length, file_path):
        self.title = title
        self.artist = artist
        self.album = album

        if "/" in track_number:
            track_num, total_tracks =  map(int, track_number.split('/'))
            self.track_number = track_num
        else:
            self.track_number = track_number
        
        self.genre = genre
        self.year = year
        self.length = length
        self.file_path = file_path
    
    def __str__(self):
         return f"Title: {self.title}\nArtist: {self.artist}\nAlbum: {self.album}\nTrack Number: {self.track_number}\nGenre: {self.genre}\nYear: {self.year}\nLength: {self.length}\nFile Path: {self.file_path}"
    
def convert_time_to_float(time_str):
    minutes, seconds = map(float, time_str.split(':'))
    if (minutes > 1.0):
        minutes = minutes * 60
    return minutes + seconds


import os, sys
from mutagen.easyid3 import EasyID3

current_dir = os.path.dirname(os.path.abspath(__file__))
artists_text_directory = os.path.join(current_dir, 'Assets', 'artists.txt')
current_dir = os.path.dirname(os.path.abspath(__file__))
albums_text_directory = os.path.join(current_dir, 'Assets', 'albums.txt')

def write_to_file(file_path, data):
    with open(file_path, 'w'): 
        pass 

    with open(file_path, 'w', encoding='utf-8', errors='ignore') as file:
        for item in data:
            file.write(f"{item}\n")

def get_mp3_albums(directory):
    albums_by_artist = {}

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                try:
                    audio = EasyID3(file_path)
                    if 'artist' in audio and 'album' in audio:
                        artist_name = audio['artist'][0]
                        album_name = audio['album'][0]
                        if artist_name not in albums_by_artist:
                            albums_by_artist[artist_name] = set()
                        albums_by_artist[artist_name].add(album_name)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    return albums_by_artist

def write_albums_and_artists_to_files(directory_to_search):
    albums = get_mp3_albums(directory_to_search)

    if albums:
        artist_file_path = artists_text_directory
        album_file_path = albums_text_directory
        
        artists = sorted(albums.keys())
        albums_list = []
        for artist, albums_set in sorted(albums.items()):
            albums_list.extend(sorted(albums_set))

        write_to_file(artist_file_path, artists)
        write_to_file(album_file_path, albums_list)
        
        print("Successfully created files: 'artists.txt' and 'albums.txt'")
    else:
        print("No albums found.")


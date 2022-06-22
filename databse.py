import sqlite3
import csv

class Database:
    def __init__(self, name):
        self.db = sqlite3.connect(name)
        self.cursor = self.db.cursor()

    def setup_db(self):
        # usunięcie poprzednich tabel
        self.cursor.execute("DROP TABLE IF EXISTS genres")
        self.cursor.execute("DROP TABLE IF EXISTS artists")
        self.cursor.execute("DROP TABLE IF EXISTS tracks")
        self.cursor.execute("DROP TABLE IF EXISTS performs")
        self.cursor.execute("DROP TABLE IF EXISTS song_genres")

        self.db.commit()

        # stworzenie nowych tabel
        self.cursor.execute("CREATE TABLE genres (code integer primary key, genre string)")
        self.cursor.execute("CREATE TABLE artists (code integer primary key, alias string)")
        self.cursor.execute("CREATE TABLE tracks (code integer primary key, name string, music_url string, cover_url string)")
        self.cursor.execute("CREATE TABLE performs (song integer, artist integer, foreign key(song) references tracks(code), foreign key(artist) references artists(code))")
        self.cursor.execute("CREATE TABLE song_genres (song_code integer, genre_code integer, foreign key(song_code) references tracks(code), foreign key(genre_code) references genres(code))")

        self.db.commit()

    # pobieranie danych z pliku csv
    def download_data(self):
        # garunki muzyczne
        with open('genres.csv', 'r') as file:
            reader = csv.reader(file, delimiter=';')

            for row in reader:
                self.cursor.execute("INSERT INTO genres (code, genre) VALUES (?,?)", (row[0], row[1]))

        self.db.commit()

        # artyści
        with open('artists.csv', 'r') as file:
            reader = csv.reader(file, delimiter=';')

            for row in reader:
                self.cursor.execute("INSERT INTO artists (code, alias) VALUES (?, ?)", (row[0], row[1]))

        self.db.commit()

        # utwory
        with open('tracks.csv', 'r') as file:
            reader = csv.reader(file, delimiter=';')

            for row in reader:
                self.cursor.execute("INSERT INTO tracks (code, name, music_url, cover_url) VALUES (?, ?, ?, ?)", (row[0], row[1], row[2], row[3]))

        self.db.commit()

        # wykonawcy danych utworów
        with open('performs.csv', 'r') as file:
            reader = csv.reader(file, delimiter=';')

            for row in reader:
                self.cursor.execute("INSERT INTO performs (song, artist) VALUES (?, ?)", (row[0], row[1]))

        self.db.commit()

        # gatunki dla danych utworów
        with open('song_genres.csv', 'r') as file:
            reader = csv.reader(file, delimiter=';')

            for row in reader:
                self.cursor.execute("INSERT INTO song_genres (song_code, genre_code) VALUES (?, ?)", (row[0], row[1]))

        self.db.commit()


    def get_url(self, song_number):
        element = self.cursor.execute("SELECT music_url FROM tracks WHERE code=?", (song_number, ))
        return element.fetchall()[0][0]

    def get_artists(self, song_number):
        element = self.cursor.execute("SELECT artist FROM performs WHERE song=?", (song_number,))

        artists = ''

        for artist_code in element.fetchall():
            artist = self.cursor.execute("SELECT alias FROM artists WHERE code=?", (artist_code[0],))
            artists += artist.fetchall()[0][0] + " / "

        artists = artists[:-3]

        return artists

    def get_song_name(self, song_number):
        element = self.cursor.execute("SELECT name FROM tracks WHERE code=?", (song_number,))
        return element.fetchall()[0][0]

    def count_songs(self):
        element = self.cursor.execute("SELECT COUNT(*) FROM tracks")
        return element.fetchall()[0][0]
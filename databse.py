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
        self.cursor.execute("DROP TABLE IF EXISTS results")

        self.db.commit()

        # stworzenie nowych tabel
        self.cursor.execute("CREATE TABLE genres (code integer primary key, genre string)")
        self.cursor.execute("CREATE TABLE artists (code integer primary key, alias string)")
        self.cursor.execute("CREATE TABLE tracks (code integer primary key, name string, music_url string, cover_url string)")
        self.cursor.execute("CREATE TABLE performs (song integer, artist integer, foreign key(song) references tracks(code), foreign key(artist) references artists(code))")
        self.cursor.execute("CREATE TABLE song_genres (song_code integer, genre_code integer, foreign key(song_code) references tracks(code), foreign key(genre_code) references genres(code))")
        self.cursor.execute("CREATE TABLE results (player_name string primary key, player_points int)")

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

    def get_song_url(self, song_number):
        element = self.cursor.execute("SELECT music_url FROM tracks WHERE code=?", (song_number, ))
        return element.fetchall()[0][0]

    def get_cover_url(self, song_number):
        element = self.cursor.execute("SELECT cover_url FROM tracks WHERE code=?", (song_number, ))
        return element.fetchall()[0][0]

    def get_artists(self, song_number):
        element = self.cursor.execute("SELECT artist FROM performs WHERE song=?", (song_number,))

        artists = ''

        for artist_code in element.fetchall():
            artist = self.cursor.execute("SELECT alias FROM artists WHERE code=?", (artist_code[0],))
            artists += artist.fetchall()[0][0] + " / "

        artists = artists[:-3]

        return artists

    def get_song_genres(self, song_number):
        element = self.cursor.execute("SELECT genre_code FROM song_genres WHERE song_code=?", (song_number,))

        genres = []

        for genre_code in element.fetchall():
            genre = self.cursor.execute("SELECT genre FROM genres WHERE code=?", (genre_code[0],))
            genres.append(genre.fetchall()[0][0])

        return genres

    def get_song_name(self, song_number):
        element = self.cursor.execute("SELECT name FROM tracks WHERE code=?", (song_number,))
        return element.fetchall()[0][0]

    def count_songs(self):
        element = self.cursor.execute("SELECT COUNT(*) FROM tracks")
        return element.fetchall()[0][0]

    def get_songs_by_genre(self, genre_code):
        element = self.cursor.execute("SELECT tracks.code FROM tracks INNER JOIN song_genres ON tracks.code = song_genres.song_code INNER JOIN genres ON song_genres.genre_code = genres.code WHERE genres.code=?", (genre_code, ))
        return element.fetchall()

    def get_all_genres(self):
        element = self.cursor.execute("SELECT genre FROM genres")

        genres = []

        for genre in element.fetchall():
            genres.append(genre[0])

        return genres

    def get_genre_code(self, genre_name):
        element = self.cursor.execute("SELECT code FROM genres WHERE genre=?", (genre_name, ))
        return element.fetchone()[0]

    def save_results(self, players_info):
        for player in players_info:
            element = self.cursor.execute("SELECT * FROM results WHERE player_name=?", (player[0],))

            row = element.fetchone()

            if row is not None:
                self.cursor.execute("UPDATE results SET player_points=? WHERE player_name=?", (row[1] + player[1], row[0]))
            else:
                self.cursor.execute("INSERT INTO results (player_name, player_points) VALUES (?, ?)", (player[0], player[1]))

            self.db.commit()

    def get_results(self):
        element = self.cursor.execute("SELECT * FROM results")
        return element.fetchall()
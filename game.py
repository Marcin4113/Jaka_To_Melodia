import random

from kivy.graphics.svg import Window
from kivy.properties import NumericProperty
from kivy.uix.screenmanager import Screen
import time
import threading
import pafy
import vlc
from databse import Database

no_of_players = 1
players_name = ['Marcin']


class Game(Screen):
    global players_name
    current_player = 0
    playback_time = 0
    song_playing = False

    # konstruktor
    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        self.player = None
        self.play_song_thread = None

    # przy uruchomieniu okna
    def on_enter(self, *args):
        #Window.fullscreen = 'auto'
        Window.bind(on_key_down=self.key_action)

        self.setup_screen()

        self.db = Database("database.db")
        self.db.setup_db()
        self.db.download_data()

    # ustawienia początkowe ekranu dla danego gracza (ustawienie nazwy, okładki i pobranie piosenki)
    def setup_screen(self):
        self.ids.label.text = "Gracz " + players_name[self.current_player]

    # wciśnięcie przycisku
    def key_action(self, *args):
        #print("got a key event: %s" % args[3])

        # jeżeli naciśnięto spację to zacznij odtwarzać fragment / zatrzymaj odtwarzany fragment
        if args[3] == ' ':
            if not self.song_playing:
                self.song_playing = True

                song_number = random.randint(1, self.db.count_songs()) #losowanie piosenki
                print(self.db.get_artists(song_number) + " - " + self.db.get_song_name(song_number))

                play_song_thread = threading.Thread(target=self.play_song, args=(self.db.get_url(song_number), )) # sprawdzić czy trzeba zapisywać wątek w klasie
                play_song_thread.start()
            else:
                self.song_playing = False
                self.current_player += 1

                if int(self.current_player) >= int(no_of_players):
                    self.current_player = 0

                self.setup_screen()

    # otwarzanie piosenki
    def play_song(self, url):
        # jeżeli piosenka była już puszczona to drugi raz jej nie odtwarzaj
        if self.ids.progress_bar.value > 0:
            return

        self.ids.info.text = "Ładowanie utworu..."
        video = pafy.new(url)
        best = video.getbestaudio()
        playurl = best.url
        self.player = vlc.MediaPlayer(playurl)
        self.player.play() # odtworzenie piosenki

        while not self.player.is_playing():
            pass

        self.ids.info.text = "Naciśnij spację, aby zatrzymać utwór!"

        # pętla odtwarzająca utwór
        while self.ids.progress_bar.value < 100:
            if not self.song_playing:
                break

            time.sleep(0.01)
            #self.playback_time += 0.1
            self.ids.progress_bar.value += 0.05

        # koniec odtwarzania
        self.ids.info.text = "Podaj odpowiedź:"
        self.player.stop()
        self.ids.progress_bar.value = 0
        self.song_playing = False


class PrepareGameNoOfPlayers(Screen):
    def save_no_of_players(self, widget):
        global no_of_players
        no_of_players = self.ids.no_of_players.text
        self.parent.current = "prepare_game_players_name"


class PrepareGamePlayersName(Screen):
    current_player = NumericProperty(1)

    def on_enter(self, *args):
        players_name.clear()
        self.check_counter()

    def check_counter(self):
        if int(no_of_players) <= int(self.current_player):
            self.ids.button_number_next.text = "Rozpocznij grę!"
            self.ids.button_number_next.bind(on_release=self.start_game)
            self.ids.player_name.bind(on_text_validate=self.start_game)

    def save_name(self, widget):
        #print("Player name: " + self.ids.player_name.text)
        players_name.append(self.ids.player_name.text)  # przypisanie nazwy gracza do tablicy
        self.ids.player_name.text = ""
        self.current_player += 1

        print(str(self.current_player) + "/" + str(no_of_players))
        self.check_counter()

    def start_game(self, value):
        self.manager.current = 'game'

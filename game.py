from kivy.graphics.svg import Window
from kivy.properties import NumericProperty
from kivy.uix.screenmanager import Screen
import time
import threading
import pafy
import vlc

no_of_players = 0
players_name = []

class Game(Screen):
    global players_name
    current_player = 0
    playback_time = 0
    song_playing = False

    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        self.player = None
        self.play_song_thread = None

    def on_enter(self, *args):
        Window.fullscreen = 'auto'
        Window.bind(on_key_down=self.key_action)
        self.setup_screen()

    # ustawienia początkowe ekranu dla danego gracza (ustawienie nazwy, okładki i pobranie piosenki)
    def setup_screen(self):
        self.ids.label.text = "Gracz " + players_name[self.current_player]

    def key_action(self, *args):
        print("got a key event: %s" % args[3])

        # jeżeli naciśnięto spację to zacznij odtwarzać fragment / zatrzymaj odtwarzany fragment
        if args[3] == ' ':
            if not self.song_playing:
                self.song_playing = True
                self.play_song_thread = threading.Thread(
                    target=self.play_song)  # sprawdzić czy trzeba zapisywać wątek w klasie
                self.play_song_thread.start()
            else:
                self.song_playing = False
                self.current_player += 1

                if int(self.current_player) >= int(no_of_players):
                    self.current_player = 0

                self.setup_screen()

    def play_song(self):
        # jeżeli piosenka była już puszczona to drugi raz jej nie odtwarzaj
        if self.ids.progress_bar.value > 0:
            return

        url = "https://www.youtube.com/watch?v=1f4snkig1nM"
        video = pafy.new(url)
        best = video.getbestaudio()
        playurl = best.url
        self.player = vlc.MediaPlayer(playurl)
        self.player.play() # odtworzenie piosenki

        while not self.player.is_playing():
            pass

        for x in range(0, 1000):
            if not self.song_playing:
                break

            time.sleep(0.01)
            self.playback_time += 0.1
            self.ids.progress_bar.value = self.playback_time

        self.player.stop()


class PrepareGameNoOfPlayers(Screen):
    def save_no_of_players(self, widget):
        global no_of_players
        no_of_players = self.ids.no_of_players.text
        self.parent.current = "prepare_game_players_name"


class PrepareGamePlayersName(Screen):
    current_player = NumericProperty(1)

    def on_enter(self, *args):
        self.check_counter()

    def check_counter(self):
        if int(no_of_players) <= int(self.current_player):
            self.ids.button_number_next.text = "Rozpocznij grę!"
            self.ids.button_number_next.bind(on_release=self.start_game)
            self.ids.player_name.bind(on_text_validate=self.start_game)

    def save_name(self, widget):
        print("Player name: " + self.ids.player_name.text)
        players_name.append(self.ids.player_name.text)  # przypisanie nazwy gracza do tablicy
        self.ids.player_name.text = ""
        self.current_player += 1

        print(str(self.current_player) + "/" + str(no_of_players))
        self.check_counter()

    def start_game(self, value):
        self.manager.current = 'game'

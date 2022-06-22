import random
import difflib
from kivy.graphics.svg import Window
from kivy.properties import NumericProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
import time
import threading
import pafy
import vlc
from kivy.uix.textinput import TextInput
from databse import Database
from results import ResultsGame

song_genre_code = 3
no_of_players = 1
players_info = [['Maracin', 0]]

volume = 100


class Game(Screen):
    global players_info
    current_player = 0
    playback_time = 0
    song_playing = False
    answering = False
    is_game_end = False

    # konstruktor
    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        self.song_number = None
        self.player = None
        self.play_song_thread = None
        self.round_number = 1
        self.answer_input = TextInput(multiline=False, size_hint=(0.5, 0.7), on_text_validate=self.check_answer)
        self.answer_button = Button(text="Sprawdź!", size_hint=(0.5, 0.7), on_release=self.check_answer)

    # przy uruchomieniu okna
    def on_enter(self, *args):
        # Window.fullscreen = 'auto'
        Window.bind(on_key_down=self.key_action)
        self.round_number = 1
        self.ids.info.text = "Naciśnij spację aby rozpocząć odsłuchiwanie fragmentu!"
        self.is_game_end = False

        for player in players_info:
            player[1] = 0

        self.setup_screen()

        self.db = Database("database.db")
        print(self.db.get_all_genres())
        # self.db.setup_db()
        # self.db.download_data()

    # sprawdzanie czy podany tekst jest podobny do wzorca
    def similar(self, seq1, seq2):
        return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio() > 0.9

    def next_player(self):
        # przesuwanie do następnego gracza
        self.current_player += 1

        if int(self.current_player) >= int(no_of_players):
            self.current_player = 0
            self.round_number += 1

            #koniec rozgrywki
            if self.round_number > 1:
                self.is_game_end = True
                self.end_game()

    def check_answer(self, widget):
        self.ids.progress_bar.value = 0
        #print("text: " + self.answer_input.text)

        # sprawdzanie czy odpowiedzi są podobne
        good_answer = self.db.get_artists(self.song_number) + " - " + self.db.get_song_name(self.song_number)
        is_good_answer = self.similar(good_answer, self.answer_input.text)

        if is_good_answer:
            player = vlc.MediaPlayer("audio//clap.mp3")
            player.play()  # odtworzenie klaskania

            self.ids.box_game.remove_widget(self.answer_input)
            self.ids.box_game.remove_widget(self.answer_button)

            players_info[self.current_player][1] += self.points_to_gain
            self.next_player()

            if not self.is_game_end:
                self.ids.info.text = "Brawo! Zdobywasz: " + str(self.points_to_gain) + " punktów!" + \
                                     "\nNaciśnij spację, by gracz " + players_info[
                                         self.current_player][0] + " rozpoczął odsłuch fragmentu!"
                self.player.play()
        else:
            self.ids.box_game.remove_widget(self.answer_input)
            self.ids.box_game.remove_widget(self.answer_button)
            self.next_player()
            self.ids.info.text = "Niestety nie jest to dobra odpowiedź!" \
                                 "\nPrawidłowa odpowiedź to: " + good_answer + \
                                 "\nNaciśnij spację, by gracz " + players_info[
                                     self.current_player][0] + " rozpoczął odsłuch fragmentu!"

        self.answer_input.text = ""
        self.answering = False

    # ustawienia początkowe ekranu dla danego gracza (ustawienie nazwy i okładki piosenki)
    def setup_screen(self):
        #print(players_info)
        self.ids.label.text = "Runda: " + str(self.round_number) + "\nGracz " + players_info[self.current_player][0] + " | Liczba punktów: " + str(players_info[self.current_player][1])

    # wciśnięcie przycisku
    def key_action(self, *args):
        if self.is_game_end:
            return
        # print("got a key event: %s" % args[3])

        # jeżeli naciśnięto spację to zacznij odtwarzać fragment / zatrzymaj odtwarzany fragment
        if args[3] == ' ' and not self.answering:
            if not self.song_playing:
                if self.player != None:
                    self.player.stop()

                self.song_playing = True
                self.setup_screen()

                songs_from_one_genre = self.db.get_songs_by_genre(song_genre_code) #pobieranie piosenek tylko z jednego gatunku
                song_number_from_one_genre = random.randint(0, len(songs_from_one_genre)-1)  # losowanie piosenki

                #print("songs_from_one_genre: " + str(songs_from_one_genre))
                #print("size: " + str(len(songs_from_one_genre)))
                #print("song_number_from_one_genre: " + str(song_number_from_one_genre))
                self.song_number = songs_from_one_genre[song_number_from_one_genre][0]

                print(self.db.get_artists(self.song_number))
                print(self.db.get_song_name(self.song_number))
                print(self.db.get_song_genres(self.song_number))

                # print(self.db.get_artists(self.song_number) + " - " + self.db.get_song_name(self.song_number))
                play_song_thread = threading.Thread(target=self.play_song, args=(self.db.get_url(self.song_number),))  # sprawdzić czy trzeba zapisywać wątek w klasie
                play_song_thread.start()
            else:
                # koniec odtwarzania
                self.player.set_pause(1)
                self.song_playing = False
                self.get_answer()

    # wyświetlenie monitu o podanie odpowiedzi
    def get_answer(self):
        self.answering = True
        self.points_to_gain = int((110 - self.ids.progress_bar.value) * 10)

        self.ids.info.text = "Punkty do zdobycia: " + str(self.points_to_gain) + ".\nPodaj odpowiedź:"
        self.ids.box_game.add_widget(self.answer_input)
        self.ids.box_game.add_widget(self.answer_button)

    # otwarzanie piosenki
    def play_song(self, url):
        #print(self.ids.progress_bar.value)
        # jeżeli piosenka była już puszczona to drugi raz jej nie odtwarzaj
        if self.ids.progress_bar.value > 0:
            return

        self.ids.info.text = "Ładowanie utworu..."

        playing = False

        while not playing:
            #print("ładowanie")
            self.video = pafy.new(url)
            self.best = self.video.getbestaudio()
            self.playurl = self.best.url
            self.player = vlc.MediaPlayer(self.playurl)
            self.player.play()  # odtworzenie piosenki

            for i in range(0, 10):
                if self.player.is_playing():
                    break
                time.sleep(0.5)

            if self.player.is_playing():
                #print("dziala")
                playing = True
                break
            else:
                self.player.stop()

        self.ids.info.text = "Naciśnij spację, aby zatrzymać utwór i podać odpowiedź!"

        # pętla odtwarzająca utwór
        while self.ids.progress_bar.value < 100:
            if not self.song_playing:
                break

            time.sleep(0.01)
            # self.playback_time += 0.1
            self.ids.progress_bar.value += 0.05

        # wyzerowanie licznika czasu
        self.player.set_pause(1)

    def end_game(self):
        self.player.stop()
        self.db.save_results(players_info)
        res_game = ResultsGame()
        res_game.set_game_results(players_info)
        self.manager.current = 'results_game'



class PrepareGameNoOfPlayers(Screen):
    # przy uruchomieniu okna
    def on_enter(self, *args):
        self.db = Database("database.db")
        self.ids.spinner_genres.values = self.db.get_all_genres()

        #wczytanie głośności dźwięków


    def save_no_of_players(self, widget):
        global no_of_players, song_genre_code

        no_of_players = self.ids.no_of_players.text
        self.parent.current = "prepare_game_players_name"
        song_genre_code = self.db.get_genre_code(self.ids.spinner_genres.text)

class PrepareGamePlayersName(Screen):
    current_player = NumericProperty(1)

    def on_enter(self, *args):
        players_info.clear()
        self.check_counter()

    def check_counter(self):
        if int(no_of_players) <= int(self.current_player):
            self.ids.button_number_next.text = "Rozpocznij grę!"
            self.ids.button_number_next.bind(on_release=self.start_game)
            self.ids.player_name.bind(on_text_validate=self.start_game)

    def save_name(self, widget):
        # print("Player name: " + self.ids.player_name.text)
        players_info.append([self.ids.player_name.text, 0])  # przypisanie nazwy gracza do tablicy
        self.ids.player_name.text = ""
        self.current_player += 1

        print(str(self.current_player) + "/" + str(no_of_players))
        self.check_counter()

    def start_game(self, value):
        self.manager.current = 'game'

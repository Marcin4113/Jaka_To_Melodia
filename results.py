from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from databse import Database

players_info = []

class Results(Screen):
    def on_enter(self, *args):
        self.db = Database("database.db")
        self.print_game_results()

    def print_game_results(self):
        for player in self.db.get_results():
            self.ids.layout_results_table.add_widget(Label(text=(player[0] + " - " + str(player[1]) + " punktów"), font_size="40dp"))

    def go_back_menu(self, widget):
        self.ids.layout_results_table.clear_widgets()
        self.manager.current = "menu"

class ResultsGame(Screen):
    def __init__(self, **kw):
        super(ResultsGame, self).__init__()
        self.button_play_again = None

    def on_enter(self, *args):
        self.button_play_again = Button(text="Zagraj ponownie!", size_hint=(0.5, 0.3), pos_hint={"center_x": 0.5}, font_size="30dp", on_release=self.play_again)
        self.ids.layout_buttons_bottom.add_widget(self.button_play_again)
        self.print_game_results()

    def go_back_menu(self, widget):
        self.ids.layout_buttons_bottom.remove_widget(self.button_play_again)
        self.ids.layout_results_table.clear_widgets()
        self.manager.current = "menu"

    def play_again(self, widget):
        self.ids.layout_buttons_bottom.remove_widget(self.button_play_again)
        self.ids.layout_results_table.clear_widgets()
        self.manager.current = 'game'

    def set_game_results(self, players_inf):
        global players_info
        players_info = players_inf

    def print_game_results(self):
        print(players_info)
        for player in players_info:
            self.ids.layout_results_table.add_widget(Label(text=(player[0] + " - " + str(player[1]) + " punktów"), font_size="40dp"))

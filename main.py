from kivy import Config
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from menu import Menu
from options import Options
from game import PrepareGameNoOfPlayers, Game
from results import Results


class Intro(Screen):
    def __init__(self, **kwargs):
        super(Intro, self).__init__(**kwargs)

    def on_enter(self):
        Clock.schedule_once(self.listener, 0)

    # listener sprawdzający kiedy skończy się intro, który przechodzi potem do głównego menu
    def on_position_change(self, screen, value):
        if value > self.label.duration - 21:  # czas: 20s
            self.label.state = 'stop'
            self.manager.current = 'menu'

    def listener(self, *args):
        self.label.bind(position=self.on_position_change)


class Manager(ScreenManager):
    intro = ObjectProperty(None)
    menu = ObjectProperty(None)
    options = ObjectProperty(None)
    game = ObjectProperty(None)
    results = ObjectProperty(None)


class MainApp(App):
    def build(self):
        m = Manager(transition=NoTransition())
        return m


if __name__ == "__main__":
    #Window.fullscreen = 'auto'
    #Config.set('graphics', 'fullscreen', 'auto')  # pełny ekran
    MainApp().run()

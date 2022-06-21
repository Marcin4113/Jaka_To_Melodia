from kivy import Config
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

class Intro(Screen):
    def __init__(self, **kwargs):
        super(Intro, self).__init__(**kwargs)

    # listener sprawdzający kiedy skończy się intro, który przechodzi potem do głównego menu
    def on_position_change(self, screen, value):
        if value > 20:
            self.label.state = 'stop'
            self.manager.current = 'menu'

    def on_enter(self):
        Clock.schedule_once(self.btnpress, 1)

    def btnpress(self, *args):
        self.label.bind(position=self.on_position_change)


class ScreenTwo(Screen):

    def __init__(self, **kwargs):
        super(ScreenTwo, self).__init__(**kwargs)


class Manager(ScreenManager):
    intro = ObjectProperty(None)
    screen_two = ObjectProperty(None)


class ScreensApp(App):
    def build(self):
        m = Manager(transition=NoTransition())
        return m


if __name__ == "__main__":
    Config.set('graphics', 'fullscreen', 'auto')  # pełny ekran
    ScreensApp().run()

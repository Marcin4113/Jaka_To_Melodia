from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.uix.screenmanager import Screen


class Options(Screen):
    intro_state = BooleanProperty(True)
    volume_value = NumericProperty(75)

    def __init__(self, **kwargs):
        super(Options, self).__init__(**kwargs)

    def on_switch_active(self, widget):
        self.intro_state = widget.active

    def on_slider_value_change(self, widget):
        self.volume_value = int(widget.value)

    def download_database(self, widget):
        pass


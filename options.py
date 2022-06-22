import threading
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.uix.screenmanager import Screen
from databse import Database

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
        x = threading.Thread(target=self.connect_to_database)  # sprawdzić czy trzeba zapisywać wątek w klasie
        x.start()

    def connect_to_database(self):
        self.ids.import_database_button.text = "Pobieranie danych..."
        db = Database("database.db")
        db.setup_db()
        db.download_data()
        self.ids.import_database_button.text = "Importuj bazę danych piosenek"

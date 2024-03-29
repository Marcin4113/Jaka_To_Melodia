import threading
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.uix.screenmanager import Screen
from databse import Database
import settings

class Options(Screen):
    volume_value = NumericProperty(100)

    def __init__(self, **kwargs):
        super(Options, self).__init__(**kwargs)

    def on_slider_value_change(self, widget):
        settings.master_volume = int(widget.value)
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

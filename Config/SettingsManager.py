import json
#import spacy
from pathlib import Path

from Iris.utils.FileProcessing.FileManager import FileManager
from Iris.utils.Logging.ConsolePrinter import ConsolePrinter
#from Iris.utils.Sound.VoiceEngine import VoiceEngine

# settings location
settings_path = Path("Iris/settings.json")


class SettingsManager:
    """This class make json manipulation easier, store data and allow us to get specific data faster without reloading the file everytime"""
    def __init__(self, json_file=settings_path):
        """Just store the data and path"""
        self.path = json_file
        self.data = FileManager.load_json(self.path)

        # Load spacy models for language processing
        #spacy.prefer_gpu()
        #self.nlp = spacy.load('fr_core_news_md')

        self.update()
        ConsolePrinter.print_debug("Settings has been loaded")

    def _read_all(self):
        """This method is essentially for debugging and explore data"""
        return json.dumps(self.data, indent=2)

    def _get(self, name, default=None):
        """A getter to get the json encoded item with name: name"""

        return self.data.get(name, default)

    def __getitem__(self, item):
        return self._get(item)

    def _set(self, name, data):
        """A setter to set the json encoded item with name: name and update the file"""

        self.data[name] = data
        self.update()

    def update(self):
        """This method make the file matching with the object data"""

        try:
            # update the file
            FileManager.write_in(self.path,
                                 json.dumps(self.data, indent=2),
                                 mode='w')

            # update path
            self.paths = self._get('paths')

            self.comparator = self._get('comparator')
            self.placeholders = self._get('placeholders')

            self.max_stc_len = self._get("max_stc_len")

            # Vocal settings
            self.tts = self._get('tts')
            self.stt = self._get('stt')
            # Load voice engine
            #self.voice_engine = VoiceEngine(self)

            self.wakers = [
                waker.lower() for waker in self._get('wakers', "Iris")
            ]

            # name/class conversion table
            self.tasks = self._get('tasks')

        except IOError as e:
            ConsolePrinter.print_error("SettingsLoader: I/O error(%s): %s" +
                                       e.errno + e.strerror)

from pathlib import Path

from Iris.utils.FileProcessing.FileManager import FileManager
#from Iris.core.Models.Reflexs.Reflex import Reflex


class Reflexs:
    """This class allows to manage reflexs(dict) saved in a json file:
    <name>: {signals: [...],
             tasks: [...],
             enabled: bool}"""
    def __init__(self, settings=None):
        self.data = {}

        self.loaded = False
        self.settings = settings

    def find_reflex_by_name(self, name):
        return Reflex(name=name, **self.data[name], settings=self.settings)

    def find_reflex_by_signal(self, signal):
        for name, reflex in self.data.items():
            if signal in reflex['signals']:
                return Reflex(name=name, **reflex, settings=self.settings)

    def load(self):
        if not self.loaded:
            self.data = FileManager.load_json(
                Path(self.settings['paths']['reflexs_path']))

            self.loaded = True

    def unload(self):
        self.data = {}
        self.loaded = False

    def save(self):
        FileManager.save_json(Path(self.settings['paths']['reflexs_path']),
                              self.data)

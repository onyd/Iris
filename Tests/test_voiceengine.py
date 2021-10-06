from Iris.Config.SettingsManager import SettingsManager
from Iris.utils.Sound.VoiceEngine import VoiceEngine
import logging as lg
import time
logger = lg.getLogger()
logger.setLevel(level=lg.ERROR)

settings = SettingsManager()

engine = VoiceEngine(settings)

engine.speak("Bonjour je fait des testes")

text = engine.listen()
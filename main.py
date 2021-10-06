# -*- coding: utf-8 -*-
import sys
import logging as lg

from Iris.Config.SettingsManager import SettingsManager
from Iris.core.Listen.Listening.ListenerHandler import ListenerHandler
from Iris.core.Listen.Listening.Listeners import VoiceListener

logger = lg.getLogger()
logger.setLevel(level=lg.ERROR)


def setup():
    # First we load settingspip
    settings = SettingsManager()

    listener_handler = ListenerHandler(settings)
    voice_listener = VoiceListener(listener_handler, settings)

    # Start listeners
    voice_listener.start()

    # Wait for thread to finish
    voice_listener.join()

    sys.exit()


# Start vocal assistant
if __name__ == "__main__":
    setup()

import random
import time
from threading import Thread
from abc import ABC, abstractmethod


class Listener(ABC, Thread):
    def __init__(self, listener_handler, settings=None):
        Thread.__init__(self)

        self.listener_handler = listener_handler
        self.stopped = True
        self.settings = settings

    @abstractmethod
    def run(self):
        pass


class VoiceListener(Listener):
    def __init__(self, listener_handler, settings=None):
        super().__init__(listener_handler, settings)

    def run(self):
        self.stopped = False
        while not self.stopped:
            # Try listening waking word
            text = self.settings.voice_engine.listen()

            if text in self.settings.wakers:
                # A waking word has been registered, it's time to listen an order
                response = random.choice(self.settings._get("wake_response"))
                self.settings.voice_engine.speak(response)

                order = self.settings.voice_engine.listen()
                if order:
                    self.listener_handler.trigger({
                        'type': 'order',
                        'value': order.lower()
                    })
                else:
                    response = random.choice(
                        self.settings._get("miss_understand_response"))
                    self.settings.voice_engine.speak(response)

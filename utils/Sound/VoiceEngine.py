from vosk import Model, KaldiRecognizer
import pyttsx3 as tts
import pyaudio
import time as t
import json

from Iris.utils.Logging.ConsolePrinter import ConsolePrinter

fr = "fr-FR", r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_FR-FR_HORTENSE_11.0"


class VoiceEngine:
    def __init__(self, settings):
        self.settings = settings

        self.stt_model = Model(self.settings.paths['stt_model'])

        # Debug info
        #ConsolePrinter.print_debug("----------VoiceEngine set with :")
        # ConsolePrinter.print_colored("tts: " + tts.get('name'))
        # ConsolePrinter.print_colored("language: " + tts.get('language'))
        # ConsolePrinter.print_colored("speak rate: " + str(tts.get('rate')))
        # ConsolePrinter.print_colored("stt: " + stt.get('name'))
        # ConsolePrinter.print_colored("language: " + stt.get('language'))
        # ConsolePrinter.print_colored("time to speak: " + str(stt.get('time')))
        # ConsolePrinter.print_debug("---------------------------------------")

    def speak(self, text):
        ConsolePrinter.print_debug("-Iris: " + text)
        tts_model = tts.init()
        tts_model.setProperty("voice", fr[1])
        tts_model.setProperty("rate", self.settings.tts['rate'])
        tts_model.say(text)
        tts_model.runAndWait()
        ConsolePrinter.print_debug("Finished speaking")

    def listen(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        frames_per_buffer=8000)
        stream.start_stream()
        rec = KaldiRecognizer(self.stt_model, 16000)

        ConsolePrinter.print_debug("->Start listening")
        t0 = t.time()

        text = ""
        while (t.time() - t0) < self.settings.stt['time']:
            data = stream.read(16000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                text = json.loads(rec.Result())['text']

        ConsolePrinter.print_debug("->Stop listening")

        if text != "":
            ConsolePrinter.print_debug("-Vous: " + text)
            return text.lower()

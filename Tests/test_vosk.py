from vosk import Model, KaldiRecognizer
import os

import pyaudio

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8000)
stream.start_stream()

model = Model(
    r"C:\Users\Anthony Dard\OneDrive\VSC\Iris\DL\Saved\vosk_model_medium_fr_pguyot"
)
rec = KaldiRecognizer(model, 16000)

while True:
    data = stream.read(4 * 16000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        print(rec.Result())
    else:
        print(rec.PartialResult())

text = rec.FinalResult()
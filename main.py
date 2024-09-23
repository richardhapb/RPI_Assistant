import os
import sys
import json
import vosk
import pyaudio
import lamp

kwrds = ['lo logré']


if not os.path.exists("model"):
    print("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
    sys.exit(1)
    
model = vosk.Model("model")
recognizer = vosk.KaldiRecognizer(model, 16000)

def recognize(data):
    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        return result
    else:
        return None
    
def main():
    lamp.main_lamp()
    return

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()
    print("Listening...")
    while True:
        data = stream.read(4000)
        if not data:
            break
        try:
            if recognize(data)['text'] in kwrds:
                break
        except TypeError:
            pass
    print("Done.")
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":

    main()

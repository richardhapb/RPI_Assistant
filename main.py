import speech_recognition as sr

recognizer = sr.Recognizer()

# Ajustar el umbral de energía (se puede ajustar según el entorno)
recognizer.energy_threshold = 4000  # Este valor puede requerir ajustes

kwrds = ['lo logré']


def recognize(audio):
    try:
        text = recognizer.recognize_google(audio, language='es-ES')
        print(f"Detected phrase: {text}")
        return text.lower()
    except sr.UnknownValueError:
        print('Unknown words')
    except sr.RequestError as e:
        print(f'Error requesting to Google Speech Recognition: {e}')


while True:
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        if recognizer.energy_threshold < 4000:
            print('Listening...')
            audio = recognizer.listen(source)
            text_listened = recognize(audio)
            if text_listened and text_listened in kwrds:
                if text_listened == kwrds[0]:
                    print(f'Phrase detected')
        else:
            print('Waiting...')


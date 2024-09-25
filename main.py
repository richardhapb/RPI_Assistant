import os
import sys
import json
import vosk
import pyaudio
from openai import OpenAI
from gtts import gTTS
import time
import config
import icloud

client = OpenAI(api_key=config.OPENAI_APIKEY)

NAME_AI = "octavia"

# Keywords

kwrds_activation = [NAME_AI]
kwrds_greetings = ["buen día", "hola " + NAME_AI, "hola"]
kwrds_chatgpt_data = ['tengo una duda', 'ayúdame con algo', 'ayúdeme con algo', 'ayudarme con algo']
kwrds_chatgpt = ['inicia una conversación', 'hablémos por favor', 'inicia un chat', 'necesito respuestas', 'iniciar un chat']
kwrds_lamp_on = ['enciende la luz', 'prende la luz', 'luz por favor', 'enciende la luz por favor']
kwrds_lamp_off = ['apaga la luz', 'quita la luz', 'apaga la luz por favor']

MAX_TOKENS = 200
PLAYER = "cvlc --play-and-exit "

DEV = True
REQUEST = "hola"
RATE = 16000
CHUNK = 1024  # Tamaño del fragmento de audio (puede ser 1024, 2048, 4000, etc.)

# Inicialización de PyAudio y apertura del flujo de entrada
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
stream.start_stream()

if not os.path.exists("model"):
    print("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
    sys.exit(1)
    
model = vosk.Model("model")
recognizer = vosk.KaldiRecognizer(model, RATE)

def recognize(data):
    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        return result
    else:
        return {}

def listen(max_listening_time=5):
    data = b""
    start_time = time.time()

    while time.time() - start_time < max_listening_time:
        try:
            chunk = stream.read(CHUNK, exception_on_overflow=False)
            data += chunk
        except Exception as e:
            print(f"Error al leer el audio: {e}")
            break
    result = recognize(data)
    if result and 'text' in result:
        res = result['text']
    else:
        res = "error"

    return res

def speak(text):
    tts = gTTS(text, lang="es", tld="com.mx")
    tts.save("response.mp3")
    os.system(PLAYER + "response.mp3")

def manage_request(request):
    response = ""
    if request in kwrds_greetings:
        response = greetings()
    elif request in kwrds_chatgpt:
        prompt = ""
        speak("Si Richard, dime que necesitas")
        while True:
            prompt = listen(10)
            print(listen)
            exit = ["gracias", "nada más", "estamos ok", "estamos listos", "con eso estamos"]
            if prompt in exit:
                speak("De nada Richard, avísame si necesitas algo más")
                break
            gpt = chatgpt(prompt)
            print(gpt)
            speak(gpt)

    elif request in kwrds_chatgpt_data:
        response = chatgpt_data()
    elif request in kwrds_lamp_on:
        response = lamp(True)
    elif request in kwrds_lamp_off:
        response = lamp(False)
    elif request == "adiós " + NAME_AI:
        response = "exit"
    return response

# Funciones de acción

def greetings():
    speak("Hola Richard, te detallo los eventos que tienes para hoy")

    reminders = icloud.reminders_today()
    events = icloud.calendar_today()

    for e in events:
        speak(e)

    return "¡Que tengas un excelente día!"

def chatgpt(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres una asistente de mi centro de trabajo y hogar, me ayudas en mi planificación diaria y en llevar a cabo mis proyectos, tu nombre es Octavia, mi nombre es Richard. Responde en texto plano, sin usar Markdown"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=MAX_TOKENS,
        temperature=0.7
    )

    res = response.choices[0].message.content
    print(res)
    return res

def chatgpt_data():
    prompt = ""

    speak("¿En qué te puedo ayudar?")

    # Escuchar por 10 segundos
    prompt = listen(10)

    if DEV:
        prompt = "Dame una frase motivadora potente"

    print(f"prompt: {prompt}")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": prompt
        }],
        max_tokens=MAX_TOKENS,
        format="text"
    )
    res = response.choices[0].message.content
    return res

def lamp(on=True):
    res = ""
    if on:
        res = "Lámpara encendida"
    else:
        res = "Lámpara apagada"
    return res
        

def main():
    response = ""
    try:
        while True:
            print("Escuchando...")
            while True:
                if DEV:
                    response = manage_request(REQUEST)
                    break
                else:
                    request = listen(5)
                    print(request)
                    response = manage_request(request)
                    if response == "error":
                        continue
                    else:
                        break
            if response == "exit":
                break
            elif response == "":
                continue

            print(response)
            speak(response)
    except KeyboardInterrupt:
        pass
    finally:
        print("Done.")
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()

from bs4 import BeautifulSoup
import requests
import urllib3
import config
import numpy as np
import json
import vosk
from gtts import gTTS
import requests
import time
import icloud
import sys
import pyaudio
import os
import spotify
from spotipy import SpotifyException
from openai import OpenAI
import lamp

client = OpenAI(api_key=config.OPENAI_APIKEY)

MAX_TOKENS = 200

urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

PHRASE_API = "http://proverbia.net"  # Frase motivadora (API))

kwrds_greetings = ["buen día", "buen día " + config.NAME_AI, "muy buenos días", "buenos días"]
kwrds_chatgpt_data = ['tengo una duda', 'ayúdame con algo', 'ayúdeme con algo', 'ayudarme con algo']
kwrds_chatgpt = ['inicia una conversación', 'hablémos por favor', 'inicia un chat', 'necesito respuestas', 'iniciar un chat', 'pon un chat']
kwrds_lamp_on = ['enciende la luz', 'prende la luz', 'luz por favor', 'enciende la luz por favor']
kwrds_lamp_off = ['apaga la luz', 'quita la luz', 'apaga la luz por favor']
kwrds_daily_phrase = ['frase del día', 'frase motivadora', 'frase para hoy', "frase de hoy"]


RATE = 16000 # Ratio de captación pyaudio
CHUNK = 1024  # Tamaño del fragmento de audio (puede ser 1024, 2048, 4000, etc.)
PLAYER = "cvlc --play-and-exit "
MAX_AI_TIME = 10 # Tiempo que asistente está activa

# Inicialización de PyAudio y apertura del flujo de entrada/salida
p = pyaudio.PyAudio()

# Micrófono
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
stream.start_stream()

# Música
music = p.open(format=pyaudio.paInt16, channels=2, rate=RATE, output=True)
music.start_stream()

# Módelo para reconocmiento de voz
if not os.path.exists("model"):
    print("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
    sys.exit(1)

KWRDS = {
    "greetings": kwrds_greetings,
    "chatgpt_data": kwrds_chatgpt_data,
    "chatgpt": kwrds_chatgpt,
    "lamp_on": kwrds_lamp_on,
    "lamp_off": kwrds_lamp_off,
    "daily_phrase": kwrds_daily_phrase
}


# Funciones de acción

def greetings():
    '''Da los buenos días e información relevante'''
    speak(f"Hola {config.NAME_USER}, muy buenos días, ¡espero estés excelente!")

    #### WEATHER
    try:
        w, fd, fh = weather()

        wl = weather_limits(fh)

        if w['temp_c'] < 16:
            speak("Hoy hace frío")
        elif w['temp_c'] < 20:
            speak("Está un poco frío, pero no mucho para ti")
        else:
            speak("Hoy hace calor")

        speak(f"El cielo está {w['condition']['text']}")    

        def is_past(hour):
            return "fue" if int(time.strftime("%H", time.localtime(time.time()))) > int(hour[:2]) else "será"
        
        speak(f"La temperatura actual es {w['temp_c']} grados celcius")
        speak(f"La mínima {is_past(wl[0][1])} de {wl[0][0]} grados celcius a las {wl[0][1]} y la máxima {is_past(wl[1][1])} de {wl[1][0]} grados celcius a las {wl[1][1]}.")
        speak(f"La probabilidad de lluvia es {fd['daily_chance_of_rain']}%")
    except KeyError:
        print("Error al obtener el clima")
    except Exception as e:
        print("Hubo en error")
        print("Error: " + e.args[0])

    try:
        # reminders = icloud.reminders_today()
        events = icloud.calendar_today()

        if events:
            speak("Estos son tus eventos para hoy: ")
            for e in events:
                speak(e)
        else:
            speak("No tienes eventos agendados para hoy")
    except ConnectionError:
        print("Hubo un error al obtener los datos de iCloud")

    ### Frase motivadora
    try:
        phrase = daily_phrase()

        speak("Tengo una frase motivadora para tí")
        speak(f"{phrase['phrase']} {phrase['author']}")
    except Exception as e:
        print("Hubo un error al obtener la frase motivadora")

    return "¡Que tengas un excelente día!"

def chatgpt(prompt):
    '''Inicia un chat con API de OpenAI'''
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Eres una asistente de mi centro de trabajo y hogar, me ayudas en mi planificación diaria y en llevar a cabo mis proyectos, tu nombre es {config.NAME_AI}, mi nombre es {config.NAME_USER}."},
            {"role": "user", "content": prompt + ". Responde en texto plano, sin usar Markdown."}
        ],
        max_tokens=MAX_TOKENS,
        temperature=0.7
    )

    res = response.choices[0].message.content
    print(res)
    return res

def chatgpt_data():
    '''Obtiene un dato puntual de Chat GPT a través de la api'''
    prompt = ""

    speak("¿En qué te puedo ayudar?")

    # Escuchar por 10 segundos
    prompt = listen(10)

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
    print(res)
    return res

def light(on=True):
    '''Enciende/apaga la luz (conectada a RPI)'''
    res = ""
    if on:
        lamp.light(on)
        res = "Listo"
    else:
        lamp.light(on)
        res = "Listo"
    return res

            
def daily_phrase():
    try:
        url = PHRASE_API
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.text, "lxml")
        phrase = soup.blockquote.text
        phrase = phrase[0 : phrase.find("(")]
    except Exception as e:
        print("Hubo un error", e)
        phrase = "Hubo un error al obtener la frase"


    return phrase

FUNCTIONS = {
    "greetings": greetings,
    "chatgpt_data": chatgpt_data,
    "chatgpt": chatgpt,
    "lamp_on": lamp.light,
    "lamp_off": lamp.light,
    "daily_phrase": daily_phrase
}



##################### UTILS

def text_to_number(text:str):
    numbers = {
        "cero": "0",
        "uno": "1",
        "dos": "2",
        "tres": "3",
        "cuatro": "4",
        "cinco": "5",
        "seis": "6",
        "siete": "7",
        "ocho": "8",
        "nueve": "9"
    }
    
    words = text.split(" ")

    numbers_str = ""

    for w in words:
        if w in numbers.keys():
            numbers_str += numbers[w]
    

    return numbers_str

def in_request(request:str):
    if config.NAME_AI in request:
        rq1, rq2 = request.split(config.NAME_AI)

## GLOBALS

want_validate_icloud = False # ¿Usuario quiere validar icloud en caso de no estarlo?
ai = False # ¿Asistente activa?
ai_since = 0 # ¿Desde cuándo está activa?
paused = False # ¿Música pausada para hablar?
stopped = True # ¿Música totalmente detenida?

### ICLOUD
def initicloud():
    '''Inicia sesión en iCloud'''
    global want_validate_icloud
    result = icloud.init_icloud()

    if result: 
        want_validate_icloud = True
        return

    ### Se requiere autenticación 2fa
    print("Se requiere autenticación de dos factores.")
    speak("Dame el código de icloud para la verifícación de segundo paso")

    while True:
        res = listen(max_listening_time = 10)
        count = 0
        while res == "error":
            speak("Me puedes repetir por favor")
            res = listen(max_listening_time = 10)
            count += 1
            if count >= 5:
                want_validate_icloud = True
                return
        
        code = text_to_number(res)
        print(code)

        if icloud.pass_2fa(code):
            try:
                result = icloud.init_icloud(code)
                if result:
                    speak("Ingreso correcto")
                    break
            except PermissionError:
                speak("Hubo un error en el ingreso a iCloud")
                continue
        else:
            speak("Lo siento, escuché mal el código")
        
        want_validate_icloud = True

model = vosk.Model("model")
recognizer = vosk.KaldiRecognizer(model, RATE)

def validate_icloud():
    '''Veriica si iCloud está iniciado'''
    global want_validate_icloud

    if not icloud.validated and want_validate_icloud:
        speak(f"{config.NAME_USER}, icloud no está validado, ¿quieres proporcionar el acceso?")
        response = listen()
        time.sleep(5)

        if response == "si":
            initicloud()
        else:
            speak("Ok, avísame si quieres validar iCloud")
            want_validate_icloud = False

def recognize(data):
    '''Reconoce el audio del usuario'''
    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        return result
    else:
        return {}

def listen(max_listening_time=5):
    '''Capta la voz del usuario'''
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
    '''Habla el texto ingresado'''
    global ai_since, paused
    global ai_since, paused
    stream.stop_stream()
    playing_music = spotify.is_playing()
    if playing_music and not paused:
        try:
            spotify.pause()
            paused = True
            time.sleep(2)
        except SpotifyException:
            pass
            
    tts = gTTS(text, lang="es", tld="com.mx")
    tts.save("response.mp3")
    os.system(PLAYER + "response.mp3")

    validate_icloud()
    
    stream.start_stream()
    ai_since = int(time.time())

def weather():

    '''
    Obtiene el clima de hoy y proyectado
    '''

    ## lat y lon locales
    lat = config.LAT
    lon = config.LON

    BASE_URL = "http://api.weatherapi.com/v1"
    PARAMS_WEATHER = f"?lang=es&key={config.WEATHER_API_KEY}&q={lat},{lon}"
    PARAMS_FORECAST = PARAMS_WEATHER + "&days=1"
    
    req = {
        "weather": "/current.json",
        "forecast": "/forecast.json"
    }

    try:
        weather = requests.get(BASE_URL + req["weather"] + PARAMS_FORECAST).json()["current"]

        forecast = requests.get(BASE_URL + req["forecast"] + PARAMS_FORECAST).json()["forecast"]
        forecast_day = forecast['forecastday'][0]['day']
        forecast_hour = forecast['forecastday'][0]['hour']
    except KeyError as e:
        print("La solicitud no fue exitosa")
        raise KeyError(e)
    except Exception as e:
        print("Error al obtener la información")
        print(e)
        raise Exception(e)
    
    return weather, forecast_day, forecast_hour

def weather_limits(hour_forecast):
    temp = np.empty(shape=(len(hour_forecast), 2))

    for f in range(0, len(hour_forecast)):
        temp[f] = [hour_forecast[f]['temp_c'], hour_forecast[f]['time_epoch']]
            # Temperatura y horario temperatura mínima y máxima
    return [[temp[np.argmin(temp, 0)[0]][0], time.strftime("%H:%M", time.localtime(temp[np.argmin(temp, 0)[0]][1]))], 
            [temp[np.argmax(temp, 0)[0]][0], time.strftime("%H:%M", time.localtime(temp[np.argmax(temp, 0)[0]][1]))]]


def manage_request(request):
    '''Ciclo principal donde se controla el flujo según orden de usuario'''
    global want_validate_icloud, ai, ai_since, paused, stopped

    response = ""

    name_ai = False

    for n in config.KWDS_AI:
        if n in request:
            name_ai = True

    if ai_since == 0 and not name_ai:
        return response
    elif name_ai:
        if int(time.time()) - ai_since > MAX_AI_TIME:
            ai = True
    elif int(time.time()) - ai_since <= MAX_AI_TIME:
        ai = True

    
    if spotify.is_playing() and int(time.time()) - ai_since > MAX_AI_TIME and paused and not stopped:
        try:
            spotify.resume()
        except SpotifyException:
            pass

    if ai:
        if request in KWRDS["greetings"]:
            response = FUNCTIONS["greetings"]()
        elif request in kwrds_chatgpt:
            prompt = ""
            speak(f"Si {config.NAME_USER}, dime que necesitas")
            while True:
                prompt = listen(10)
                print(listen)
                exit = ["gracias", "nada más", "estamos ok", "estamos listos", "con eso estamos"]
                if prompt in exit:
                    speak(f"De nada {config.NAME_USER}, avísame si necesitas algo más")
                    break
                gpt = FUNCTIONS["chatgpt"](prompt)
                print(gpt)
                speak(gpt)

        elif request in kwrds_chatgpt_data:
            response = FUNCTIONS["chatgpt_data"]()
        elif request in kwrds_lamp_on:
            FUNCTIONS["lamp_on"](True)
            response = "Lámpara encendida"
        elif request in kwrds_lamp_off:
            FUNCTIONS["lamp_on"](False)
            response = "Lámpara apagada"
        elif request in kwrds_daily_phrase:
            response = daily_phrase()
        elif "icloud" in request or "cloud" in request or "club" in request or "clavo" in request:
            if icloud.validated:
                speak(f"Si {config.NAME_USER}, se encuentra validado el acceso a iCloud")
            else:
                speak(f"No {config.NAME_USER}, no se encuentra validado el acceso a iCloud")
                want_validate_icloud = True
            validate_icloud()
        elif "música" in  request:
            try:
                if "detén" in request or "pausa" in request:
                    try:
                        spotify.pause()
                        speak("listo")
                        stopped = True
                        paused = False
                    except SpotifyException:
                        response = "Hubo un problema con Spotify"
                elif "reanuda" in request or "continúa" in request or "play" in request:
                    try:
                        spotify.resume()
                        speak("listo")
                        stopped = False
                        paused = False
                    except SpotifyException:
                        response = "Hubo un problema con Spotify"
                else:
                    last_word = request.split(" ")[-1]
                    if last_word == "música":
                        spotify.playlist()
                    elif last_word == "viajar":
                        spotify.playlist("spotify:playlist:47RDqYFo357tW5sIk5cN8p")
                    elif last_word == "estudiar":
                        spotify.playlist("spotify:playlist:1YIe34rcmLjCYpY9wJoM2p")
                    elif last_word == "relajarme":
                        spotify.playlist("spotify:playlist:0qPA1tBtiCLVHCUfREECnO")
                    stopped = False
            except SpotifyException:
                speak("Hay un problema con Spotify")
            except ValueError as e:
                print(e)
                speak(str(e))
        elif name_ai:
            response = f"¿Si {config.NAME_USER}?"
        elif request == "adiós " and name_ai:
            response = "exit"
    return response

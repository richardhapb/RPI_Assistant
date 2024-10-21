from bs4 import BeautifulSoup
import requests
import urllib3
import config
import numpy as np
import json
import vosk
from gtts import gTTS
import time
import icloud
import sys
import pyaudio
import os
import spotify
from spotipy import SpotifyException
from openai import OpenAI
from datetime import datetime, timedelta

RPI = True

try:
    import lamp
except ImportError:
    RPI = False
    print("No se importó lampara, porque el entorno no es Raspberry PI")

client = OpenAI(api_key=config.OPENAI_APIKEY)

MAX_TOKENS = 200

urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

PHRASE_API = "http://proverbia.net"  # Frase del día (link para extracción)

KWRDS = {
    "greetings": ["buen día", "buen día " + config.NAME_AI, "muy buenos días", "buenos días"],
    "chatgpt_data": ['tengo una duda', 'ayúdame con algo', 'ayúdeme con algo', 'ayudarme con algo'],
    "chatgpt": ['inicia una conversación', 'hablémos por favor', 'inicia un chat', 'necesito respuestas', 'iniciar un chat', 'pon un chat'],
    "lamp_on": ['enciende la luz', 'prende la luz', 'luz por favor', 'enciende la luz por favor'] if RPI else [],
    "lamp_off": ['apaga la luz', 'quita la luz', 'apaga la luz por favor'] if RPI else [],
    "daily_phrase": ['frase del día', 'frase motivadora', 'frase para hoy', "frase de hoy"],
    "weather_info": ['clima', 'temperatura'],
    "calendar_info": ['calendario', 'agenda', "organizado", "eventos"],
    "icloud_is_validated": ["icloud", "cloud", "club", "clavo"],
    "music": ["música"],
    "ai": config.KWDS_AI,
    "alarm": ["alarma", "despertar", "despertarme", "alarmas", "despertar alarma", "despertar alarmas", "despiertame"],
    "date_now": ["fecha actual", "fecha de hoy", "fecha es hoy", "fecha estamos", "qué día es hoy"],
    "time_now": ["dime la hora", "qué hora es"]
}

## GLOBALS

want_validate_icloud = False # ¿Usuario quiere validar icloud en caso de no estarlo?
ai_active = False # ¿Asistente activa?
ai_since = 0 # ¿Desde cuándo está activa?
paused = False # ¿Música pausada para hablar?
stopped = True # ¿Música totalmente detenida?
alarm_active = False # ¿Alarma activa?
alarm_time = int(datetime.now().timestamp()) # Hora de la alarma

RATE = 16000 # Ratio de captación pyaudio
CHUNK = 1024  # Tamaño del fragmento de audio (puede ser 1024, 2048, 4000, etc.)
PLAYER = "cvlc --play-and-exit "
MAX_AI_TIME = 10 # Tiempo que asistente está activa en segundos

# Inicialización de PyAudio y apertura del flujo de entrada/salida
p = pyaudio.PyAudio()

# Micrófono
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
stream.start_stream()

# Música
music_stream = p.open(format=pyaudio.paInt16, channels=2, rate=RATE, output=True)
music_stream.start_stream()

# Módelo para reconocmiento de voz
if not os.path.exists("model"):
    print("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
    sys.exit(1)

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
        "nueve": "9",
        "diez": "10",
        "once": "11",
        "doce": "12",
        "trece": "13",
        "catorce": "14",
        "quince": "15",
        "dieciséis": "16",
        "diecisiete": "17",
        "dieciocho": "18",
        "diecinueve": "19",
        "veinte": "20",
        "veintiuno": "21",
        "veintidós": "22",
        "veintitrés": "23",
        "veinticuatro": "24",
        "veinticinco": "25",
        "veintiséis": "26",
        "veintisiete": "27",
        "veintiocho": "28",
        "veintinueve": "29",
        "treinta": "30",
        "cuarenta": "40",
        "cincuenta": "50",
        "sesenta": "60",
        "setenta": "70",
        "ochenta": "80",
        "noventa": "90"
    }
    
    try:
        words = text.split(" ")

        numbers_str = ""

        cont = False
        for w in words:
            if w in numbers.keys():
                numbers_str += numbers[w]
                cont = True
            else:
                if cont and w == "y":
                    numbers_str = numbers_str[:-1]
                cont = False
    except Exception as e:
        print(e)
        raise ValueError("Error al procesar el texto, al parecer no son números")
    

    return numbers_str

def day_to_es(day:str):
    days = [("sunday", "domingo"),
            ("monday", "lunes"),
            ("tuesday", "martes"),
            ("wednesday", "miércoles"),
            ("thursday", "jueves"),
            ("friday", "viernes"),
            ("saturday", "sábado")]
    
    response = day
    
    for d in days:
        response = response.lower().replace(*d)
    
    return response

def month_to_es(date: str):
    months = [("january", "enero"),
            ("february", "febrero"),
            ("march", "marzo"),
            ("april", "abril"),
            ("may", "mayo"),
            ("june", "junio"),
            ("july", "julio"),
            ("august", "agosto"),
            ("september", "septiembre"),
            ("october", "octubre"),
            ("november", "noviembre"),
            ("december", "diciembre")]

    response = date

    for m in months:
        response = response.lower().replace(*m)

    return response

### ICLOUD
def initicloud():
    '''Inicia sesión en iCloud'''
    global want_validate_icloud
    try:
        result = icloud.init_icloud()
    except ConnectionError:
        print("Hubo un problema con la conexión a iCloud")
        want_validate_icloud = False
        return

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
    try:
        if not icloud.validated and want_validate_icloud:
            speak(f"{config.NAME_USER}, icloud no está validado, ¿quieres proporcionar el acceso?")
            response = listen()
            time.sleep(5)

            if response == "si":
                initicloud()
            else:
                speak("Ok, avísame si quieres validar iCloud")
                want_validate_icloud = False
    except AttributeError:
        print("Hubo un problema con la conexión a iCloud")
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
    global ai_since, paused, stopped
    stream.stop_stream()
    
    if not stopped: # No verifica siempre, porque verificar tarda
        try:
            playing_music = spotify.is_playing()
            if playing_music and not paused and not stopped:
                    spotify.pause()
                    paused = True
                    time.sleep(2)
        except ConnectionError:
            print("No fue posible conectarse a Spotify")
        except SpotifyException:
            print("Spotify no disponible")

            
    tts = gTTS(text, lang="es", tld="com.mx")
    tts.save("response.mp3")
    os.system(PLAYER + "response.mp3")

    if want_validate_icloud:
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

def chatgpt_chat(prompt):
    '''Inicia un chat con API de OpenAI'''
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Eres una asistente de mi centro de trabajo y hogar, me ayudas en mi planificación diaria y en llevar a cabo mis proyectos, tu nombre es {config.NAME_AI}, mi nombre es {config.NAME_USER}."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    res = response.choices[0].message.content
    ## Remover caracteres de markdown
    res = res.replace("*", "").replace("#", "").replace("`", "").replace("_", "")
    print(res)
    return res


def isin(request:str, keywords:list):
    '''Verifica si el request contiene las keywords'''
    theris = False
    for k in keywords:
        theris = k in request
        if theris:
            break
    
    return theris

# Funciones de acción

def weather_info():
    response = ""
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
        response = "Hubo un problema al obtener la frase del día"
    except Exception as e:
        print("Hubo en error")
        print("Error: " + e.args[0])
        response = "Hubo un problema al obtener la frase del día"
    return response

def calendar_info():
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
        return "Hubo un error al obtener los datos de iCloud"
    
    return "Éxito en tu día"

def greetings():
    '''Da los buenos días e información relevante'''
    speak(f"Hola {config.NAME_USER}, muy buenos días, ¡espero estés excelente!")

    weather_info()

    calendar_info()

    ### Frase motivadora
    try:
        phrase = daily_phrase()

        speak("Tengo una frase motivadora para tí")
        speak(phrase)
    except Exception:
        print("Hubo un error al obtener la frase motivadora")

    return "¡Que tengas un excelente día!"

def chatgpt():
    prompt = ""
    speak(f"Si {config.NAME_USER}, dime que necesitas")

    res = ""

    try:
        while True:
            prompt = listen(10)
            print(listen)
            exit = ["gracias", "nada más", "estamos ok", "estamos listos", "con eso estamos"]
            if prompt in exit:
                speak(f"De nada {config.NAME_USER}, avísame si necesitas algo más")
                break
            gpt = chatgpt_chat(prompt)
            print(gpt)
            speak(gpt)
    except Exception as e:
        print(e)
        res = "Hubo un error en el chat"

    return res

def chatgpt_data():
    '''Obtiene un dato puntual de Chat GPT a través de la api'''
    prompt = ""

    speak("¿En qué te puedo ayudar?")

    # Escuchar por 10 segundos
    prompt = listen(10)

    print(f"prompt: {prompt}")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        res = response.choices[0].message.content
        # Remover caracteres de markdown
        res = res.replace("*", "").replace("#", "").replace("`", "").replace("_", "")
    except Exception:
        res = "Hubo un error con la consulta"
    print(res)
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

def lamp_on():
    lamp.light(True)
    return "Lámpara encendida"

def lamp_off():
    lamp.light(False)
    return "Lámpara apagada"

def icloud_is_validated():
    global want_validate_icloud
    if icloud.validated:
        speak(f"Si {config.NAME_USER}, se encuentra validado el acceso a iCloud")
    else:
        speak(f"No {config.NAME_USER}, no se encuentra validado el acceso a iCloud")
        want_validate_icloud = True
    validate_icloud()
    return ""

def music(request):
    global paused, stopped
    response = ""
    try:
        if isin(request, ["pausa", "detén"]):
            spotify.pause()
            stopped = True
            paused = False
            response = "Música pausada"
        elif isin(request, ["reanuda", "continúa", "play"]):
            spotify.resume()
            stopped = False
            paused = False
            response = "listo"
        else:
            if isin(request, ["viajar"]):
                spotify.playlist("spotify:playlist:47RDqYFo357tW5sIk5cN8p")
            elif isin(request, ["estudiar", "leer"]):
                spotify.playlist("spotify:playlist:1YIe34rcmLjCYpY9wJoM2p", volume=70)
            elif isin(request, ["relajarme", "tranquila"]):
                spotify.playlist("spotify:playlist:0qPA1tBtiCLVHCUfREECnO")
            else:
                spotify.playlist()
            stopped = False
            paused = False
    except SpotifyException:
        response = "Hay un problema con Spotify"
    except ValueError as e:
        print(e)
        response = "Hay un problema con Spotify"
    
    return response

def ai():
    return f"¿Si {config.NAME_USER}?"

def alarm(request):
    global alarm_active, alarm_time

    text = request

    response = ""
    if alarm_active and "desactiva" in request:
        response = "Alarma desactivada"
        alarm_active = False
    else: # Si no está activa, capturar la hora, y si es AM o PM
        words_am = ["am", "a.m.", "de la mañana"]
        words_pm = ["pm", "p.m.", "de la tarde"]

        is_am = isin(request, words_am)
        is_pm = isin(request, words_pm)

        if not is_am and not is_pm:
            is_am = True # Por defecto, si no es AM o PM, es AM
            word = words_am[0]
            text = text.replace(config.NAME_AI, "")
            text = text.strip()
            text = text + " " + word
        elif is_am:
            word = [w for w in words_am if w in request][0]
        elif is_pm:
            word = [w for w in words_pm if w in request][0]
        
        text = text.replace("y media", "treinta")
        text = text.replace("un cuarto", "quince")
        text = text.replace("y cuarto", "quince")
        try:
            minutes = text.split(word)[0].strip().split(" ")
            minutes = int(text_to_number(minutes[-1]))
        except ValueError:
            response = "No se pudo procesar el texto"
            return response
        try:
            hour = text.split(word)[0].strip().split(" ")
            hour = int(text_to_number(hour[-2]))
        except ValueError:
            hour = minutes # El usuario no dio minutos, asumimos que es la hora
            minutes = 0

            if hour > 24:
                response = "La hora " + str(hour) + " no es válida"
                return response
            
        al_time = datetime.now().replace(hour=hour, minute=minutes)
        if al_time < datetime.now():
            al_time = al_time + timedelta(days=1)
        alarm_time = int(al_time.timestamp())
    
        response = "Alarma activada para las " + str(hour) + ":" + str(minutes)
        alarm_active = True
    return response

def date_now():
    now = datetime.now()
    return "Hoy es " + month_to_es(day_to_es(now.strftime("%A, %d de %B de %Y")))

def time_now():
    now = datetime.now()
    return "Son las " + now.strftime("%H y %M")

##########

FUNCTIONS = dict(zip(KWRDS.keys(), [globals()[k] for k in KWRDS.keys()]))

def manage_request(request):
    '''Ciclo principal donde se controla el flujo según orden de usuario'''
    global ai_active, ai_since, paused, stopped, alarm_active, alarm_time

    response = ""

    if alarm_active:
        if alarm_time < int(datetime.now().timestamp()) and alarm_time > int(datetime.now().timestamp()) - 8:
            print("Alarma activa, música para relajarme")
            speak("Hola " + config.NAME_USER + ", despierta, " + time_now())
            try:
                music("música para relajarme", volume=50)
            except ConnectionError as e:
                print(e)
                response = "No se pudo cambiar el volumen"
            alarm_active = False
        
    try:
        if int(time.time()) - ai_since > MAX_AI_TIME and paused and not stopped: 
            # No verifica siempre si está reproduciendo, porque verificar tarda
            if spotify.is_playing():
                spotify.resume()
                paused = False
                stopped = False
    except ConnectionError:
        print("No fue posible conectarse a Spotify")
    except SpotifyException:
        print("Spotify no disponible")

    ai_active = isin(request, KWRDS["ai"])

    if not ai_active and int(time.time()) - ai_since > MAX_AI_TIME:
        return response

    if ai:
        if request == "adiós " + config.NAME_AI[0]:
            response = "exit"
        else:
            for k in KWRDS.keys():
                if isin(request, KWRDS[k]):
                    if len(request) > len(config.NAME_AI) and k == "ai":
                        continue
                    elif k == "music" or k == "alarm":
                        response = FUNCTIONS[k](request)
                    else:
                        response = FUNCTIONS[k]()
                    break
    return response

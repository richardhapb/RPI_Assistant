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
import requests
import spotify
from spotipy import SpotifyException
import lamp
import utils

client = OpenAI(api_key=config.OPENAI_APIKEY)

# Keywords


kwrds_greetings = ["buen día", "buen día " + config.NAME_AI, "muy buenos días", "buenos días"]
kwrds_chatgpt_data = ['tengo una duda', 'ayúdame con algo', 'ayúdeme con algo', 'ayudarme con algo']
kwrds_chatgpt = ['inicia una conversación', 'hablémos por favor', 'inicia un chat', 'necesito respuestas', 'iniciar un chat', 'pon un chat']
kwrds_lamp_on = ['enciende la luz', 'prende la luz', 'luz por favor', 'enciende la luz por favor']
kwrds_lamp_off = ['apaga la luz', 'quita la luz', 'apaga la luz por favor']

# Constantes

MAX_TOKENS = 200
PLAYER = "cvlc --play-and-exit "

DEV = False # ¿Modo desarrollo?
REQUEST = "buen día" # Request predeterminado para desarrollo
RATE = 16000 # Ratio de captación pyaudio
CHUNK = 1024  # Tamaño del fragmento de audio (puede ser 1024, 2048, 4000, etc.)
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
        
        code = utils.text_to_number(res)
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
    if playing_music:
        try:
            spotify.pause()
            paused = True
            time.sleep(2)
        except SpotifyException:
            pass
            
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

def weather(kind='weather', fc_days=1):

    '''
    Obtiene el clima de hoy o proyectado
    kind = weather, forecast
    '''

    ## lat y lon locales
    lat = config.LAT
    lon = config.LON

    BASE_URL = "http://api.weatherapi.com/v1"
    PARAMS = f"?lang=es&key={config.WEATHER_API_KEY}&q={lat},{lon}"
    PARAMS += f"&days={fc_days}" if kind == 'forecast' else ""
    
    req = {
        "weather": "/current.json",
        "forecast": f"/forecast.json"
    }

    responses = {
        "weather": "current",
        "forecast": "forecast"
    }

    try:
        response = requests.get(BASE_URL + req[kind] + PARAMS).json()[responses[kind]]
        if kind == 'forecast':
            response = response['forecastday'][0]['day']
    except KeyError as e:
        print("La solicitud no fue exitosa")
        raise KeyError(e)
    except Exception as e:
        print("Error al obtener la información")
        print(e)
        response = "error"
        raise Exception(e)
    
    return response


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
        if request in kwrds_greetings:
            response = greetings()
        elif name_ai:
            response = f"¿Si {config.NAME_USER}?"
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
                gpt = chatgpt(prompt)
                print(gpt)
                speak(gpt)

        elif request in kwrds_chatgpt_data:
            response = chatgpt_data()
        elif request in kwrds_lamp_on:
            lamp.light(True)
            response = "Lámpara encendida"
        elif request in kwrds_lamp_off:
            lamp.light(False)
            response = "Lámpara apagada"
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
        elif request == "adiós " and name_ai:
            response = "exit"
    return response


# Funciones de acción

def greetings():
    '''Da los buenos días e información relevante'''
    speak(f"Hola {config.NAME_USER}, muy buenos días, ¡espero estés excelente!")

    #### WEATHER
    try:
        w = weather()
        f = weather('forecast')

        if w['temp_c'] < 16:
            speak("Hoy hace frío")
        elif w['temp_c'] < 20:
            speak("Está un poco frío, pero no mucho para ti")
        else:
            speak("Hoy hace calor")

        speak(f"El cielo está {w['condition']['text']}")    
        
        speak(f"La temperatura actual es {w['temp_c']} grados celcius")
        speak(f"Se espera una mínima de {f['mintemp_c']} y una máxima de {f['maxtemp_c']} grados celcius")
        speak(f"La probabilidad de lluvia es {f['daily_chance_of_rain'] * 100}%")
    except KeyError:
        print("Error al obtener el clima")
    except Exception as e:
        print("Hubo en error")
        print(e)

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
        prompt = "Dame una frase motivadora potente, que haya dicho una persona exitósa, filósofo o científico. Que sea inspiradora. Damelo en texto plano, no uses markdown."

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=MAX_TOKENS
        )
        res = response.choices[0].message.content
        speak("Tengo una frase motivadora para ti")
        print(res)
        speak(res)
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
        

def main():
    '''Función principal de captación de voz'''
    global ai_since, ai
    initicloud()
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
                    if response == "error" or request == "error":
                        continue
                    else:
                        break
            if response == "exit":
                speak(f"adiós {config.NAME_USER}")
                break
            elif response == "":
                ai = False
                continue

            print(response)
            speak(response)
            ai = False
    except KeyboardInterrupt:
        pass
    finally:
        print("Done.")
        stream.stop_stream()
        stream.close()
        music.stop_stream()
        music.close()
        lamp.close()
        p.terminate()

if __name__ == "__main__":
    main()

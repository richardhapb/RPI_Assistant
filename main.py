import os
import sys
import json
import vosk
import pexpect
import pyaudio
import time
import config


#########################

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Configura la autenticación con Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config.CLIENT_ID,
                                               client_secret=config.CLIENT_SECRET,
                                               redirect_uri="http://localhost:8080",
                                               scope="user-read-playback-state,user-modify-playback-state"))

# Lista los dispositivos conectados
devices = sp.devices()
print("Dispositivos:", devices)

def playlist():
    # Reproduce una playlist específica
    print("Reproduciendo playlist...")
    sp.start_playback(device_id=config.ID_IPHONE, context_uri='spotify:playlist:4xZOpXJZVeKyE8Cm2PJb9m')

def pause():
    #
    # Pausa la reproducción
    print("Pausando...")
    sp.pause_playback()

def resume():
    # Reanuda la reproducción
    print("Reanudando...")
    sp.start_playback()

#########################


def conectar_dispositivo(direccion_mac):
    # Ejecuta bluetoothctl
    child = pexpect.spawn('bluetoothctl', encoding='utf-8')

    # Aumentar el tiempo de espera si es necesario
    child.timeout = 10

    # Activa Bluetooth
    child.expect('#')
    child.sendline('power on')
    child.expect('#')
    
    # Ejecuta el escaneo
    child.sendline('scan on')
    child.expect('Discovery started')  # Espera la confirmación de que el escaneo ha comenzado
    
    # Dale tiempo al escaneo para encontrar dispositivos
    time.sleep(5)  # Espera unos segundos para que el dispositivo sea detectado
    
    try: 
        # Si es que no hay una conexión
        child.sendline(f'info {direccion_mac}')
        child.expect('Connected: no', timeout=3)
        # Intenta conectarse
        child.sendline(f'connect {direccion_mac}')
        
        # Espera una confirmación de conexión
        try:
            child.expect('Connected: yes', timeout=10)
            print("Conexión realizada exitosamente.")
        except pexpect.TIMEOUT:
            print("La conexión no se realizó a tiempo. Verifica si el dispositivo está en modo de emparejamiento o si es accesible.")
    except pexpect.TIMEOUT:
        print('Conexión ya se encontraba establecida.')
    
    # Apaga el escaneo para ahorrar energía
    child.sendline('scan off')
    child.expect('#')
    
    # Salir de bluetoothctl
    child.sendline('exit')
    time.sleep(1)  # Espera un segundo para asegurarse de que los comandos se ejecuten completamente


if __name__ == "__main__":
    conectar_dispositivo(config.SONY_WH1000XM4)

kwrds = ['reproduce música', 'pausa', 'reanuda']

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
    p = pyaudio.PyAudio()
    # Configurar el stream de audio para capturar desde el dispositivo 'pulse'
    try:
        stream = p.open(format=pyaudio.paInt16, 
                        channels=1, 
                        rate=16000, 
                        input=True, 
                        input_device_index=0, 
                        frames_per_buffer=8192)
        print("Listening...")
        
        while True:
            try:
                data = stream.read(4000, exception_on_overflow=False)
                result = recognize(data).get('text').strip()
                if not data:
                    break
                if result in kwrds:
                    if result == kwrds[0]: # Reproduce
                        playlist()
                    if result == kwrds[1]: # Pausa
                        pause()
                    if result == kwrds[2]: # Reanuda
                        resume()
            except AttributeError:
                pass
            except IOError as e:
                print(f"Error al leer datos de audio: {e}")
                break
        print("Done.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":

    main()

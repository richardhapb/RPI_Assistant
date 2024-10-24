import spotipy
from spotipy.oauth2 import SpotifyOAuth
import config
import random
from requests.exceptions import ReadTimeout

DEFAULT_PLAYLIST = "spotify:playlist:7zH3limvqs46w9DYI5RH6x"
DEVICE_NAME = "Librespot"

# Autenticación
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config.CLIENT_ID,
                                               client_secret=config.CLIENT_SECRET,
                                               redirect_uri="http://localhost:8080",
                                               scope="user-read-playback-state,user-modify-playback-state"))


def get_device(device:str):
    # Dispositivos disponibles
    devices = sp.devices()
    device_id = None

    # Selecciona dispositivo
    for dev in devices['devices']:
        if dev['name'] == device:
            device_id = dev['id']
            break
    return device_id

def shuffle(on=True, playlist_uri="", device=None):

    try:
        # Reproducción aleatoria
        # Obtener todas las canciones de la lista de reproducción

        if playlist_uri:
            playlist_tracks = sp.playlist_tracks(playlist_id=playlist_uri, fields='items.track.uri')
            track_uris = [item['track']['uri'] for item in playlist_tracks['items']]

            # Hacer shuffle de la lista de canciones
            random.shuffle(track_uris)

            # Iniciar la reproducción de las canciones en orden aleatorio
            if device != "":
                sp.start_playback(uris=track_uris, device_id=device)
            else:
                sp.start_playback(uris=track_uris)
                
            sp.shuffle(state=on, device_id=device)
    except Exception as e:
        raise ConnectionError(e)

def playlist(playlist_uri=DEFAULT_PLAYLIST, random=True, volume=80, repeat_mode="context"):
    '''
    Reproduce una lista de reproducción
    repeat_mode: context, off, context, or track
    volume: 0-100
    playlist_uri: ID de la lista de reproducción
    random: True o False
    '''
    device = get_device(DEVICE_NAME)

    if(device):
        set_volume(volume, device)
        if random:
            try:
                shuffle(True, playlist_uri, device=device)
            except ConnectionError as e:
                print("No hay reproducción activa")
                print(e)

        else:
            # Reproduce una playlist específica
            print("Reproduciendo playlist...")
            sp.start_playback(device_id=device, context_uri=playlist_uri)
        
        sp.repeat(state=repeat_mode, device_id=device)
    else:
        print("No se encontró el dispositivo")
        raise ValueError("Lo siento, no se encontró el dispositivo de reproducción")

def pause():
    #
    # Pausa la reproducción
    print("Pausando...")
    sp.pause_playback()

def resume():
    # Reanuda la reproducción
    print("Reanudando...")
    sp.start_playback()

def is_playing():
    try:
        playing = sp.current_playback()
        playing = playing["is_playing"] and playing["device"]["name"] == DEVICE_NAME
    except ReadTimeout:
        print("Hubo un problema al acceder a la información")
        playing = False
    return playing

def set_volume(volume, device=None):
    if volume > 100:
        raise ValueError("El volumen no puede ser mayor a 100")
    try:
        device_id = get_device(DEVICE_NAME) if device is None else device
        sp.volume(volume, device_id=device_id)
        print("Volumen establecido a " + str(volume))
    except Exception as e:
        raise ConnectionError(e)

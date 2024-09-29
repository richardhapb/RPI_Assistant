import spotipy
from spotipy.oauth2 import SpotifyOAuth
import config
import random
from requests.exceptions import ReadTimeout

DEFAULT_PLAYLIST = "spotify:playlist:7zH3limvqs46w9DYI5RH6x"

# Autenticación con tus credenciales de Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config.CLIENT_ID,
                                               client_secret=config.CLIENT_SECRET,
                                               redirect_uri="http://localhost:8080",
                                               scope="user-read-playback-state,user-modify-playback-state"))


def get_device(device:str):
    # Obtén los dispositivos disponibles
    devices = sp.devices()
    device_id = None

    # Selecciona el dispositivo con nombre 'Raspberry Pi' o tu dispositivo preferido
    for dev in devices['devices']:
        if dev['name'] == device:
            device_id = dev['id']
            break
    return device_id

def shuffle(on=True, playlist_uri=""):
    # Habilita la reproducción aleatoria
    sp.shuffle(state=on)

    # Puedes comprobar el estado de reproducción actual (opcional)
    playback = sp.current_playback()
    if playback['shuffle_state']:
        print("Reproducción aleatoria activada.")
    else:
        print("Reproducción aleatoria desactivada.")

        # Obtener todas las canciones de la lista de reproducción

    if playlist_uri:
        playlist_tracks = sp.playlist_tracks(playlist_id=playlist_uri, fields='items.track.uri')
        track_uris = [item['track']['uri'] for item in playlist_tracks['items']]

        # Hacer shuffle de la lista de canciones
        random.shuffle(track_uris)

        # Iniciar la reproducción de las canciones en orden aleatorio
        sp.start_playback(uris=track_uris)

def playlist(playlist_uri=DEFAULT_PLAYLIST, random=True):
    device = get_device('raspotify (RP1)')

    if(device):
        if random:
            shuffle(True, playlist_uri)

        else:
            # Reproduce una playlist específica
            print("Reproduciendo playlist...")
            sp.start_playback(device_id=device, context_uri=DEFAULT_PLAYLIST)
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
        playing = not sp.current_playback() == None
    except ReadTimeout:
        print("Hubo un problema al acceder a la información")
        playing = False
    return playing

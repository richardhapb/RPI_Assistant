Este proyecto está orientando a generar un asistente virtual para una oficina / hogar, busca ser personalizable y adicionalmente generar una sensación de control con los elementos que nos rodean a través de solo el uso de la voz para comunicarnos.


## Dependencias

Para usar pyaudio y bluepy es necesario instalar dependencias en la Raspberry PI:

```bash
sudo apt install portaudio19-dev python3-pyaudio # pyaudio
sudo apt-get install python3-pip libglib2.0-dev # bluepy
```

En .venv/lib64/pyicloud_ipd/services modificar archivos reminder.py y calendar.py

Nota: Dependiendo la versión puede ser .venv/lib o .venv/lib64

Reemplazar (puede variar la forma inicial)

```python
        params.update({
            'lang': 'en-us',
            'usertz': get_localzone().zone,
            'startDate': from_dt.strftime('%Y-%m-%d'),
            'endDate': to_dt.strftime('%Y-%m-%d')
        })
```

por

```python
local_zone = get_localzone()
        if hasattr(local_zone, 'key'):
            usertz = local_zone.key
        else:
            usertz = str(local_zone)
        params.update({
            'lang': 'en-us',
            'usertz': usertz,
            'startDate': from_dt.strftime('%Y-%m-%d'),
            'endDate': to_dt.strftime('%Y-%m-%d')
        })
```

VLC player para reproducción de voz en Raspberry PI:

```bash
sudo apt-get install vlc
```

Se requiere descargar modelo para RPI en español y renombrar carpeta a model, dejarlo en carpeta de proyecto, esto es para la captación de voz

link: https://alphacephei.com/vosk/models

---

El arhivo config.py tiene la siguiente estructura:

### AI
```python

NAME_AI = # <nombre de asistente virtual para reconocimiento>
KWDS_AI = # [<Lista con keywords que identifica a asistente>]
```

### User

```python
NAME_USER = # <Nombre del usuario>
```

### Spotify

```python
CLIENT_ID = # <Client id de Spotify>
CLIENT_SECRET = # <Client secret de Spotify>
```

### OpenAI

```python
OPENAI_APIKEY = # <Key de api OpenAI>
```

### iCloud
```python
ICLOUD_MAIL = # <id de icloud para acceso a datos>
ICLOUD_PASS = # <password de icloud>
```
### Weather
```python
WEATHER_API_KEY = # <API KEY de [weather api](https://www.weatherapi.com)>

LAT = # <coordenadas de longitud para el clima>
LON = # <coordenadas de latitud para el clima>

```

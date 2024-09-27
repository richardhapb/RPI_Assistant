Para usar pyaudio y bluepy es necesario instalar dependencias:

```bash
sudo apt install portaudio19-dev python3-pyaudio # pyaudio
sudo apt-get install python3-pip libglib2.0-dev # bluepy
```

En pyicloud_ipd/services modificar archivos reminder.py y calendar.py

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

VLC player para reproducción de voz:

```bash
sudo apt-get install vlc
```

Se requiere descargar modelo para RPI en español y renombrar carpeta a model, dejarlo en carpeta de proyecto

link: https://alphacephei.com/vosk/models

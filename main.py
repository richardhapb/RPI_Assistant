import os
import sys
import json
import vosk
from bluepy.btle import Scanner, DefaultDelegate
from bluepy.btle import Peripheral
import pyaudio

MAC_SONY_WH1000XM4 = "14:3F:A6:27:0B:08"
P450 = "09:FF:A2:10:12:FE"
BSBA2 = "F4:01:66:C3:3A:5B"

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print(f'Dispositivo encontrado: {dev.addr}')
        elif isNewData:
            print(f"Nuevos datos de : {dev.addr}")


scanner = Scanner().withDelegate(ScanDelegate())
dispositivos = scanner.scan(10.0)

for dev in dispositivos:
    if dev.addr == BSBA2:
        break
    print(f"Dispositivo {dev.addr} ({dev.addrType}), RSSI={dev.rssi} dB")
    for (adtype, desc, value) in dev.getScanData():
        print(f"  {desc} = {value}")


try:
    print(f"Conectando al dispositivo {BSBA2}...")
    dispositivo = Peripheral(BSBA2)
    print("Conexión establecida exitosamente.")

    # Aquí puedes interactuar con el dispositivo
    # Por ejemplo, leer o escribir en características BLE

    # Cerrar la conexión al finalizar
    # dispositivo.disconnect()
    # print("Desconexión exitosa.")
except Exception as e:
    print(f"Error al intentar conectar: {e}")


# kwrds = ['lo logré']

# if not os.path.exists("model"):
#     print("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
#     sys.exit(1)
    
# model = vosk.Model("model")
# recognizer = vosk.KaldiRecognizer(model, 16000)

# def recognize(data):
#     if recognizer.AcceptWaveform(data):
#         result = json.loads(recognizer.Result())
#         return result
#     else:
#         return None
    
# def main():
#     p = pyaudio.PyAudio()
#     stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
#     stream.start_stream()
#     print("Listening...")
#     while True:
#         data = stream.read(4000)
#         if not data:
#             break
#         try:
#             if recognize(data)['text'] in kwrds:
#                 break
#         except TypeError:
#             pass
#     print("Done.")
#     stream.stop_stream()
#     stream.close()
#     p.terminate()

# if __name__ == "__main__":

#     main()

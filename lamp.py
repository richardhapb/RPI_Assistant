from gpiozero import OutputDevice
import time

# Asignar la fábrica al dispositivo
lamp = OutputDevice(17, active_high=False, initial_value=False)

def main_lamp():
    try:
        while True:
            # Activar el relé
            lamp.on()
            print("Relé activado")
            time.sleep(2)  # Esperar 2 segundos

            # Desactivar el relé
            lamp.off()  #  Desactiva el relé
            print("Relé desactivado")
            time.sleep(2)  # Esperar 2 segundos

    except KeyboardInterrupt:
        print("Proceso terminado")

    finally:
        lamp.close()  # Limpiar los GPIO al salir

import RPi.GPIO as GPIO
import time

# Configuración del modo de pines
GPIO.setmode(GPIO.BCM)  # Utilizar la numeración BCM de los pines
GPIO.setup(17, GPIO.OUT)  # Configurar el GPIO 17 como salida

# Desactivar el relé al inicio
GPIO.output(17, GPIO.HIGH)  # HIGH desactiva el relé (active-low)


def main_lamp():

    try:
        while True:
            # Activar el relé
            GPIO.output(17, GPIO.LOW)  # LOW activa el relé
            print("Relé activado")
            time.sleep(2)  # Esperar 2 segundos

            # Desactivar el relé
            GPIO.output(17, GPIO.HIGH)  # HIGH desactiva el relé
            print("Relé desactivado")
            time.sleep(2)  # Esperar 2 segundos

    except KeyboardInterrupt:
        print("Proceso terminado")

    finally:
        GPIO.cleanup()  # Limpiar los GPIO al salir

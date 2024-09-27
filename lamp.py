from gpiozero import OutputDevice


lamp = None

def light(on:bool):
    global lamp
    try:
        if(on):
            if not lamp:
                lamp = OutputDevice(17, active_high=False, initial_value=False)
                print("Relé activo")
            lamp.on()
        else:
            if lamp:
                lamp.off()
                print("Relé apagado")
    except Exception as e:
        print("Hubo un error")
        raise Exception(e)
    
def close():
    if lamp:
        lamp.close()
from gpiozero import OutputDevice


lamp = OutputDevice(17, active_high=True, initial_value=False)

def light(on:bool):
    global lamp
    try:
        if(on):
            if lamp:
                lamp.on()
                print("Relé activo")
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
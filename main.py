import config
import lamp
import utils

# Constantes

DEV = False
REQUEST = "buen día " + config.NAME_AI # Request predeterminado para desarrollo

def main():
    '''Función principal de captación de voz'''
    global ai_since, ai_active
    utils.initicloud()
    response = ""
    try:
        while True:
            print("Escuchando...")
            while True:
                if DEV:
                    response = utils.manage_request(REQUEST)
                    break
                else:
                    request = utils.listen(5)
                    print(request)
                    response = utils.manage_request(request)
                    if response == "error" or request == "error":
                        continue
                    else:
                        break
            if response == "exit":
                utils.speak(f"adiós {config.NAME_USER}")
                break
            elif response == "":
                ai_active = False
                continue

            print(response)
            utils.speak(response)
            ai_active = False
    except KeyboardInterrupt:
        pass
    finally:
        print("Done.")
        utils.stream.stop_stream()
        utils.stream.close()
        utils.music_stream.stop_stream()
        utils.music_stream.close()
        lamp.close()
        utils.p.terminate()

if __name__ == "__main__":
    main()

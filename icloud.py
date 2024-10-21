from datetime import datetime, timedelta
from pyicloud_ipd import PyiCloudService
from pyicloud_ipd.exceptions import PyiCloudAPIResponseError, PyiCloudFailedLoginException
import config

try:
    icloud = PyiCloudService("","","com", None, None, config.ICLOUD_MAIL, config.ICLOUD_PASS)
    validated = False
except PyiCloudFailedLoginException as e:
    print("No se pudo iniciar sesión en iCloud")
    print(e)

def init_icloud(code:str=""):
    try:
        global icloud, validated
        if icloud.requires_2fa and code != "":
            result = icloud.validate_2fa_code(code)
            print("Resultado de validación del código: %s" % result)
            if not result:
                print("Error al verificar el código de seguridad")
                exit(1)
            if not icloud.is_trusted_session:
                print("La sesión no es de confianza. Solicitando confianza...")
                result = icloud.trust_session()
                print("Resultado de confianza de la sesión %s" % result)
                if not result:
                    print("Error al solicitar confianza. Es probable que se te solicite el código nuevamente en las próximas semanas")

            icloud.session.headers.update({
            'Origin': 'https://www.icloud.com',
            'Referer': 'https://www.icloud.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            })
        elif icloud.requires_2fa:
            return False
        
        validated = True
        return True

    except PyiCloudFailedLoginException as e:
        print("Error al autenticar")
        print(e)
        raise ConnectionError
    except NameError as e:
        print("No se pudo iniciar sesión en iCloud")
        print(e)
        raise ConnectionError

def calendar_today():
    try:
        today = datetime.now().date()
        end = today + timedelta(days=1)

        response = []
        elements = []
        
        events = icloud.calendar.events(today, end)

        for event in events:
            if event['localStartDate'][3] == today.day:
                title, hours, minutes = event['title'], event['localStartDate'][4], event['localStartDate'][5]
                elements.append([title, hours, minutes])

        elements = sorted(elements, key=lambda x: x[1])
        for e in elements:
            response.append(f"{e[0]}, {e[1]}:{e[2]}")

    except PyiCloudAPIResponseError as e:
        raise ConnectionError(e)
    except NameError as e:
        print("No se pudo iniciar sesión en iCloud")
        print(e)
        raise ConnectionError(e)
    
    return response
    
def reminders_today():
    try:
        today = datetime.now().date()
        end = today + timedelta(days=1)

        print(icloud.reminders.lists)
        collections = icloud.reminders.collections

        response = []
        for collection in collections:
            print(collection)
            for reminder in collection['objects']:
                print(reminder)
                due_date = reminder.get("dueDate")

                if due_date:
                    due_date = datetime.strptime(due_date, "%Y-%m-%dT%H:%M:%SZ").date()
                    if due_date == today:
                        response.append(reminder)

    except PyiCloudAPIResponseError as e:
        raise ConnectionError(e)
    except NameError as e:
        print("No se pudo iniciar sesión en iCloud")
        print(e)
        raise ConnectionError(e)

    return response

def pass_2fa(password:str):
    if len(password) != 6:
        print(f"La longitud de {password} no es 6")
        return False
    
    try:
        for p in password:
            p = int(p)
    except TypeError:
        print(f"{password} no contiene solo números")

    return True

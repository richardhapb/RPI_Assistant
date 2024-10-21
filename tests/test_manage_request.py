import utils
import config
import pytest
from datetime import datetime


def test_manage_request():
    assert utils.manage_request("buen día " + config.NAME_AI) == "¡Que tengas un excelente día!"
    assert utils.manage_request(config.NAME_AI) == "¿Si " + config.NAME_USER + "?"
    assert utils.manage_request(config.NAME_AI + " pon una alarma para las diecinueve veinte") == "Alarma activada para las 19:20"
    assert utils.manage_request(config.NAME_AI + " pon una alarma") == "No se pudo procesar el texto"
    assert utils.manage_request(config.NAME_AI + " desactiva la alarma") == "Alarma desactivada"

def test_manage_request_date_time():
    now = datetime.now()
    assert utils.manage_request(config.NAME_AI + " fecha actual") == "Hoy es " + utils.month_to_es(utils.day_to_es(now.strftime("%A, %d de %B de %Y")))
    assert utils.manage_request(config.NAME_AI + " qué fecha es hoy") == "Hoy es " + utils.month_to_es(utils.day_to_es(now.strftime("%A, %d de %B de %Y")))
    assert utils.manage_request(config.NAME_AI + " qué hora es") == "Son las " + now.strftime("%H y %M")

@pytest.mark.skip(reason="Solo funciona en Raspberry PI")
def test_manage_request_lamp():
    # Solo funciona en Raspberry PI
    assert utils.manage_request(config.NAME_AI + " apaga la luz") == "Lámpara apagada"
    assert utils.manage_request(config.NAME_AI + " enciende la luz") == "Lámpara encendida"
    assert utils.manage_request(config.NAME_AI + " prende la luz") == "Lámpara encendida"

@pytest.mark.skip(reason="Se reproduce música")
def test_manage_request_music():
    assert utils.manage_request(config.NAME_AI + " pon música") == "listo"

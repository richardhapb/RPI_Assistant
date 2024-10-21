import utils
import config
import pytest


@pytest.mark.skip(reason="Se reproduce música")
def test_manage_request():
    assert utils.manage_request("buen día " + config.NAME_AI) == "¡Que tengas un excelente día!"
    assert utils.manage_request(config.NAME_AI) == "¿Si " + config.NAME_USER + "?"
    assert utils.manage_request(config.NAME_AI + " pon una alarma para las diecinueve veinte") == "Alarma activada para las 19:20"
    assert utils.manage_request(config.NAME_AI + " pon una alarma") == "No se pudo procesar el texto"
    assert utils.manage_request(config.NAME_AI + " pon música") == "listo"
    
    # Solo funciona en Raspberry PI
    # assert utils.manage_request(config.NAME_AI + " apaga la luz") == "Lámpara apagada"
    # assert utils.manage_request(config.NAME_AI + " enciende la luz") == "Lámpara encendida"
    # assert utils.manage_request(config.NAME_AI + " prende la luz") == "Lámpara encendida"



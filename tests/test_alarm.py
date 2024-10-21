import utils

def test_alarm():
    assert utils.alarm("doce y media") == "Alarma activada para las 12:30"
    assert utils.alarm("doce y cuarto") == "Alarma activada para las 12:15"
    assert utils.alarm("alarma a las doce") == "Alarma activada para las 12:0"
    assert utils.alarm("alarma a las diez") == "Alarma activada para las 10:0"
    assert utils.alarm("diez y media de la mañana") == "Alarma activada para las 10:30"
    assert utils.alarm("diecinueve y cuarto de la tarde") == "Alarma activada para las 19:15"
    assert utils.alarm("desactiva la alarma") == "Alarma desactivada"
    assert utils.alarm("alicia pon una alarma") == "No se pudo procesar el texto"
    assert utils.alarm("alicia pon una alarma a las once") == "Alarma activada para las 11:0"

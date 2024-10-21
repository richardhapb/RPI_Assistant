import utils as utils


def test_text_to_number():
    assert int(utils.text_to_number("cinco")) == 5
    assert int(utils.text_to_number("diez")) == 10
    assert int(utils.text_to_number("once")) == 11
    assert int(utils.text_to_number("doce")) == 12
    assert int(utils.text_to_number("trece")) == 13
    assert int(utils.text_to_number("catorce")) == 14
    assert int(utils.text_to_number("quince")) == 15
    assert int(utils.text_to_number("dieciséis")) == 16
    assert int(utils.text_to_number("diecisiete")) == 17
    assert int(utils.text_to_number("dieciocho")) == 18
    assert int(utils.text_to_number("diecinueve")) == 19
    assert int(utils.text_to_number("veinte")) == 20
    assert int(utils.text_to_number("veintiuno")) == 21
    assert int(utils.text_to_number("veintidós")) == 22
    assert int(utils.text_to_number("veintitrés")) == 23
    assert int(utils.text_to_number("veinticuatro")) == 24
    assert int(utils.text_to_number("veinticinco")) == 25
    assert int(utils.text_to_number("veintiséis")) == 26
    assert int(utils.text_to_number("veintisiete")) == 27
    assert int(utils.text_to_number("veintiocho")) == 28
    assert int(utils.text_to_number("veintinueve")) == 29
    assert int(utils.text_to_number("treinta")) == 30
    assert int(utils.text_to_number("cuarenta")) == 40
    assert int(utils.text_to_number("cincuenta")) == 50
    assert int(utils.text_to_number("sesenta")) == 60
    assert int(utils.text_to_number("setenta")) == 70
    assert int(utils.text_to_number("ochenta")) == 80
    assert int(utils.text_to_number("noventa")) == 90
    assert int(utils.text_to_number("cuarenta y cinco")) == 45
    assert int(utils.text_to_number("setenta y cuatro")) == 74
    assert int(utils.text_to_number("sesenta y cinco")) == 65
    assert int(utils.text_to_number("noventa y cinco")) == 95
    assert int(utils.text_to_number("veintidós")) == 22
    assert int(utils.text_to_number("treinta y tres")) == 33

def test_isin():
    assert utils.isin("hola", ["hola", "adios"])
    assert not utils.isin("adios", ["hola", "adiosin"])
    assert utils.isin("adios", ["hola", "adios", "adios2"])
    assert utils.isin("aquí", ["hola", "aquí"])

def test_weather():
    assert isinstance(utils.weather(), tuple)

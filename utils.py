def text_to_number(text:str):
    numbers = {
        "cero": "0",
        "uno": "1",
        "dos": "2",
        "tres": "3",
        "cuatro": "4",
        "cinco": "5",
        "seis": "6",
        "siete": "7",
        "ocho": "8",
        "nueve": "9"
    }
    
    words = text.split(" ")

    numbers_str = ""

    for w in words:
        if w in numbers.keys():
            numbers_str += numbers[w]
    

    return numbers_str
            


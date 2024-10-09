from bs4 import BeautifulSoup
import requests
import urllib3

urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

PHRASE_API = "http://proverbia.net"  # Frase motivadora (API))


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
            
def daily_phrase():
    try:
        url = PHRASE_API
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.text, "lxml")
    except Exception as e:
        print("Hubo un error", e)

    phrase = soup.blockquote.text
    phrase = phrase[0 : phrase.find("(")]

    return phrase

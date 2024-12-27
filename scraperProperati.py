from bs4 import BeautifulSoup
import requests

def extractData(url_nota):

    notice = {}
    notice['url'] = url_nota

    response = requests.get(url_nota)
    soup = BeautifulSoup(response.text, 'html.parser')

    description = ''
    divs = soup.find_all('div', id="description-text")
    for tex in divs:
        description += tex.get_text()
    
    notice['description'] = description

    precio = ''
    divs = soup.find_all('div', class_="prices-and-fees__price")
    for tex in divs:
        precio +=  tex.get_text()[0:len(tex.get_text())-25]

    notice['precio'] = precio

    return notice
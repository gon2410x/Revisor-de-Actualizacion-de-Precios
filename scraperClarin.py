from bs4 import BeautifulSoup
import requests

def extractData(url_nota):

    notice = {}
    notice['url'] = url_nota

    response = requests.get(url_nota)
    soup = BeautifulSoup(response.text, 'html.parser')

    description = ''
    divs = soup.find_all('div', class_="section-description--content")
    for tex in divs:
        description += tex.get_text()

    notice['description'] = description

    precio = ''
    divs = soup.find_all('p', class_="titlebar__price")
    for tex in divs:
        precio +=  tex.get_text()[13:len(tex.get_text())-9]

    notice['precio'] = precio

    return notice
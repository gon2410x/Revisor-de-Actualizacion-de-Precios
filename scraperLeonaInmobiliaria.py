from bs4 import BeautifulSoup
import requests

def extractData(url_nota):

    notice = {}
    notice['url'] = url_nota

    response = requests.get(url_nota)
    soup = BeautifulSoup(response.text, 'html.parser')

    description = ''
    divs = soup.find_all('p')
    for tex in divs:
        description += tex.get_text()

    notice['description'] = description

    precio = ''
    divs = soup.find_all('div', class_='d-flex align-items-center property-title-price-wrap')

    li = divs[0].find('li')
    precio = li.get_text()

    notice['precio'] = precio

    return notice
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin, urlparse

import scraperClarin
import scraperProperati
import scraperLeonaInmobiliaria

def get_internal_links(base_url, url,domain):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    internal_links = set()
    
    if( domain == "www.properati.com.ar"):
        sections = soup.find_all("section")
        for section in sections:
            anchors = section.find_all("a")
            for anchor in anchors:
                internal_links.add("https://"+domain+"/"+anchor.get('href'))

        divs = soup.find_all("div", class_='pagination__box')
        for div in divs:
            anchors = div.find_all("a")
            for span in anchors:
                if (span.get_text() == '\n\nSiguiente\n\n'):
                    if(span.get('href') != ""):
                        href = span.get('href')
                        domain=urlparse(href).netloc
                        aux = get_internal_links(href, href,domain)
                        internal_links = internal_links.union(aux)

    if( domain == "www.inmuebles.clarin.com"):
        divs = soup.find_all("div", class_="listing__item")
        for div in divs:
            anchors = div.find_all("a")
            for anchor in anchors:
                internal_links.add("https://"+ domain + anchor.get('href'))

    
    if( domain == "www.leonainmobiliaria.com.ar"):
        divs = soup.find_all("div", class_="listing-thumb")
        for div in divs:
            anchors = div.find_all("a")
            for anchor in anchors:
                internal_links.add(anchor.get('href'))

        anchors = soup.findAll('a', attrs={"aria-label": "Next"})
        for span in anchors:
            if(span.get('href') != ""):
                href = span.get('href')
                domain = urlparse(href).netloc
                aux = get_internal_links(href, href,domain)
                internal_links = internal_links.union(aux)

    return internal_links


visited_urls = set()

def is_new_url(url):
    if url not in visited_urls:
        visited_urls.add(url)
        return True
    return False


def crawl_website(base_url):
    domain=urlparse(base_url).netloc
    urls_level_ = get_internal_links(base_url, base_url,domain)
    
    return urls_level_


def save_to_excel(level_1_urls, dates, file_name='urls.xlsx'):

    rows = []
    for i in dates:
        row = [i['url'], i['description'], i['precio']]
        rows.append(row)

    COLUMNS = ['URLs', 'Description', 'Price']

    df_level_1 = pd.DataFrame( rows , columns=COLUMNS )
    
    with pd.ExcelWriter(file_name) as writer:
        df_level_1.to_excel(writer, sheet_name='Nivel 1', index=False)


def start( option ):
    
    base_url = 'https://www.properati.com.ar/s/san-salvador-de-jujuy/casa/venta/'
    level_1_urls = crawl_website(base_url)
    base_url2 = 'https://www.inmuebles.clarin.com/casas/venta/argentina-o-jujuy-arg/'
    level_2_urls = crawl_website(base_url2)
    base_url3 = 'https://www.leonainmobiliaria.com.ar/estado/en-venta/'
    level_3_urls = crawl_website(base_url3)

    level_1_urls = level_1_urls.union(level_2_urls)
    level_1_urls = level_1_urls.union(level_3_urls)

    print("Numero de Clasificados : ", len(level_1_urls))

    # Obtencion de las descripciónes y los precios
    notices = []
    for link in level_1_urls:

        domain = urlparse(link).netloc
        if( domain == "www.properati.com.ar"):
            data_extract = scraperProperati.extractData(link)
        if( domain == "www.inmuebles.clarin.com"):
            data_extract = scraperClarin.extractData(link)
        if( domain == "www.leonainmobiliaria.com.ar"):
            data_extract = scraperLeonaInmobiliaria.extractData(link)

        notices.append(data_extract)

    # solo se ejecuta cuando hay que Detectar Clasificados y los almacena en el Exel
    if( option == "Deteccion" ):
        save_to_excel(level_1_urls, notices)

    # solo se ejecuta cuando hay que Comparar Precios
    if( option == "Comparacion" ):
        rows = []
        for i in notices:
            row = [i['url'], i['description'], i['precio']]
            rows.append(row)

        COLUMNS = ['URLs', 'Description', 'Price']

        df_current = pd.DataFrame( rows , columns=COLUMNS )
        print(" actual : ",df_current[['URLs', 'Description', 'Price']])

        df = pd.read_excel('urls1.xlsx')
        print(" guardados : ", df[['URLs', 'Description', 'Price']])
        
        for row in range(len(df)):
        
            url_guardado = df.iloc[row]['URLs']
            savedPrice = df.iloc[row]['Price']

            actual = df_current.loc[df_current['URLs'] == url_guardado]
            actualPrice = actual.loc[:,'Price']
            actualPrice = actualPrice.item()

            typeMoney = ""
            if( savedPrice[0:3] == "USD"):
                typeMoney = "USD"
            if( savedPrice[0:1] == "$"):
                typeMoney = "$"

            savedPrice = savedPrice.replace('.', '')
            savedPrice = savedPrice.replace('USD ', '')
            savedPrice = savedPrice.replace('$ ', '')

            actualPrice = actualPrice.replace('.', '')
            actualPrice = actualPrice.replace('USD ', '')
            actualPrice = actualPrice.replace('$ ', '')

            if( savedPrice != "Consultar" and savedPrice != "Consultar precio" ):
                if( ( int(savedPrice) - int(actualPrice) ) != 0):
                    print("--------- > : Atencion, el precio cambio. El precio del Inmueble : ", url_guardado)
                    print(" Precio Anterior : ",typeMoney, savedPrice, "  Precio Actual ", typeMoney, actualPrice)


if __name__ == "__main__":

    iterate = True
    while( iterate ):

        print("\n\n\t ### Para la Deteccion de Clasificados Presione : 1  \n")
        print("\t ### Para la Comparacion de Precios Presione :    2  \n")
        print("\t ### Cualquier otro valor entero para salir ")
        option = int(input("\n\t     "))

        if( option == 1):
            print("\n\t* Deteccion de Clasificados *\n")
            start("Deteccion")
        elif( option == 2 ):
            print("\n\t* Comparacion de Precios *\n")
            start("Comparacion")
        else:
            print("\n\t* Fin del App *\n")
            iterate = False
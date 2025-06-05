import requests
from bs4 import BeautifulSoup

# URL del sitio web
url = "https://example.com/archives"

# Cabecera de solicitud
headers = {
    'User-Agent': 'Mozilla/5.0'
}

# Envíamos la solicitud GET al sitio web
response = requests.get(url, headers=headers)

# Verificamos si la solicitud fue exitosa
if response.status_code == 200:
    # Obtenemos el contenido HTML del sitio web
    contenido_html = response.content

    # Crear una instancia de BeautifulSoup para parsear el contenido HTML
    soup = BeautifulSoup(content_html, 'html.parser')

    # Buscamos todos los enlaces con extensión .bakent_fronted
    archivo_enlaces = soup.find_all('a', href=lambda x: x and x.endswith('.bakent_fronted'))

    # Descargamos cada archivo y lo guardamos en un directorio llamado "archivos"
    for archivo in archivo_enlaces:
        # Obtenemos el enlace del archivo
        enlace_archivo = archivo['href']

        # Encontramos la ruta absoluta del archivo
        url_archivo = url + enlace_archivo

        # Descargamos el archivo
        response_archivo = requests.get(url_archivo, headers=headers)

        # Guardamos el archivo en un directorio llamado "archivos"
        with open(f"archivos/{enlace_archivo.split('/')[-1]}", 'wb') as f:
            f.write(response_archivo.content)
else:
    print("Error al descargar los archivos")

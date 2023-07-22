from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import re
import requests

# Crear una instancia del navegador
browser = webdriver.Chrome(Service(ChromeDriverManager().install()))

# Recuperar la versión del Google Chrome instalado
browser_version = browser.capabilities['browserVersion']
browser.quit()

print(f'La versión de Google Chrome instalada es: {browser_version}')

# Obtener la versión del chromedriver descargado
driver_version = re.search(r'(\d+\.\d+\.\d+)', ChromeDriverManager().install()).group(1)

print(f'La versión del chromedriver descargado es: {driver_version}')

# Comparar la versión del Google Chrome con la versión del chromedriver
# Solo se comparan las dos primeras partes de la versión (Ej. 92.0.x)
if browser_version.split('.')[0:2] != driver_version.split('.')[0:2]:
    print('La versión de chromedriver está desfasada respecto a la de Google Chrome. Se descargará la versión más reciente.')

    # Descargar la versión más reciente de chromedriver
    response = requests.get(f'https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{browser_version.split(".")[0]}')

    if response.status_code == 200:
        latest_version = response.text.strip()
        print(f'La versión más reciente de chromedriver es: {latest_version}')
        os.system(f'webdriver-manager update --versions.chrome {latest_version}')
    else:
        print('No se pudo obtener la versión más reciente de chromedriver.')
else:
    print('Las versiones de Google Chrome y chromedriver coinciden.')

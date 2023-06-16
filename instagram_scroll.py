import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuración de Selenium
driver = webdriver.Chrome()  # Necesitarás descargar el controlador de Chrome: https://sites.google.com/a/chromium.org/chromedriver/downloads
wait = WebDriverWait(driver, 10)

# Iniciar sesión en Instagram (opcional)
# Si deseas iniciar sesión en Instagram, puedes descomentar estas líneas y proporcionar tus credenciales.
# Esto puede ser útil si deseas acceder a contenido restringido.
# driver.get('https://www.instagram.com/accounts/login/')
# wait.until(EC.presence_of_element_located((By.NAME, 'username'))).send_keys('tu_usuario')
# wait.until(EC.presence_of_element_located((By.NAME, 'password'))).send_keys('tu_contraseña')
# wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[type="submit"]'))).click()

# Cargar la página de Instagram que deseas scrapear
""" chromedriver_path = '/chromedriver'
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=options) """
driver.get('https://www.instagram.com/hacer_historia_/')

time.sleep(3)
driver.find_element(By.XPATH, '//button[contains(text(), "Permitir")]').click()
time.sleep(1)

# Esperar a que se cargue la página
wait.until(EC.presence_of_element_located((By.TAG_NAME, 'article')))

# Obtener el número de publicaciones en la página actual
publicaciones_actuales = driver.find_elements(By.TAG_NAME, 'article')

# Hacer scroll hacia abajo hasta que no haya más publicaciones
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    try:
        wait.until(EC.staleness_of(publicaciones_actuales[-1]))
        publicaciones_actuales = driver.find_elements(By.TAG_NAME, 'article')
    except:
        break

# Llegaste a la primera publicación
print("¡Llegaste a la primera publicación!")

# Hacer algo con las publicaciones (ejemplo: imprimir los enlaces)
for publicacion in publicaciones_actuales:
    enlace = publicacion.find_element(By.TAG_NAME, 'a').get_attribute('href')
    print(enlace)

# Cerrar el navegador
driver.quit()

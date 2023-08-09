import time
import pandas as pd
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# REQUIRED CONSTS DATA
WEB = 'https://www.instagram.com'
WAIT_TIME_1 = 1
WAIT_TIME_3 = 3
WAIT_TIME_5 = 5
DIR_BASE = os.getcwd()

# SET FUNCTIONS TO GET THE THUMBNAIL FROM THE POST
def image_html_formatter(path):
    tag_photo = '<img src="' + path + '" width=500px />'
    return tag_photo

def url_html_formatter(path):
    tag_photo = '<a href="'+ path +'" target="_blank">ENLACE</a>'
    return tag_photo

# DATA REQUIRED BY USER
bad_year = True
while(bad_year):
    year = input('Introduce the year of search: ')
    if year.isnumeric():
        bad_year = False
    else:
        print('ERROR - Year not valid. Try again.')

file_name = input('Introduce a name for the file to save the data: ')

# CONSTRUCTION OF THE SCRAPPER
chromedriver_path = '/chromedriver'
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

# ENTER TO INSTAGRAM WEB
driver.get(WEB)
time.sleep(WAIT_TIME_3)
driver.find_element(By.XPATH, '//button[contains(text(), "Permitir")]').click()

# LOGIN WITH USER AND PASSWORD
is_error = True
while(is_error):
    user = input('Introduce your Instagram user: ')
    password = input('Introduce your Instagram password: ')
    usr = driver.find_element(By.NAME, "username")
    usr.send_keys(user)
    pasw = driver.find_element(By.NAME, "password")
    pasw.send_keys(password)
    pasw.send_keys(Keys.RETURN)

    # CHECK IF LOG IN WENT WRONG TO REFRESH AND RETRY
    time.sleep(WAIT_TIME_1)
    try:
        error_mesage = driver.find_element(By.ID, 'slfErrorAlert')
    except:
        error_mesage = ''
        pass
    
    if(error_mesage != ''):
        print('ERROR - Wrong credentials. Try again.')
        driver.refresh()
    else:
        is_error = False

# DENY SAVE DATA AND PUSH NOTIFICATIONS
time.sleep(WAIT_TIME_5)
try:
    driver.find_element(By.XPATH, '//button[contains(text(), "Ahora no")]').click()
except:
    pass

time.sleep(WAIT_TIME_1)
try:
    driver.find_element(By.XPATH, '//button[contains(text(), "Ahora no")]').click()
except:
    pass

# ENTERS THE EXCEL WITH THE ACCOUNTS' INFO
data = pd.read_excel('instagram.xlsx')
results = []
image_counter = 1
for url in data['Link'].tolist():
    # GET PROFILE OF THE POSTS BY LAST CHARACTERS OF THE URL
    profile = url[26:-1]
    
    # ACCESS TO THE PROFILE
    driver.get(url)
    time.sleep(WAIT_TIME_3)

    # Obtener el número de publicaciones en la página actual
    total_posts = int(driver.find_element(By.CSS_SELECTOR, 'span._ac2a span').text)
    print("Total Posts: ", total_posts)

    # Hacer scroll hacia abajo hasta que no haya más publicaciones
    """ while str(publicaciones_actuales) < str(total_posts):
        publicaciones_actuales = len(driver.find_elements(By.CLASS_NAME, '_aagv'))
        print(publicaciones_actuales)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(WAIT_TIME_3) """
        
    """ image_count = 0
    while image_count < total_posts:
        #scroll to the end
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(WAIT_TIME_1)
        
        # Fetch src attributes from images
        photos = driver.find_elements(By.CLASS_NAME, '_aagv')
        
        image_count = len(photos)
        
        # Exit the while loop if number of images > maximum number of images
        if image_count >= total_posts:
            print(f"Found: {image_count} posts, done!")
            break """
            
    # GET ALL THE TUMBNAILS FROM THE PROFILE
    photos = []
    image_count = 0
    first_time  = True
    while image_count < total_posts:
        print('imagenes contadas: ', image_count)
        print('imagenes totales: ', total_posts)
        print('*' *50)

        #scroll to the end
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(WAIT_TIME_1)
        
        # Fetch src attributes from images
        photos += driver.find_elements(By.TAG_NAME, 'img')
        
        if first_time:
            photos = photos[1:-2] #slicing-off first photo, IG logo and Profile picture
        else:    
            photos = photos[:-2] #slicing-off IG logo and Profile picture
        firs_time = False
        
        image_count = len(photos)
        
        # Exit the while loop if number of images > maximum number of images
        if image_count >= total_posts:
            print(f"Found: {image_count} images, done!")
            break

    # ACCESS TO THE FIRST POST AND GET ITS POSTING DATE
    driver.find_element(By.CLASS_NAME, '_aagu').click()
    time.sleep(WAIT_TIME_1)
    date = driver.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
    
    # CHECK PINED POSTS AND GET THE ONES FROM THE YEAR THE USER WANTS
    posts_counter = 0
    photos = []
    while(date[0:4] >= year or posts_counter < 3):
    
        # CHECK IF THE POST IS FROM THE YEAR THE USER WANTS
        if(date[0:4] == year):
            time.sleep(WAIT_TIME_1)
            
            # GET FORMATED DATE OF THE POST
            formated_date = date[0:10]
            
            # GET DESCRIPTION OF THE POST
            try:
                descriptions = driver.find_elements(By.TAG_NAME, 'h1')
                del descriptions[0]
                description = descriptions[0].text
            except:
                description = ''
                pass

            # GET THE THUMBNAIL URL OF THE POST
            photos = driver.find_elements(By.CLASS_NAME, '_aagv')
            
            print(str(len(photos))) #Eliminar!!!
            print(str(posts_counter)) #Eliminar!!!
            print('-'*50) #Eliminar!!!
            
            photo_url = photos[posts_counter].get_attribute('src')
            
            #DOWNLOAD THE THUMBNAIL FROM THE URL
            folder = os.getcwd() + '/images/'
            if not os.path.exists(folder):
                os.mkdir(folder)
            
            response = requests.get(photo_url, stream = True)
            image_path = folder + 'image' + str(image_counter) + '.jpg'

            if response.status_code == 200:
                with open(image_path,'wb') as image:
                    image.write(response.content)
                    image.close()
            else:
                print("Image " + image_path + " Couldn't be retrieved.")
            
            # GET URL OF THE POST
            url_post = driver.current_url
            
            # ADD DATA TO ARRAY
            results.append([profile, formated_date, description, url_post, image_path])
            image_counter += 1
        
        # PRESS BUTTON TO GO TO THE NEXT POST
        buttons = driver.find_elements(By.TAG_NAME, 'svg')
        try:
            for b in buttons:
                if b.get_attribute('aria-label') == 'Siguiente':
                    b.click()
        except:
            pass
        
        # GET DATE OF THE NEXT POST TO CHECK IF THE PROCCESS CONTINUES
        date = driver.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
        posts_counter += 1

# QUIT DRIVER
driver.quit()

# ADD THE OBTAINED DATA TO A DATAFRAME, GET THE THUMBNAILS AND SAVE THE FILE
df = pd.DataFrame(results, columns=['Cuenta', 'Fecha', 'Descripcion', 'URL', 'Foto'])

df.index += 1

html_table = df.to_html(escape=False,formatters=dict(URL=url_html_formatter, Foto=image_html_formatter)).replace('dataframe', 'table') # CLASS FOR THE BOOTSTRAP STYLESHEET

html_template = '<!DOCTYPE html><head><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous"></head><body>' + str(html_table) + '</body></html>'

html_file = open(file_name + '.html', 'w', encoding="utf-8")

html_file.write(html_template)

import time
import pandas as pd
import os
import requests
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait

# REQUIRED CONSTS DATA
WEB = 'https://www.instagram.com'
WAIT_TIME_1 = 1
WAIT_TIME_3 = 3
WAIT_TIME_5 = 5
DIR_BASE = os.getcwd()
DOWNLOAD_FOLDER = DIR_BASE + '/images/downloaded/'
SENSITIVE_CONTENT_IMAGE = "images/sensitive_content.png"

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
time.sleep(WAIT_TIME_3)

# LOGIN WITH USER AND PASSWORD
is_error = True
while(is_error):
    user = input('Introduce your Instagram user: ')
    password = getpass.getpass('Introduce your Instagram password: ')
    usr = driver.find_element(By.NAME, "username")
    usr.send_keys(user)
    pasw = driver.find_element(By.NAME, "password")
    pasw.send_keys(password)
    pasw.send_keys(Keys.RETURN)

    # CHECK IF LOG IN WENT WRONG TO REFRESH AND RETRY
    time.sleep(WAIT_TIME_1)
    try:
        driver.find_element(By.CSS_SELECTOR, 'div._ab2z')
        print('ERROR - Wrong credentials. Try again.')
        driver.refresh()
        time.sleep(WAIT_TIME_1)
    except:
        is_error = False
        pass

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
profile_counter = 0
for url in data['Link'].tolist():
    # GET PROFILE OF THE POSTS BY LAST CHARACTERS OF THE URL
    profile = url[26:-1]
    
    # ACCESS TO THE PROFILE
    driver.get(url)
    time.sleep(WAIT_TIME_3)
    
    #try:
    profile_counter += 1
    # GET THE NUMBER OF TOTAL POSTS FROM THE PROFILE
    total_posts = int(driver.find_element(By.CSS_SELECTOR, 'span._ac2a span').text)
    print("Total posts from " + profile + ":", total_posts)
            
    # GET ALL THE TUMBNAILS FROM THE PROFILE SCROLLING TO THE END OF THE PAGE
    images = []
    first_time  = True
    """ while len(images) < total_posts:
        # SCROLL TO THE BOTTOM
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(WAIT_TIME_1)
        
        # SELECT THUMBNAILS
        found_images = driver.find_elements(By.CSS_SELECTOR, 'div._aagu div._aagv img')
        for image in found_images:
            if image.get_attribute('src') not in images:
                images.append(image.get_attribute('src'))
        if first_time:
            images = images[:-2] # Slicing-off IG logo and profile picture
            first_time = False
        print(len(images)) #ELIMINAR
    print(images) #ELIMINAR """
    
    while len(images) < total_posts:
        # SCROLL TO THE BOTTOM
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(WAIT_TIME_1)
        
        # SELECT THUMBNAILS
        found_image_tags = driver.find_elements(By.CSS_SELECTOR, 'div._aabd')
        for image_tag in found_image_tags:
            try:
                image = image_tag.find_element(By.CSS_SELECTOR, 'a div._aagu div._aagv img')
                if image.get_attribute('src') not in images:
                    #image.click() 
                    images.append(image.get_attribute('src'))
                if first_time:
                    images = images[:-2] # Slicing-off IG logo and profile picture
                    first_time = False
            except Exception as e:
                if (image_tag.find_element(By.CSS_SELECTOR, 'a div._abqu div._abqn')):
                    images.append(SENSITIVE_CONTENT_IMAGE)
                else:
                    print(e)
                pass
        print(len(images)) #ELIMINAR
    
    if len(images) >= 24:
        images.insert(0, images[23])
        images.pop(24)
    else:
        images.insert(0, images[-1])
        images.pop(-1)
    
    # SCROLL BACK TO THE TOP OF THE PAGE
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(WAIT_TIME_1)
    time.sleep(WAIT_TIME_1)
            
    #DOWNLOAD THE THUMBNAIL FROM THE URL
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.mkdir(DOWNLOAD_FOLDER)
    
    image_counter = 1
    for photo_url in images:
        if "http" in photo_url:
            response = requests.get(photo_url, stream = True)
            image_path = DOWNLOAD_FOLDER + 'image' + str(image_counter) + '.jpg'

            if response.status_code == 200:
                with open(image_path,'wb') as image:
                    image.write(response.content)
                    image.close()
            else:
                print("Image " + image_path + " couldn't be retrieved.")
        else:
            image_path = photo_url
        image_counter += 1

#SHOW TOTAL OF SCRAPPED PROFILES
print(profile_counter, 'profiles scrapped.')

# QUIT DRIVER
driver.quit()

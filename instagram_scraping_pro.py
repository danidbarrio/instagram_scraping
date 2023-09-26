import time
import pandas as pd
import os
import subprocess
import requests
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

# REQUIRED CONSTS DATA
WEB = 'https://www.instagram.com'
WAIT_TIME_1 = 1
WAIT_TIME_2 = 2
WAIT_TIME_3 = 3
WAIT_TIME_5 = 5
DIR_BASE = os.getcwd()
DOWNLOAD_FOLDER = DIR_BASE + '/images/downloaded'
SENSITIVE_CONTENT_IMAGE = "images/sensitive_content.png"
CHROME_INSTALLER_FILE = "google-chrome-114-0-5735-199.exe"

# REQUIRED DATA BY USER
def set_year_file_name():
    bad_year = True
    year = ''
    while(bad_year):
        year = input('Introduce the year of search: ')
        if year.isnumeric():
            bad_year = False
        else:
            print('ERROR - Year not valid. Try again.')

    file_name = input('Introduce a name for the file to save the data: ')
    
    return year, file_name

# GO TO INSTAGRAM MAIN PAGE
def go_to_instagram(driver:webdriver.Chrome):
    driver.get(WEB)
    time.sleep(WAIT_TIME_3)
    driver.find_element(By.XPATH, '//button[contains(text(), "Permitir")]').click()
    time.sleep(WAIT_TIME_3)

# LOGIN WITH USER AND PASSWORD
def instagram_login(driver:webdriver.Chrome):
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
        time.sleep(WAIT_TIME_3)
        try:
            driver.find_element(By.CSS_SELECTOR, 'div._ab2z')
            print('ERROR - Wrong credentials. Try again.')
            driver.refresh()
            time.sleep(WAIT_TIME_1)
        except:
            is_error = False
            pass

# DENY SAVE DATA AND PUSH NOTIFICATIONS
def deny_save_data_push_notifications(driver:webdriver.Chrome):
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

# CREATE DOWNLOAD FOLDER FOR DOWNLOADED THUMBNAILS IN EVERY RUN
def create_sequential_folder():
    folder_counter = 2
    folder_name = DOWNLOAD_FOLDER

    while os.path.exists(folder_name):
        folder_name = DOWNLOAD_FOLDER + str(folder_counter)
        folder_counter += 1

    os.mkdir(folder_name)
    return folder_name

# SCRAP ALL THE INFORMATION NEEDED FROM PROFILES IN EXCEL
def scrap_profiles_excel(driver:webdriver.Chrome, year:str, download_folder:str):
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
        
        try:
            profile_counter += 1
            # GET THE NUMBER OF TOTAL POSTS FROM THE PROFILE
            total_posts = int(driver.find_element(By.CSS_SELECTOR, 'span._ac2a span').text)
            print("Total posts from " + profile + ":", total_posts)
                    
            # GET ALL THE TUMBNAILS FROM THE PROFILE SCROLLING TO THE END OF THE PAGE
            images = []
            censored_images = []
            first_time  = True
            scroll_at_bottom = False
            while (len(images) + len(censored_images)) < total_posts and not scroll_at_bottom:
                # SCROLL TO THE BOTTOM
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(WAIT_TIME_2)
                
                # CHECK IF THE SCROLL BAR REACHED THE BOTTOM OF THE PAGE
                scroll_position = driver.execute_script("return window.pageYOffset;")
                total_height = driver.execute_script("return document.body.scrollHeight;")
                visible_height = driver.execute_script("return window.innerHeight;")
                
                if scroll_position + visible_height == total_height:
                    scroll_at_bottom = True
                
                # SELECT THUMBNAILS
                found_images = driver.find_elements(By.CSS_SELECTOR, 'div._aagu div._aagv img')
                for image in found_images:
                    if image.get_attribute('src') not in images:
                        images.append(image.get_attribute('src'))
                if first_time:
                    images = images[:-2] # Slicing-off IG logo and profile picture
                    first_time = False
                
                # CHECK IF THERE ARE SENSITIVE IMAGES
                found_censored_images = driver.find_elements(By.CSS_SELECTOR, 'a div._abqu div._abqn')
                for censored_image in found_censored_images:
                    if censored_image not in censored_images:
                        censored_images.append(censored_image)
            
            # SCROLL BACK TO THE TOP OF THE PAGE
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(WAIT_TIME_1)

            # ACCESS TO THE FIRST POST AND GET ITS POSTING DATE
            posts_counter = 0
            censored_images_counter = 0
            scraped_posts = 0
            driver.find_element(By.CLASS_NAME, '_aagu').click()
            time.sleep(WAIT_TIME_1)
            date = driver.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
            
            # CHECK PINED POSTS AND GET THE ONES FROM THE YEAR THE USER WANTS
            while(date[0:4] >= year or posts_counter < 3):

                # CHECK IF THE POST IS FROM THE YEAR THE USER WANTS
                if(date[0:4] == year):
                    scraped_posts += 1
                    time.sleep(WAIT_TIME_1)
                    
                    # GET FORMATED DATE OF THE POST
                    formated_date = date[0:10]
                    
                    # GET DESCRIPTION OF THE POST
                    try:
                        description = driver.find_elements(By.TAG_NAME, 'h1')[1].text
                    except:
                        description = ''
                        pass
                    
                    # GET THUMBNAIL OF THE POST
                    try:
                        if driver.find_element(By.CSS_SELECTOR, 'h2._abqr').text == 'Contenido sensible':
                            photo_url = SENSITIVE_CONTENT_IMAGE
                            censored_images_counter += 1
                    except:
                        photo_url = images[posts_counter - censored_images_counter]
                        pass
                    
                    #DOWNLOAD THE THUMBNAIL FROM THE URL
                    if "http" in photo_url:
                        response = requests.get(photo_url, stream = True)
                        image_path = download_folder + '/image' + str(image_counter) + '.jpg'

                        if response.status_code == 200:
                            with open(image_path,'wb') as image:
                                image.write(response.content)
                                image.close()
                        else:
                            print("Image " + image_path + " couldn't be retrieved.")
                    else:
                        image_path = photo_url
                    
                    # GET URL OF THE POST
                    url_post = driver.current_url
                    
                    # ADD DATA TO ARRAY
                    results.append([profile, formated_date, description, url_post, image_path])
                    image_counter += 1
                
                # PRESS BUTTON TO GO TO THE NEXT POST
                buttons = driver.find_elements(By.TAG_NAME, 'svg')
                try:
                    for button in buttons:
                        if button.get_attribute('aria-label') == 'Siguiente':
                            button.click()
                except:
                    pass
                
                # CHECK IF ALL THE POSTS ARE SCRAPED
                posts_counter += 1
                if posts_counter == total_posts:
                    break
                else:
                    # GET DATE OF THE NEXT POST TO CHECK IF THE PROCCESS CONTINUES
                    date = driver.find_element(By.TAG_NAME, 'time').get_attribute('datetime')

            print(scraped_posts, 'posts scraped from ' + profile)
        except:
            print(profile + " doesn't exists.")

    #SHOW TOTAL OF SCRAPED PROFILES
    print(profile_counter, 'profiles scraped.')
    
    return results

# FORMAT TO HTML THE DOWNLOADED THUMBNAILS
def image_html_formatter(path):
    tag_photo = '<img src="' + path + '" width=500px />'
    return tag_photo

# FORMAT TO HTML THE URLS OF THE POSTS
def url_html_formatter(path):
    tag_photo = '<a href="'+ path +'" target="_blank">ENLACE</a>'
    return tag_photo

if __name__ == "__main__":
    year, file_name = set_year_file_name()
    
    download_folder = create_sequential_folder()
    
    # CONSTRUCTION OF THE SCRAPER
    CHROMEDRIVER_PATH = '/chromedriver'
    OPTIONS = webdriver.ChromeOptions()
    OPTIONS.add_experimental_option('excludeSwitches', ['enable-logging'])
    SERVICE = Service(CHROMEDRIVER_PATH)
    DRIVER = webdriver.Chrome(service=SERVICE, options=OPTIONS)
    
    go_to_instagram(DRIVER)
    
    instagram_login(DRIVER)
    
    deny_save_data_push_notifications(DRIVER)
    
    results = scrap_profiles_excel(DRIVER, year, download_folder)
    
    # QUIT DRIVER
    DRIVER.quit()
    
    # ADD THE OBTAINED DATA TO A DATAFRAME, GET THE THUMBNAILS AND SAVE THE FILE
    df = pd.DataFrame(results, columns=['Cuenta', 'Fecha', 'Descripcion', 'URL', 'Foto'])

    df.index += 1

    html_table = df.to_html(escape=False,formatters=dict(URL=url_html_formatter, Foto=image_html_formatter)).replace('dataframe', 'table') # CLASS FOR THE BOOTSTRAP STYLESHEET

    html_template = '<!DOCTYPE html><head><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous"></head><body>' + str(html_table) + '</body></html>'

    html_file = open(file_name + '.html', 'w', encoding="utf-8")

    html_file.write(html_template)

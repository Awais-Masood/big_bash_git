# This project picked from upwork.
# Big Bash league players data scraped using Selenium and Requests mixed approach.
# This is post step implementation of teams_palyers.py. 
# This project scrapes Team Name, player name and Player Logo.
# This project is implemented in two steps: In first step required data scraped but when checked in excel, images
# size was varying. So second step was implemented in special_working_file.py (Consult that for detail.)
# Project description is available in this folder.
# Python version 3.9.1 is used to perform this exercise.
# Method to share scraped excel file with client as google sheet.
# i. Login it to developer's google drive.
# ii. Create a blank google sheet.
# iii. Use import option from file menu. It will import data along with images in google spread sheet.
# iv. Transfer ownership of the spreadsheet to the client.
# Note: Client may download this file and it will be downloaded correctly. Develper may delete this file. These all 
# steps are manual no API call is required programmatically. 
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import pandas as pd
import os
import shutil

datalist_players = []
############ Overwriting existing images directory #############
dir = 'images'
if os.path.exists (dir):
    shutil.rmtree (dir)
os.makedirs (dir)    
def export_to_excel ():
    global datalist_players
    with pd.ExcelWriter ('teams_players_var_1.xlsx', engine='xlsxwriter') as excel_writer:
        df = pd.DataFrame(datalist_players)
        df.to_excel(excel_writer, index=False)
        work_sheet = excel_writer.sheets["Sheet1"]
        work_sheet.set_default_row (115)
        work_sheet.set_column (1, 3, 30)
        images=os.listdir('images')
        for image in images:
            image_num = image.split('.')[0]
            row_num = 'D'+str(int (image_num)+1)
            print (row_num)
            work_sheet.insert_image (row_num, 'images/' + image_num + '.jpg', {'x_scale':0.5,'y_scale':0.5})
### Chrome Options ###
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging']) #Without it warning are thrown.
options.add_experimental_option("detach", True) # This enables browser to stay alive when run from command prompt.
options.add_argument('User-Agent=Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36')
#options.add_argument("--headless=new")
#######################
#### Find BIG BASH Teams ####
url = "https://www.cricket.com.au/big-bash?isCompleted=0"
driver = webdriver.Chrome(options=options)
driver.maximize_window()
driver.get(url)
page_source = driver.page_source
doc = BeautifulSoup(page_source, 'html.parser')
ul_ = doc.find ("ul", class_="o-dropdown__options-list")
li_ = ul_.find_all ("li")
big_bash_teams = []
for teams in li_:
    print (teams.text)
    big_bash_teams.append (teams.text)
#############################

url = "https://www.cricket.com.au/players"
#options = webdriver.ChromeOptions()
#options.add_experimental_option('excludeSwitches', ['enable-logging']) #Without it warning are thrown.
#options.add_experimental_option("detach", True) # This enables browser to stay alive when run from command prompt.
#options.add_argument("start-maximized")
#options.add_argument("disable-infobars")
#driver = webdriver.Chrome(options=options)
#driver.maximize_window()
driver.get(url)
els = driver.find_elements(By.CLASS_NAME, 'o-dropdown__trigger')
print (len (els))
print (driver.execute_script("return document.body.scrollHeight"))
driver.execute_script ("window.scrollTo(0,500)")
###### Initialize a browser to browse players profile to extract images url #######
driver_2 = webdriver.Chrome(options=options)
driver_2.maximize_window()
###################################################################################        
#driver.execute_script("arguments[0].scrollIntoView();", els[1])
sr = 0
for team in big_bash_teams[1:]: #[1:] To skip first value which is "All Teams"
    print ('Team Name ==>>', team)
    els[1].click ()
    sleep (2)
    els_textbox = driver.find_element(By.CLASS_NAME, 'o-dropdown__input')
    els_textbox.send_keys(team)
    sleep (2)
    els_team = driver.find_element(By.CLASS_NAME, "o-dropdown__item-trigger ")
    sleep (2)
    els_team.click ()
    sleep (20)
    page_source = driver.page_source
    doc = BeautifulSoup(page_source, 'html.parser')
    ## Find Logos ##
    div_ = doc.find_all ("div", class_="o-dropdown__options-item-icon")
    img_src = ""
    for item in div_:
        try:
            img = item.find ("img")
            src = img ["src"]
            team_name = img ['alt']
            print ('Team ==>>', team)
            print ('Team Name ==>>', team_name)    
            print ('------------------------')
            if team == team_name:
                img_src = src
                print ('image source ==>', src)
                break
        except:
            print ("No image attached with this link")
    ##################
    ## Find players ##
    li_ = doc.find_all ('li', class_="w-player-listing__players-item")
    print (len (li_))
    
    players_link = []
    for item in li_:
        print (item.text)
        print ('https://cricket.com.au' + item.find ("a")["href"])
        players_link.append ('https://cricket.com.au' + item.find ("a")["href"])
    for link in players_link:
        sr += 1
        print ('before next player')
        driver_2.get(link)
        print ('after next player')
        sleep (10)
        page_source = driver_2.page_source
        #-- Image
        #els_image = driver_2.find_element(By.CSS_SELECTOR, ".w-player-header__player-headshot.u-hide-tablet")
        # try:
        #     r = requests.get (link)
        # except:
        #     sleep (60)
        #     r = requests.get (link)
        doc = BeautifulSoup(page_source, 'html.parser')
        img_ = doc.find ("img", "w-player-header__player-headshot u-show-tablet")
        player_image_src = img_ ["src"]
        ul_ = doc.find ("ul", class_="w-player-bio__list")
        print (ul_)
        li_ = ul_.find("li")
        print (li_)
        print (li_.contents)
        print ("Full Name ==>>", li_.contents[2].strip ())
        player_name = (li_.contents[2].strip ())
        empty_str = ""
        dict_people = {
            'Sr': sr,
            'Team': team,
            'Full Name':player_name,
            'Picture': empty_str
            #,'Player Image Source': player_image_src,
            #'Logo Source':img_src
        }
        datalist_players.append(dict_people)
        with open ('images/' + str (sr) + '.jpg', 'wb') as f:  
            im = requests.get ('https:' + player_image_src)
            f.write (im.content)

export_to_excel()
#els_textbox.send_keys (big_bash_teams[1])
# headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
# r = requests.get (url)
# doc = BeautifulSoup(r.text, "html.parser")
# #ul_ = doc.find_all ("ul")
# #print (len (ul_))
# div_ = doc.find ("div", class_="flex-col-12")
# print (div_)

#------------------ Spool html to file ---------------------
#with open('teams_players.html', 'w', encoding='utf-8', newline='') as f:
#        f.write (div_.prettify ())
#-----------------------------------------------------------
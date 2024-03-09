# This special_working_file.py is continuation of teams_players_variation_1.py.
# This file has two segmemnts: SEGMENT-I converts all images into PNG and then resize PNG images.
# Segment two reads excel file created in teams_players_variation_1.py and using data in that file it creates
# teams_players_variation_final.xlsx and adds modified png images in that file. Hence project completes here.
# Completion date 06-JAN-2023.

import requests
from bs4 import BeautifulSoup
import os
import shutil
from os import walk
import pandas as pd
from PIL import Image, ImageChops

# Segment-I
############ Saving Images as PNG #############
# images = os.listdir ('images/original')
# for image in images:
#     image_name = image.split('.')[0]
#     im = Image.open ('images/original/' + image)
#     im.save ('images/png/' + image_name + '.png')
# images = os.listdir('images/png')
    ######## Re-sizing image #########
# for image in images:
#     image_name = image.split('.')[0]
#     im = Image.open('images/png/'+image)
#     im.thumbnail ((144, 144), Image.LANCZOS) # Scale down image
#     im.save ('images/png/' + image_name + '.png')
###############################################
# Segment - II
############## Update original excel file image column with images in png folder ##########
# with pd.ExcelWriter('teams_players_var_final.xlsx', engine='xlsxwriter') as excel_writer:
#     df = pd.read_excel ('teams_players_var_1.xlsx', usecols="A:C")
#     print (df)
#     df.insert (3, 'PICTURE', "")
#     print (df)
#     df.to_excel(excel_writer, index=False) #Create excel file teams_players_var_Final.
#     work_sheet = excel_writer.sheets["Sheet1"]
#     work_sheet.set_default_row (115)
#     work_sheet.set_column (1, 3, 30)
#     images=os.listdir('images/png') # This statement will assign all images in png directory to images list.
#     for image in images:
#         image_num = image.split('.')[0] # image.split('.') will convert 1.PNG into [1, PNG] while [0] will return first element i-e 1. 
#         row_num = 'D'+str(int (image_num)+1)
#         print (row_num)
#         work_sheet.insert_image (row_num, 'images/png/' + image_num + '.png')

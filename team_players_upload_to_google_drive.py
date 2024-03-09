# This project created with the perspective to provide BIG BASH scraped data and images to prospective client on a
# google sheet.
# Programmatic approach was used to upload scraped file with images to services account google drive and then
# transfer ownership of that file with client programmatically.
# Following failures faced in this project:
# i. Programmatically when, scraped data along with images, excel file uploaded, images lost.
# ii. Alternatively, file without images uploaded (successful), images folder tried to upload but it failed. So,
# individual images uploaded successfully. Successfully, images shared with public.
# Now it was tried to transfer ownership of the excel file, client has to accept ownership manually, but ownersip
# transfer was successful.
# Manually =Image formula checked in uploaded excel file (that automatically converted in google sheet via used code)
# and it displayed images correctly.
# Now images had to be transferred ownership to client as well, so that those can be combined with client excel file
# using =Image formula. But images could not be tranferred in one go via folder in which images reside. Only folder
# gets transferred but images stayed under ownership of services account. Now there was on option but to transfer 
# owner ship of each image and user has to accept those ownerships one by one. Images were around 750 and that 
# seemed a hactic task.
# At his point this approach left for the time being. Alternatively, scraped file along with images can be uploaded
# manually as google sheet and ownership can also be transferred manually. This file will be re-consulted when a
# similar project is faced again. 
   
from google.oauth2 import service_account
import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload
import io
from googleapiclient.http import HttpError
import json
import os
from time import sleep
def resource_id (service, resource_name, mime_type=None):
    print ('------------ Return Resource Id -------------')    
    #print (resource_name)    
    response = service.files().list().execute ()
    #print (json.dumps(response, indent=1))    
    for _file in response["files"]:
        if (mime_type):        
            if (_file["name"] == resource_name and _file["mimeType"] == mime_type):
                return _file["id"]
        else:
            if (_file["name"] == resource_name):
                return _file["id"]

def permissions_detail (fileid):
    print ('------- Permissions Detail --------')
    response = service.permissions().list(fileId=fileid).execute()
    print (json.dumps(response, indent=1))
    for permission in response ["permissions"]:
        permission_email = service.permissions().get(fileId=fileid, permissionId=permission["id"], fields="emailAddress").execute()
        print (permission ["role"], '==>> ', permission_email['emailAddress'])

def delete_from_drive (service, resource_id=None):
    print ('---------- Delete function call----------')
    if (resource_id):
        service.files().delete(fileId=resource_id).execute()
    else:
        response = service.files().list (pageSize=1000).execute()
        print (json.dumps(response, indent=1))
        for items in response ["files"]:
            try:
                print (items["name"], '-->' , items["id"])
                service.files().delete(fileId=items["id"]).execute()
            except Exception as ex:
                print ('error occurred')
                print (str (ex))
                permissions_detail (items["id"])
    drives_current_situation(service, 'Situation after Delete')
    sleep (10)
    drives_current_situation(service, 'Situation after Delete attempt 2')

def create_folder (service, folder_name, parent_folder_name=None):
    print ('---------- Create Folder--------------')
    mime_type = 'application/vnd.google-apps.folder'
    if (parent_folder_name):
        parent_folder_id = resource_id(service, parent_folder_name) 
        file_metadata = {
            'name': folder_name,
            'mimeType': mime_type,
            'parents': [parent_folder_id]
        }
    else:
        file_metadata = {
            'name': folder_name,
            'mimeType': mime_type
        }
    response = service.files().create(body=file_metadata).execute()
    #print (response)
    drives_current_situation(service, 'Situation after Create')
    #response = service.files().list().execute()
    #print (json.dumps(response, indent=1))

def upload_file (service, file_name, file_path, gdrive_folder_id, mime_type1, mime_type2):
    print ('--------------- File Update ---------------')
    print (file_path+file_name)
    print (mime_type1)
    print (mime_type2)
    file_metadata = {
        'name'      : file_name,
        'mimeType'  : mime_type1,
        'parents'   : [gdrive_folder_id]
    }
    media_content = MediaFileUpload (file_path+file_name, mimetype=mime_type2)
    response = service.files().create(
        body=file_metadata,
        media_body=media_content
        ).execute()
    #print (json.dumps (response, indent=1))
    drives_current_situation(service, 'Situation after Create')
    return response
def get_file_id (file_json, file_name):
    print ('------------ Get File Id --------------')
    #print (file_name)
    #print (file_json)
    for item in file_json:
        if (item["name"] == file_name):
            print (item["name"])
            return item["id"]

def drives_current_situation (service, MSG, parent_folder_id=None):
    if (parent_folder_id):
        query = "parents in '%s' " % parent_folder_id
        response = service.files().list(q=query).execute()
    else:
        response = service.files().list(fields="files(id, name, mimeType, permissions(id, type, role, emailAddress, pendingOwner))").execute()
    print ('------------- ' + MSG + ' ----------------')
    print (json.dumps(response, indent=1))    

def share_with (service, resource_id, perm_type, perm_role, perm_email=None):
    print ('------------ Share Public -------------')
    if (perm_email):
        new_permission = {
            'type':perm_type,
            'role':perm_role,
            'emailAddress':perm_email
        }
    else:
        new_permission = {
            'type': perm_type,
            'role': perm_role
        }
    response = service.permissions().create(fileId=resource_id, body=new_permission, transferOwnership=False).execute()

def get_permission_id (service, resource_id, perm_email, perm_role=None):
    print ('-------------- Get permission Id ----------------')
    if (perm_role):
        return
    else:
        response = service.files().get(fileId=resource_id, fields="id, name, mimeType, permissions(id,type,role,emailAddress)").execute()
        _permissions = response.get ("permissions")
        print (json.dumps (_permissions, indent=1))
        for item in _permissions:
            try:
                if (item ["emailAddress"] == perm_email):
                    return item ["id"] 
            except:
                pass

############################## Main Function ###############################
if __name__ == "__main__":
    ######### 1. Create a service object ##########
    scope = ['https://www.googleapis.com/auth/drive']
    credentials = service_account.Credentials.from_service_account_file(
        filename='sv_creds.json',
        scopes=scope
    )
    print (type(credentials))
    service = build ('drive', 'v3', credentials=credentials)
    #print (type(service))
    #response = service.files().list().execute()
    #print (response)

    ########## 2. Create Big Bash folder in Services Account ########
    #create_folder (service, 'BIG BASH')
    #create_folder (service, folder_name='Images', parent_folder_name='BIG BASH')
    #################################################################
    
    ####################### 3. Upload Images ########################
    images = os.listdir ('images/png')
    i = 0 
    for image in (images):
        i += 1
        file_name = image
        file_path = 'images/png/'
        mime_type1 = 'image/png'
        mime_type2 = 'image/png'
        #gdrive_folder_id = resource_id(service, 'Images')
        #response = upload_file(service, file_name, file_path, gdrive_folder_id, mime_type1, mime_type2)
        #print (response.get ("name"))
        #print (response.get ("id"))
        if i==2:
            break
    #parent_folder_id = resource_id(service, 'Images')
    #drives_current_situation(service, 'Situatio after image upload', parent_folder_id)
    
    # for image in (images):
    #     i += 1
    #     print (image)
    #     parent_folder_id = resource_id(service, 'Images')
    #     file_metadata = {
    #         'name'      : image,
    #         'parents'   : [parent_folder_id]
    #     }
    #     media_content = MediaFileUpload ('images/png/' + image, mimetype='image/png')
        # response = service.files().create(
        #     body=file_metadata,
        #     media_body=media_content
        #     ).execute()
        # print (response)
        # if i == 2:
        #     print ('going to break')
        #     break
    #, q="mimeType='application/vnd.google-apps.folder'"
    #parent_folder_id = resource_id(service, 'Images')
    #query = "parents in '%s' " % parent_folder_id
    #print (query)
    #response = service.files().list(pageSize=1000, fields="nextPageToken, files(id, name, mimeType)", q=query).execute()
    #print (json.dumps(response, indent=1))
    
    ####################### 3.1. Upload Excel #######################
    file_name = 'teams_players_var_final_for_gdrive.xlsx'
    file_path = ''
    mime_type1 = 'application/vnd.google-apps.spreadsheet'
    mime_type2 = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    #gdrive_folder_id = resource_id(service, 'BIG BASH')
    #upload_file(service, file_name, file_path, gdrive_folder_id, mime_type1, mime_type2)
    #parent_folder_id = resource_id(service, 'BIG BASH')
    #query = "parents in '%s' " % parent_folder_id
    #print (query)
    #response = service.files().list(pageSize=1000, fields="nextPageToken, files(id, name, mimeType)", q=query).execute()
    #print (json.dumps(response, indent=1))
    ####
    #response = service.files().list().execute()
    #print ('------------- Situation After Excel File Upload ----------------')
    #print (json.dumps(response, indent=1))
    #####
    #print (response.get ("files"))
    #file_json = response.get ("files")
    #file_id = get_file_id (file_json, "BIG BASH")
    #print (file_id)
    #####################################################################

    ######################## Share ######################################
    #resource_id = resource_id (service, '10.png')
    #print (resource_id)
    #resource_id = resource_id (service, 'Images')
    #share_with (service, resource_id, 'anyone', 'reader')
    #response = service.permissions().list(fileId=resource_id).execute()
    #print (json.dumps (response, indent=1))
    
    #share_with (service, resource_id, 'user', 'reader', 'awais105@gmail.com')
    #response = service.permissions().list(fileId=resource_id).execute()
    #print (json.dumps (response, indent=1))
    #resource_id = resource_id (service, 'Images')
    #response = service.files().get(fileId=resource_id, fields="id, name, mimeType, permissions(id,type,role,emailAddress)").execute()    
    #print (json.dumps(response, indent=1))
    
    
    #### Create permission ####
    #resource_id = resource_id (service, 'BIG BASH')
    new_permission = {
        'type':'user',
        'role':'writer',
        'pendingOwner':'true',
        'emailAddress':'awais105@gmail.com'
    }
    #response = service.permissions().create(fileId=resource_id, body=new_permission).execute()
    #print (json.dumps(response, indent=1))
    ###############################
    
    #### Update permission ####
    #resource_id = resource_id (service, 'BIG BASH')
    #print (resource_id)
    #_permission_id = get_permission_id (service, resource_id, 'awais105@gmail.com')
    #print (_permission_id)
    new_permission = {
        'role':'writer',
        'pendingOwner':'true'
    }
    #response = service.permissions().update(fileId=resource_id, permissionId=_permission_id, body=new_permission).execute()
    #print (json.dumps(response, indent=1))
    ################
    ###### Delete Permission ########
    # resource_id = resource_id (service, 'BIG BASH')
    # print (resource_id)
    # _permission_id = get_permission_id (service, resource_id, 'Awais105@gmail.com')
    # print (_permission_id)
    # service.permissions().delete(fileId=resource_id, permissionId=_permission_id).execute()
    ####################### Permissions #################################
    # response = service.files().list().execute()
    # file_json = response.get ("files")
    # file_id = get_file_id(file_json=file_json, file_name='BIG BASH')
    new_permission = {
        'type':'user',
        'role':'reader',
        'emailAddress':'awais105@gmail.com'
    }
    #response = service.permissions().create(fileId=file_id, body=new_permission, transferOwnership=False).execute()
    #print (response)
    ######################################################################
    
    ############################ Delete ##################################
    #teams_players_var_final_for_gdrive
    resource_id = resource_id(service, '1.png')
    delete_from_drive(service, resource_id)
    #response = service.files().list().execute()
    #print (json.dumps(response, indent=1))
    ######################################################################
    #parent_folder_id = resource_id (service, 'Images')
    #drives_current_situation(service, 'Images Folder Situation', parent_folder_id)
    sleep (3)
    drives_current_situation(service, 'Current Situation')
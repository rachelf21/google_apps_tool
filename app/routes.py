from flask import render_template, request, Response
from app import app

import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from tabulate import tabulate

#delete pickle file if modifying scope
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/photoslibrary.readonly']

#%%
def get_gdrive_service():
    credentials = None
    
    # if os.path.exists('token.pickle'):
    #     print("Loading credentials from file...")
    #     with open('token.pickle', 'rb') as token:
    #         credentials = pickle.load(token)
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("Refreshing access token..")
            credentials.refresh(Request())
        else:
            print("Fetching new token..")
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
    
            flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
            credentials = flow.credentials
            
            # with open('token.pickle', 'wb') as f:
            #     print("Saving credentials for future use...")
            #     pickle.dump(credentials, f)
        
    #print(credentials.to_json())
    
    return build('drive', 'v3', credentials=credentials)
    #return build('photos', 'v3', credentials=credentials)

#%%
def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"

#%% not used
def list_files(items):
    """given items returned by Google Drive API, prints them in a tabular way"""
    if not items:
        # empty drive
        print('No files found.')
    else:
        rows = []
        for item in items:
            # get the File ID
            # get the name of file
            name = item["name"]
            try:
                # get the size in nice bytes format (KB, MB, etc.)
                size = get_size_format(int(item["size"]))
            except:
                # not a file, may be a folder
                size = "N/A"
            # get the Google Drive type of file
            mime_type = item["mimeType"]
            # get last modified date time
            modified_time = item["modifiedTime"]
            # append everything to the list
            rows.append((name, size, mime_type, modified_time))
        print("Files:")
        # convert to a human readable table
        table = tabulate(rows, headers=["Name", "Size", "Type", "Modified Time"])
        # print the table
        print(table)

#%%
def search(service, query):
    results = []
    page_token=None
    while True:
        response = service.files().list(q=query, spaces="drive", fields="nextPageToken, files(parents, name, mimeType, size, modifiedTime, modifiedByMe, trashed, modifiedByMeTime, webViewLink)", pageToken=page_token).execute()
        #response = service.files().list(q=query, spaces="drive", fields='*', pageToken=page_token).execute()
        for file in response['files']:
            results.append((file))
        page_token = response.get('nextPageToken', None)
        if not page_token:
            break
    print(results)
    return results
    
#%%
def main():
    service = get_gdrive_service()
    
    #print list of files, first 5 pages:
    # results =[]
    # page_token=None
    # i=0
    # while i<5:
    #     try:
    #         param = {}
    #         if page_token:
    #             param['pageToken'] = page_token
    #         x = service.files().list(fields='nextPageToken, files(name, mimeType, size, modifiedTime)', pageToken=page_token).execute()
    #         for f in x['files']:
    #             print(f.get('name'))
    #             results.append(f.get('name'))

    #         page_token = x.get('nextPageToken')
    #         #print(page_token)
    #         i=i+1
    #         if not page_token:
    #             break
    #     except:
    #         print('error')
    #         break
    #             #results = service.files().list(pageSize=30, fields='nextPageToken, files(name, mimeType, size, modifiedTime)').execute()
    
    # #print(results['nextPageToken'])
    # for r in results:
    #     print(r)
    # #items = results.get('files',[])
    # #list_files(items)

    #search for files
    filetype = "application/vnd.google-apps.folder"

    
    #search_result = search(service, query= "'rfriedman@mdyschool.org' in owners" and "modifiedTime > '2020-09-01T12:00:00.000Z'")
    
    search_result = search(service, query=  "modifiedTime > '2020-01-01T12:00:00.000Z'")
    print(search_result)
    print(len(search_result))
   
    service.close()
    
#%%    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_drive_files')
def search_drive_files():
    service = get_gdrive_service()
    
    filetype = "application/vnd.google-apps.folder"
    query =  ("modifiedTime > '2020-09-01T12:00:00.000Z' and trashed = false and 'rfriedman113@gmail.com' in owners" )
    try:
        search_result = search(service, query=query)
        print(search_result)
        print(len(search_result))
      
        service.close()
    
        return render_template('search_files.html', results=search_result)
    except:
        return "Error retrieving files"

@app.route('/list_drive_files')
def list_drive_files():
    service = get_gdrive_service()
    
    #print list of files, first 5 pages:
    results =[]
    page_token=None
    i=0
    while i<5:
        try:
            param = {}
            if page_token:
                param['pageToken'] = page_token
            x = service.files().list(fields='nextPageToken, files(name, mimeType, size, modifiedByMeTime, webViewLink)', pageToken=page_token).execute()
            #x = service.files().list(**param).execute()
            for f in x['files']:
                #print(f.get('name'))
                #results.append(f.get('name'))
                results.append(f)

            page_token = x.get('nextPageToken')
            #print(page_token)
            i=i+1
            if not page_token:
                break
        except:
            print('error')
            break
                #results = service.files().list(pageSize=30, fields='nextPageToken, files(name, mimeType, size, modifiedTime)').execute()
    
    #print(results['nextPageToken'])
    for r in results:
        print(r)
    #items = results.get('files',[])
    #list_files(items)
    service.close()
    return render_template('list_files.html', results = results)

#%%    
if __name__ == '__main__':
    main()
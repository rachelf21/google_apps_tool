import io
import os

import logging 

from flask import render_template, request, Response, redirect, flash, url_for
from app import app
import sys
import pickle

import httplib2

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from tabulate import tabulate
from datetime import datetime, timedelta

logging.basicConfig(level=logging.DEBUG, filename='mylog.log',filemode="w", format="%(asctime)-15s %(levelname)-8s %(message)s")
logging.info('this should to write to the log file')

from app.forms import SelectDateForm

#delete pickle file if modifying scope
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/photoslibrary.readonly']

#%%
def get_gdrive_service():
    credentials = None
    
    if os.path.exists('token.pickle'):
        print("Loading credentials from file...")
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("Refreshing access token..")
            credentials.refresh(Request())
        else:
            print("Fetching new token..")
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
    
            flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
            credentials = flow.credentials   
            
            with open('token.pickle', 'wb') as f:
                print("Saving credentials for future use...")
                pickle.dump(credentials, f)
                
    return build('drive', 'v3', credentials=credentials)
    #return build('photoslibrary', 'v1', credentials=credentials)


'''
            authorization_url, state = flow.authorization_url(
    # Enable offline access so that you can refresh an access token without
    # re-prompting the user for permission. Recommended for web server apps.    access_type='offline',
    prompt='consent',
    # Enable incremental authorization. Recommended as a best practice.
    include_granted_scopes='true')

            flow.redirect_uri = 'https://google-apps-tools.herokuapp.com/'
            '''
            #print(credentials.to_json())
    
    #return redirect(authorization_url)

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
        response = service.files().list(q=query, spaces="drive", fields="nextPageToken, files(parents, id, name, mimeType, size, modifiedTime, modifiedByMe, trashed,  modifiedByMeTime, webViewLink)", pageToken=page_token).execute()
        #response = service.files().list(q=query, spaces="drive", fields='*', pageToken=page_token).execute()
        for file in response['files']:
            results.append((file))
        page_token = response.get('nextPageToken', None)
        if not page_token:
            break
    #this is really slowing down the code. not sure why. in the meantime, comment it out.    
    # for r in results:
    #     parent = r['parents'][0]
    #     #query = "fileId = '" + parent +"'"
    #     #folder = service.files().list(q=query, spaces="drive", fields="files(name,webViewLink").execute()
    #     folder = service.files().get(fileId=parent).execute()
    #     r['containing_folder'] = folder['name']
    #     #r['containing_folder_link'] = folder['webViewLink']

    #print(results)
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
     
@app.route('/download_file/<file_id>/<file_name>/<mime_type>')
def download_file(file_id, file_name, mime_type):
    ext = ''
    
    service = get_gdrive_service()

    #mime_type = mime_type.replace('%2F', '/')
    mime_type_orig = mime_type
    mime_type = mime_type.replace('12345', '/')
    if 'presentation' in mime_type:
        mime_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ext = ".pptx"
        request = service.files().export(fileId=file_id,mimeType=mime_type)
    elif 'spreadsheet' in mime_type:
        mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ext = ".xlsx"
        request = service.files().export(fileId=file_id,mimeType=mime_type)

    elif 'document' in mime_type:
        mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ext = ".docx"
        request = service.files().export(fileId=file_id,mimeType=mime_type)

    elif 'drawing' in mime_type:
        mime_type = 'image/png'
        ext = ".png"
        request = service.files().export(fileId=file_id,mimeType=mime_type)
        #what's the dif between export and export_media 
    
    else:
        #for binary files:
            
        request = service.files().get_media(fileId=file_id)
        #for photo from photo album
        #request = service.mediaItems().get(file_id)
        
    #how to download folder, site, form

    try:
    
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
        fh.seek(0)
        path = './backups'
    
        with open(os.path.join(path, file_name+ext), 'wb') as f:
            f.write(fh.read())
            f.close()
        
        flash('Successfully downloaded ' + file_name+ext, 'success')
        return redirect(url_for('search_drive_files'))
            
    except Exception as e:
        message = "Check the file format and file size. Google folders, sites, and forms cannot be downloaded. In addition, file size cannot exceed 10 MB."
        flash(message, 'danger')
        return redirect(url_for('search_drive_files'))


@app.route('/copy_file/<file_id>/<file_name>')
def copy_file(file_id, file_name):
    service = get_gdrive_service()
    
    todays_date = datetime.today()
    todays_date = datetime.strftime(todays_date, '%m%d%Y')
    folder_name = "Copies"+todays_date
    
    query = "name = '" + folder_name +"'"
    
    folder_exists = search(service, query)
    
    x = len(folder_exists)
    
    if x==0:
        file_metadata = {
            'name': folder_name,
            'description': 'This folder was copied with the use of the Google Tools App.',
            'mimeType': 'application/vnd.google-apps.folder'
        }
            
        folder = service.files().create(body=file_metadata).execute()
        parent = folder['id']
    else:
        parent = folder_exists[0]['id']
    
    file_metadata = {
        'name': file_name,
        'parents': [parent],
        'description': 'This file was copied with the use of the Google Tools App.'
    }
    
    service.files().copy(fileId=file_id, body=file_metadata).execute()

    #change the output - go back to search files page, flash success/warning message 
    return "Your file " + file_name + " has been copied successfully."

@app.route('/search_drive_files')
def search_drive_files():
    service = get_gdrive_service()
    
    lastyear = datetime.today() - timedelta(days=183)
    datestring = datetime.strftime(lastyear, "%Y-%m-%d")
    
    query =  ("modifiedTime > '" + datestring + "T12:00:00.000Z' and trashed = false and 'me' in owners" )
    try:
        search_result = search(service, query=query)
        #print(search_result)
        print(len(search_result))
      
        service.close()
    
        return render_template('search_files.html', results=search_result)
    except Exception as e:
        print(e)
        return "Error retrieving files" 

@app.route('/search_files/<mime_type>/<date1>/<date2>')
def search_files(mime_type, date1, date2):
    
    service = get_gdrive_service()
    query = ''
    mime_type_orig = mime_type
    
    if 'slide' in mime_type:
        mime_type = 'application/vnd.google-apps.presentation'
    elif 'spreadsheet' in mime_type:
        mime_type = 'application/vnd.google-apps.spreadsheet'
    elif 'document' in mime_type:
        mime_type = 'application/vnd.google-apps.document'
    elif 'drawing' in mime_type:
        mime_type = 'application/vnd.google-apps.drawing'
    elif 'form' in mime_type:
        mime_type = 'application/vnd.google-apps.form'  #find export format
    elif 'map' in mime_type:
        mime_type = 'application/vnd.google-apps.map'  #find export format       
    elif 'script' in mime_type:
        mime_type = 'application/vnd.google-apps.script'  #find export format     
    elif 'site' in mime_type:
        mime_type = 'application/vnd.google-apps.site'  #find export format 
    elif 'folder' in mime_type:
        mime_type = 'application/vnd.google-apps.folder'
    elif 'pdf' in mime_type:
        mime_type = 'application/pdf'
    elif 'other' in mime_type:
        mime_types = ['text/html','application/zip','text/plain','application/vnd.openxmlformats-officedocument.wordprocessingml.document','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','text/csv','image/jpeg','image/png','application/vnd.openxmlformats-officedocument.presentationml.presentation','application/octet-stream','text/x-python']
        subquery='('
        for m in mime_types:
            subquery = subquery + "mimeType='"+m+"' or"
        subquery = subquery[0:-2]+')'
    
    if mime_type == 'other':
        query =  ("modifiedTime >= '" + str(date1)+ "T12:00:00.000Z' and modifiedTime <= '" + str(date2)+ "T12:00:00.000Z' and trashed = false and 'me' in owners and " + subquery )
    else:
        query =  ("modifiedTime >= '" + str(date1)+ "T12:00:00.000Z' and modifiedTime <= '" + str(date2)+ "T12:00:00.000Z' and trashed = false and 'me' in owners and mimeType = '"+mime_type+"'" )
            
            
    try:
        search_result = search(service, query=query)
        #print(search_result)
        count = len(search_result)
      
        service.close()
        
        category = mime_type_orig.capitalize()
        if count == 0 or count>1:
            category = category+"s"
    
        logging.info(category)
        return render_template('search_files.html', results=search_result, category=category)
    except Exception as e:
        logging.info(e)
        return "Error retrieving files" 
    
@app.route('/display_form/<mimeType>', methods=['GET', 'POST'])
def display_form(mimeType):
    form = SelectDateForm()
    
    if request.method=='GET':
        halfyear = datetime.today() - timedelta(days=183)
        form.date_start.data = halfyear
        form.date_end.data = datetime.today()
        return render_template('form.html', form=form, mimeType=mimeType.capitalize()+'s')
    
    elif request.method=='POST':
        date_start = form.date_start.data
        date_end = form.date_end.data
        search_files(mimeType,date_start,date_end)
        return redirect(url_for("search_files", mime_type=mimeType, date1=date_start, date2=date_end))
            
    flash("Invalid entry", 'danger')
    return render_template('form.html', form=form, mimeType=mimeType.capitalize()+'s')
        
        
            
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
            x = service.files().list(fields='nextPageToken, files(name, mimeType, size, modifiedByMeTime, parents, webViewLink)', pageToken=page_token).execute()
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
import os
import pandas as pd
import logging 
import requests
from datetime import datetime

from flask import render_template, url_for, request, redirect, Blueprint, Response,flash
from PIL import Image
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

photos = Blueprint('photos', __name__)

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/photoslibrary.readonly']

logging.basicConfig(level=logging.DEBUG, filename='mylog.log',filemode="w", format="%(asctime)-15s %(levelname)-8s %(message)s")
logging.info('this should to write to the log file')

from app.forms import SelectDateForm

dest_folder = r'C:\Users\Rachel\OneDrive\Brooklyn College\5-Bklyn College Fall 2020\Google Tools\backups'

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
                
    return build('photoslibrary', 'v1', credentials=credentials)
    
    
#%%    
def display_thumbnail(base_url, width, height):    
    base_url = base_url+"=w"+str(width)+"-h"+str(height) 
    im = Image.open(requests.get(base_url, stream=True).raw)
    return im

@photos.route('/list_photos')
def list_photos():
    service = get_gdrive_service()
    
    results =[]
    page_token=None
    count=0
    while count<=200:
        try:
            param = {}
            if page_token:
                param['pageToken'] = page_token
                
            photos = service.mediaItems().list(**param).execute()
            
            media_files = photos['mediaItems']
            
            for m in media_files:
                #print(f.get('name'))
                #results.append(f.get('name'))
                #logging.info(m['baseUrl'])
                results.append(m)
    
    # for r in photos['mediaItems']:
    #    results.append([r['filename'], r['mediaMetadata']['creationTime'], r['productUrl'],  r['mimeType'],r['baseUrl'],])
            count = len(results)
            logging.info("count of media_files="+str(count))
            #logging.info("results:" + str(media_files))
            page_token = photos['nextPageToken']
            logging.info("page token: " + page_token)
            if not page_token:
                break
            
        except Exception as e:
            logging.info(e)
            break
            
    return render_template('photos.html' , media_files = results)

@photos.route('/search_photos/<date1>/<date2>')
def search_photos(date1,date2):
    service = get_gdrive_service()
    results =[]

    month1, day1, year1 = date1[5:7], date1[8:10], date1[0:4]  # Day or month may be 0 => full month resp. year
    month2, day2, year2 = date2[5:7], date2[8:10], date2[0:4]  # Day or month may be 0 => full month resp. year
    date_filter = [{"day": day1, "month": month1, "year": year1}]  # No leading zeroes for day and month!
    nextpagetoken = 'Dummy'
    
    while nextpagetoken != '':
        nextpagetoken = '' if nextpagetoken == 'Dummy' else nextpagetoken
        photos = service.mediaItems().search(
            body={"filters":  
                  {"dateFilter": 
                   {"ranges": [
                       {
                           "startDate": {"day": day1, "month": month1, "year": year1},
                           "endDate": {"day": day2, "month": month2, "year": year2}
                        } 
                       ]
                   } },"pageSize": 100, "pageToken": nextpagetoken}).execute()
        
        logging.info(photos)
        items = photos.get('mediaItems', [])
        nextpagetoken = photos.get('nextPageToken', '')
        
        for item in items:
            logging.info(item['baseUrl'])
            results.append(item)
            

    return render_template('photos.html' , media_files = results)

#%%
@photos.route('/display_form_photos', methods=['GET', 'POST'])
def display_form_photos():
    form = SelectDateForm()
    
    if request.method=='GET':
        form.date_start.data = datetime(2020, 9, 1).date()
        form.date_end.data = datetime.today()
        return render_template('form.html', form=form, mimeType='Photos')
    
    elif request.method=='POST':
        date_start = form.date_start.data
        date_end = form.date_end.data
        search_photos(date_start.strftime("%Y-%m-%d"), date_end.strftime("%Y-%m-%d"))
        return redirect(url_for("photos.search_photos", date1=date_start, date2=date_end))
            
    flash("Invalid entry", 'danger')
    return render_template('form.html', form=form, mimeType='Photos')


#%%
@photos.route('/download_photo/<base_url>/<file_name>')
def download_photo(base_url, file_name):
    base_url = base_url.replace('12345', '/')
    response = requests.get(base_url+"=d")
    if response.status_code==200:
        #logging.info("Downloading photo {0}".format(file_name))
        with open(os.path.join(dest_folder, file_name), 'wb') as f:
            f.write(response.content)
            f.close()
    return "You have successfully downloaded this photo " + file_name            
            
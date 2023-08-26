#%% import libraries
import os, shutil
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from bing_image_downloader import downloader

#%% pull holidays from national holiday website
resp = requests.get('https://nationaltoday.com/what-is-today/') # get request against url
html = resp.text # pull html from response

soup = BeautifulSoup(html, 'html.parser') # parse html with bs4

holidays= [] 

for element in soup.body.find_all('h3', class_= 'holiday-title'): # create list of holidays from tagged elements
    holidays.append(element.string)

#%% convert to df for adding further dims
holidays_df = pd.DataFrame(holidays, columns= ['holiday_name'])

holidays_df['search_term'] = holidays_df['holiday_name'].str.replace('National Day of ', '').str.replace('National ', '').str.replace('Day of ', '').str.replace(' Day', '').str.replace(' Birthday', '').str.replace('’s', '')

holidays_df['is_birthday'] = holidays_df['holiday_name'].str.contains('Birthday') # is it a birthday?

print(holidays_df)

#%% remove existing images/dir from prior runs
dir = 'images'

for files in os.listdir(dir):
    path = os.path.join(dir, files)
    try:
        shutil.rmtree(path)
    except OSError:
        os.remove(path)

#%% pull top images for search result
for holiday, search in holidays_df[['holiday_name', 'search_term']].values:
    # print(holiday, ', ', search)
    holiday_dir = 'images/{}'.format(holiday.lower().replace(' ', '_').encode('ascii', 'ignore').decode())
    os.mkdir(holiday_dir)
    
    downloader.download(search, limit= 5, output_dir= holiday_dir, adult_filter_off= True, force_replace= False, timeout= 60, verbose= True)

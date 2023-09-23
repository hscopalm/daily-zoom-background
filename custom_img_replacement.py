#%% import libraries
import os, shutil
import yaml
import numpy as np
import pandas as pd
import datetime as dt

#%% set baseline vars from system, or config if unable
with open("config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

zoom_custom_path = config['zoom_custom_path']
birthdays = config['birthdays']
auto_select = config['auto_select']

abs_path = os.getcwd()

#%% define func
def replace_img():
    
    #%% find latest modified custom background
    dir = 'VirtualBkgnd_Custom'
    bg_path = os.path.join(zoom_custom_path, dir)

    bg_images = {}

    for files in os.listdir(bg_path):
        file_path =  os.path.join(bg_path, files)

        bg_images[file_path] = dt.datetime.fromtimestamp(os.path.getmtime(file_path))
        
    #%% sort dict, pull latest image
    sorted_bg_images = list(dict(sorted(bg_images.items(), key= lambda item: item[1], reverse= True)).keys())

    img_pair = {}
    
    # full res image is modified first, thumbnail second
    img_pair['thumbnail'] = sorted_bg_images[0]
    img_pair['background'] = sorted_bg_images[1]
    
    return img_pair

#%% run if executed separately
if __name__ == "__main__":
    img_pair = replace_img()
    print(img_pair)
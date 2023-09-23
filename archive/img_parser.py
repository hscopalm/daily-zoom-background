#%% import libraries
import os, shutil
import yaml
import itertools
import numpy as np
import pandas as pd
import cv2

#%% define func for img comparison
def mse(img1, img2):
   h, w = img1.shape
   diff = cv2.absdiff(img1, img2) # not really mse, whatever
   err = np.sum(diff**2)
   mse = err / (float(h * w))
   
   return mse

#%% define script func
def parse_img():
    #%% set baseline vars from system, or config if unable
    with open("config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    zoom_custom_path = config['zoom_custom_path']
    birthdays = config['birthdays']
    auto_select = config['auto_select']

    abs_path = os.getcwd()

    #%% backup peoples defaults just in case
    dir = 'VirtualBkgnd_Default'
    bg_path = os.path.join(zoom_custom_path, dir)

    try:
        shutil.copytree(bg_path, os.path.join(zoom_custom_path, 'VirtualBkgnd_Default_Bkup'))
    except OSError as error:
        print(error)   

    #%% iterate over files to compare
    bg_images = {}

    for files in os.listdir(bg_path):
        file_path =  os.path.join(bg_path, files)
        
        head, tail = os.path.splitext(file_path)
        
        if not tail:
            shutil.copy(file_path, file_path + '.jpg')
            
            img = cv2.imread(file_path + '.jpg')
            img = cv2.resize(img, (72, 72), interpolation = cv2.INTER_AREA)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
            os.remove(file_path + '.jpg')
            bg_images[file_path] = img
            
    #%% get all permutations of pairs of images and compute amse
    img_perms = list(itertools.permutations(bg_images, r= 2))

    img_diff_df = pd.DataFrame(columns= ['base', 'comp', 'diff'])
    img_diff_df.set_index(['base', 'comp'], inplace= True)

    for img1, img2 in img_perms:
        img_diff_df.loc[(img1, img2), 'diff'] = mse(bg_images[img1], bg_images[img2])

    img_diff_df['diff'] = pd.to_numeric(img_diff_df['diff'])
    img_diff_df.reset_index(inplace= True)

    # get comp key with minimum diff in the base group
    img_set = img_diff_df.loc[img_diff_df.groupby('base')['diff'].idxmin()][['base', 'comp']].rename({'base':'thumbnail', 'comp': 'background'}, axis= 1)
    img_pairs = pd.DataFrame(np.sort(img_set, axis= 1), columns= img_set.columns).drop_duplicates().reset_index(drop= True)

    return img_pairs
#%% run if executed separately
if __name__ == "__main__":
    img_pairs = parse_img()
    print(img_pairs)
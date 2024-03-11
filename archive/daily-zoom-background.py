# %% import libraries
import os, shutil, platform
import yaml
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from bing_image_downloader import downloader

# custom scripts
from archive.custom_img_replacement import replace_img

# %% set baseline vars from system, or config if unable
with open("config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# if custom path supplied
if config["zoom_custom_path"] != None:
    zoom_path = config["zoom_custom_path"]
# if windows
elif platform.system() == "Windows":
    zoom_path = config["zoom_win_path"].format(user=os.getlogin())
# if mac
elif platform.system() == "Darwin":
    zoom_path = config["zoom_mac_path"].format(user=os.getlogin())
# if not win/mac
else:
    raise ValueError("Non supported OS detected")

birthdays = config["birthdays"]
auto_select = config["auto_select"]

abs_path = os.getcwd()

# %% pull holidays from national holiday website
resp = requests.get("https://nationaltoday.com/today/")  # get request against url
html = resp.text  # pull html from response

soup = BeautifulSoup(html, "html.parser")  # parse html with bs4

holidays = []

for element in soup.body.find_all(
    "h3", class_="holiday-title"
):  # create list of holidays from tagged elements
    holidays.append(element.string)

# %% convert to df for adding further dims
holidays_df = pd.DataFrame(holidays, columns=["holiday_name"])

holidays_df["search_term"] = (
    holidays_df["holiday_name"]
    .str.replace("National Day of ", "")
    .str.replace("National ", "")
    .str.replace("Day of ", "")
    .str.replace(" Day", "")
    .str.replace(" Birthday", "")
    .str.replace("’s", "")
)

holidays_df["is_birthday"] = holidays_df["holiday_name"].str.contains(
    "Birthday"
)  # is it a birthday?

# remove birthdays if we turned off in the config.yaml
holidays_df = holidays_df.loc[~holidays_df["is_birthday"] | birthdays]

# %% remove existing images/dir from prior runs
dir = "images"

try:
    os.mkdir(dir)
except OSError as error:
    print(error)

for files in os.listdir(dir):
    path = os.path.join(dir, files)
    try:
        shutil.rmtree(path)
    except OSError:
        os.remove(path)

# %% which holiday(s) does the user want?
print(holidays_df["holiday_name"])
user_holiday_raw = input(
    "What is the index # of the holiday you want to celebrate?\nProvide a comma separated list if you want to see options for multiple...\n"
)
user_holiday_int = list(map(int, user_holiday_raw.replace(" ", "").split(",")))
user_holiday = [x for x in user_holiday_int if x <= len(holidays_df) - 1]

# %% pull top images for search result
for holiday, search in holidays_df.iloc[user_holiday][
    ["holiday_name", "search_term"]
].values:

    downloader.download(
        search,
        output_dir=dir,
        limit=5,
        adult_filter_off=True,
        force_replace=False,
        timeout=60,
        verbose=True,
    )

# %% choose final selection
if len(user_holiday) > 1:
    print(holidays_df.iloc[user_holiday]["holiday_name"])
    user_final_holiday = holidays_df.iloc[
        int(input("What is the index # of your final holiday choice?\n"))
    ]

else:
    user_final_holiday = holidays_df.iloc[user_holiday[0]]

user_final_img = int(input("What is your image choice from the options presented?\n"))

# find the right file extension
ext_list = (
    []
)  # there is an easier way to do this, I am up late and just want something to work quickly

for file in os.listdir(os.path.join(dir, user_final_holiday["search_term"])):
    ext_list.append(os.path.splitext(file))

# which image did you want again?
user_final_img_name = "Image_{img_num}{file_ext}".format(
    img_num=user_final_img, file_ext=ext_list[user_final_img - 1][1]
)

# %% take over images in the "VirtualBkgnd_Default" folder
img_pair = replace_img(zoom_path)

# %% set image as background
src_dir = "src_images"
img_dir = os.path.join("images", user_final_holiday["search_term"])

# just replacing both with the same image, no perfect method for determining thumb vs back
# src_thumb_path = os.path.join(src_dir, 'custom_bg.png')
src_thumb_path = os.path.join(img_dir, user_final_img_name)
tgt_thumb_path = img_pair["thumbnail"]

src_bg_path = os.path.join(img_dir, user_final_img_name)
tgt_bg_path = img_pair["background"]

# %% copy chosen image over provided background (and thumbnail for now)
shutil.copy(src_thumb_path, tgt_thumb_path)
shutil.copy(src_bg_path, tgt_bg_path)

import os, platform, shutil
from urllib import request
import json
import datetime as dt


def read_config(filename):
    """
    Read the config file to get the API key and any other configurations set
    Written without non-standard python libraries to ensure it will work as long as python is installed
    """

    config = {}
    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):  # Ignore empty lines and comments
                key, value = line.split("=")
                config[key.strip()] = value.strip()
    return config


print("Reading the config file...")
print("-" * 50)
config = read_config("config.txt")

# set the API key
if config["api_key"] != "":
    api_key = config["api_key"]
    print("API key found in config file")
else:
    raise ValueError("API key not found in config file")

include_birthdays = bool(config["birthdays"] == "True")
print("Include birthdays: ", include_birthdays)
auto_select = bool(config["auto_select"] == "True")
print("Auto select: ", auto_select)

# if custom path supplied
if config["zoom_custom_path"] != "":
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

dir = "VirtualBkgnd_Custom"
bg_path = os.path.join(zoom_path, dir)

print("Zoom path: ", zoom_path)
print("\n")
print("-" * 50)

# these are the headers that we need to send with the request and they are constant
header = {"x-api-key": api_key, "User-Agent": "Mozilla/5.0"}

# constans for the API endpoints
root = "https://z2w55sggr4.execute-api.us-east-1.amazonaws.com"
stage = "v1"

# first, we need to get the available holidays from the API for today
holidays_endpoint = "{root}/{stage}/holidays".format(root=root, stage=stage)
holidays_req = request.Request(
    holidays_endpoint,
    headers=header,
    method="POST",
)

# take the response from the API and print the holidays with their index
with request.urlopen(holidays_req) as resp:
    holidays = dict(
        zip(range(0, 1000), resp.read().decode("utf-8").replace('"', "").split("\\n"))
    )

# filter out the birthdays if the user doesn't want them
if not include_birthdays:
    holidays_filt = {
        index: holiday
        for index, holiday in holidays.items()
        if "Birthday" not in holiday
    }
else:
    holidays_filt = holidays

print("Available holidays for the provided date: ")
for index in holidays_filt:
    print("[{index}] {holiday}".format(index=index, holiday=holidays[index]))
print("\n")

# next, we need to get the user's choice of holiday
print("-" * 50)
choice_idx = input("Please enter the number corresponding to your choice of holiday: ")
print("\n")

choice_name = holidays[int(choice_idx)]

print("-" * 50)
print("You chose: ", choice_name)
print("\n")

# now we need to get the image for the chosen holiday
print("-" * 50)
print("Getting the image for the chosen holiday...")

# we need to send the choice to the API to get the image
data = str(json.dumps({"holiday_name": choice_name})).encode("utf-8")

img_endpoint = "{root}/{stage}/images".format(root=root, stage=stage)
img_req = request.Request(
    img_endpoint,
    headers=header,
    method="POST",
    data=data,
)

# take the response from the API and download the image
with request.urlopen(img_req) as resp:
    img_url = resp.read().decode("utf-8").replace('"', "")

print("Downloading the image at: " + img_url)

# download the image
img_download_req = request.Request(
    img_url,
    headers=header,
)

# take the response from the API and download the image
os.makedirs("img", exist_ok=True)  # create the directory if it doesn't exist

with request.urlopen(img_download_req) as resp:

    with open("img/background.jpg", "wb") as f:
        f.write(resp.read())

print("Image downloaded successfully!")
print("\n")

print("-" * 50)
print("Setting the image as your Zoom background...")

# find latest modified custom background
bg_images = {}

for files in os.listdir(bg_path):
    file_path = os.path.join(bg_path, files)

    bg_images[file_path] = dt.datetime.fromtimestamp(os.path.getmtime(file_path))

# sort dict, pull latest image
sorted_bg_images = list(
    dict(sorted(bg_images.items(), key=lambda item: item[1], reverse=True)).keys()
)

img_pair = {}

# full res image is modified first, thumbnail second
img_pair["thumbnail"] = sorted_bg_images[0]
img_pair["background"] = sorted_bg_images[1]

print("Replacing background image located at: ", img_pair["background"])
print("Replacing thumbnail image located at: ", img_pair["thumbnail"])
print("...")

# %% copy chosen image over provided background (and thumbnail for now)
# just replacing both with the same image, no perfect method for determining thumb vs back
shutil.copy("img/background.jpg", img_pair["background"])
shutil.copy("img/background.jpg", img_pair["thumbnail"])

print("Background image replaced successfully!")

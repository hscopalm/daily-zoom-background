import os, platform, shutil, sys
import requests
import yaml
import datetime as dt
from PIL import Image
import psutil
from random import randint


def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, "").count(os.sep)
        indent = " " * 4 * (level)
        print("{}{}/".format(indent, os.path.basename(root)))
        subindent = " " * 4 * (level + 1)
        for f in files:
            print("{}{}".format(subindent, f))


print(list_files(os.getcwd()))
print("\n")
print("Starting the Zoom background changer...")
print("Sys args: ")
print(sys.argv)
print("\n")

print("-" * 50)
print("Reading the config file...")
print("-" * 50)
# read the config file
with open("config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# set the API key
if config["api_key"] != None:
    api_key = config["api_key"]
    print("API key found in config file")
else:
    raise ValueError("API key not found in config file")

include_birthdays = bool(config["birthdays"] == "True")
print("Include birthdays: ", include_birthdays)
auto_select = bool(config["auto_select"] == "True")
print("Auto select: ", auto_select)

# if custom path supplied
if config["zoom_custom_path"] != None:
    zoom_path = config["zoom_custom_path"]
# if windows
elif platform.system() == "Windows":
    zoom_path = r"C:\Users\{user}\AppData\Roaming\Zoom\data".format(user=os.getlogin())
# if mac
elif platform.system() == "Darwin":
    zoom_path = r"/Users/{user}/Library/Application Support/zoom.us/data".format(
        user=os.getlogin()
    )
# if linux (or container)
elif platform.system() == "Linux" or os.path.exists("/.dockerenv"):
    print("Detected that this is running on Linux or in a docker container")

    zoom_path = "/app"

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

with requests.post(holidays_endpoint, headers=header) as resp:

    holidays = dict(zip(range(0, 1000), resp.text.replace('"', "").split("\\n")))

# filter out the birthdays if the user doesn't want them
if not include_birthdays:
    holidays_filt = {
        index: holiday
        for index, holiday in holidays.items()
        if "Birthday" not in holiday
    }
else:
    holidays_filt = holidays

# take the response from the API and print the holidays with their index
print("Available holidays for the provided date: ")
for index in holidays_filt:
    print("[{index}] {holiday}".format(index=index, holiday=holidays[index]))
print("\n")

# next, we need to get the user's choice of holiday
print("-" * 50)
choice_idx = randint(0, len(holidays_filt) - 1)
# choice_idx = input("Please enter the number corresponding to your choice of holiday: ")
print("\n")

choice_name = holidays[int(choice_idx)]

print("-" * 50)
print("You chose: ", choice_name)
print("\n")

# now we need to get the image for the chosen holiday
print("-" * 50)
print("Getting the image for the chosen holiday...")

# we need to send the choice to the API to get the image
img_endpoint = "{root}/{stage}/images".format(root=root, stage=stage)

# take the response from the API and download the image
with requests.post(
    img_endpoint, headers=header, json={"holiday_name": choice_name}
) as resp:
    img_url = resp.text.replace('"', "")


# take the response from the API and download the image
os.makedirs("img", exist_ok=True)  # create the directory if it doesn't exist

# clear the directory of any files from prior runs
file_list = os.listdir("img")
for file_name in file_list:
    file_path = os.path.join("img", file_name)
    os.remove(file_path)

with requests.get(img_url, headers=header, allow_redirects=True, stream=True) as resp:

    redirected_img_url = resp.url
    print("Downloading the image at: " + redirected_img_url)

    # pull the file extension from the url
    orig_file_ext = os.path.splitext(redirected_img_url)[1]
    print("File extension: ", orig_file_ext)

    output_file = "img/background.jpg"
    with open(output_file, "wb") as f:

        if orig_file_ext == ".webp":
            print("WebP file detected, converting the image to the correct format...")

            im = Image.open(resp.raw).convert("RGB")
            im.save(f, "jpeg")
        else:
            shutil.copyfileobj(resp.raw, f)

print("Image downloaded successfully!")
print("\n")

# check if zoom is currently running and kill it if so
if platform.system() == "Windows" or platform.system() == "Darwin":
    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == "Zoom.exe":
            print("-" * 50)
            print("Zoom is currently running, closing the application...")
            proc.kill()
            print("Zoom closed successfully!")
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
shutil.copy(output_file, img_pair["background"])
shutil.copy(output_file, img_pair["thumbnail"])

print("Background image replaced successfully!")

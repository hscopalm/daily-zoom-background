import os
from urllib import request
import json


# read the config file to get the API key and any other configuration
def read_config(filename):
    config = {}
    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):  # Ignore empty lines and comments
                key, value = line.split("=")
                config[key.strip()] = value.strip()
    return config


config = read_config("config.txt")

# these are the headers that we need to send with the request and they are constant
api_key = config["api_key"]
header = {"x-api-key": api_key, "User-Agent": "Mozilla/5.0"}

# first, we need to get the available holidays from the API for today
holidays_endpoint = "https://z2w55sggr4.execute-api.us-east-1.amazonaws.com/v1/holidays"
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

for index in holidays:
    print("[{index}] {holiday}".format(index=index, holiday=holidays[index]))

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

img_endpoint = "https://z2w55sggr4.execute-api.us-east-1.amazonaws.com/v1/images"
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

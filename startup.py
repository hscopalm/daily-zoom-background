import os
from datetime import datetime

# until I can figure out how to read a live stdout from docker subprocess
import docker

# prevent buffering of stdout and stderr
os.environ["PYTHONUNBUFFERED"] = "1"

image_name = "dailyzoombackground"
tag = "latest"
zoom_path = r"C:\Users\hscop\AppData\Roaming\Zoom\data\VirtualBkgnd_Custom"

volume = "{zoom_path}:/app/VirtualBkgnd_Custom".format(zoom_path=zoom_path)

os.makedirs("log", exist_ok=True)  # create the directory if it doesn't exist

client = docker.from_env()

with open(
    "log/output_{ts}.log".format(ts=datetime.now().strftime("%Y%m%d")), "w"
) as output_file:

    container = client.containers.run(
        image_name + ":" + tag, volumes=[volume], detach=True, remove=True
    )

    output = container.attach(stdout=True, stream=True, logs=True)

    for line in output:
        decoded_line = line.decode("utf-8")
        print(decoded_line)
        output_file.write(decoded_line)

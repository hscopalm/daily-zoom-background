# daily-zoom-background
Allows automatically changing your zoom background to a "National Day Of..."

## Usage
To use, ensure you already have used a virtual background before in zoom. This is required, as this effectively commandeers the file name and locations of the last modified custom background.

If you have a default install directory for zoom, there are no configuration steps needed. If you do have a custom install, or encounter issues, set the 'zoom_custom_path' var in the 'config.yaml' to the 'data' folder in your zoom app files.

1. Run the 'daily-zoom-background.py' script
2. (Optional) Schedule using windows .bat, cron, etc
3. Provide the holiday of choice, or a comma separated list to download the top images for each holiday provided
4. Review the images downloaded, and make your final holiday and image selections
5. You're done! Your zoom background should now be a represenation of your favorite holiday

Optionally, explore the 'config.yaml' for more customization options, including the 'auto_selection' mode, birthday mode, image # controls, etc.

## Purpose
This was a fun project to help celebrate a tradition my team followed, in which we changed our background photo in zoom to a "National Day of" photo.

Feel free to use personally, in a work capacity, etc. If you do fork, or use my code, please just give credit!

## Acknowledgements
[The holidays are grabbed from this site](https://nationaltoday.com/what-is-today/)

The images are downloaded via [bing-image-downloader](https://pypi.org/project/bing-image-downloader/)

## Future improvements
The plan is to implement an electron GUI frontend to experiment with the framework, and allow for more friendly usage. This would entail bundling the app into an executable, and incorporating scheduling. 

In addition, replacing the reliance on a package for image download, and pursuing selenium or similar for a headless browser.

If you want to help contribute, just let me know! This is a pet project that I work on in my free time, but am happy to include others if anyone desires.

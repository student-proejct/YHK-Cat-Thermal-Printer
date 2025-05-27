import struct
from sys import argv
import PIL.Image
import PIL.ImageOps
import re
import requests
from io import BytesIO

printerWidth = 384


def printImage(im: PIL.Image):
    im = im.convert('L')
    if im.width > printerWidth:
        # image is wider than printer resolution; scale it down proportionately
        height = int(im.height * (printerWidth / im.width))
        im = im.resize((printerWidth, height))

    im = PIL.ImageOps.invert(im.convert("L"))
    im.save('image.png')


if (len(argv) >= 2):
    if (re.search(r'^http?s://', argv[1])):
        try:
            response = requests.get(argv[1], stream=True)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            printImage(PIL.Image.open(BytesIO(response.content)))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching image from URL: {e}")
    else:
        printImage(PIL.Image.open(argv[1]))

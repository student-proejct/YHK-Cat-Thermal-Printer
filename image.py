import struct
from sys import argv
import PIL.Image
import PIL.ImageOps

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
    printImage(PIL.Image.open(argv[1]))

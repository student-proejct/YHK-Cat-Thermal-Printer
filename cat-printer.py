import socket
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageChops
import PIL.ImageOps
from sys import argv, exit
from time import sleep
import struct
import config,re,requests
from io import BytesIO


# printerMACAddress = 'XX:XX:XX:XX:XX:XX'
printerMACAddress = config.getBlutoothMac()
if not printerMACAddress:
   print("Printer MAC address not configured Please add configuration file to printer app")
   exit()

printerWidth = 384
port = 2


def initilizePrinter(soc):
    soc.send(b"\x1b\x40")


def getPrinterStatus(soc: socket.socket) -> str:
    soc.send(b"\x1e\x47\x03")
    return soc.recv(1024).decode('UTF-8')


def getPrinterSerialNumber(soc):
    soc.send(b"\x1D\x67\x39")
    return soc.recv(21)


def getPrinterProductInfo(soc):
    soc.send(b"\x1d\x67\x69")
    return soc.recv(16)


def sendStartPrintSequence(soc):
    soc.send(b"\x1d\x49\xf0\x19")


def sendEndPrintSequence(soc):
    soc.send(b"\x0a\x0a\x0a\x0a")


def trimImage(im):
    bg = PIL.Image.new(im.mode, im.size, (255, 255, 255))
    diff = PIL.ImageChops.difference(im, bg)
    diff = PIL.ImageChops.add(diff, diff, 2.0)
    bbox = diff.getbbox()
    if bbox:
        # don't cut off the end of the image
        return im.crop((bbox[0], bbox[1], bbox[2], bbox[3]+10))


def create_text(text, font_name="Lucon.ttf", font_size=12):
    img = PIL.Image.new('RGB', (printerWidth, 5000), color=(255, 255, 255))
    font = PIL.ImageFont.truetype(font_name, font_size)

    d = PIL.ImageDraw.Draw(img)
    lines = []
    for line in text.splitlines():
        lines.append(get_wrapped_text(line, font, printerWidth))
    lines = "\n".join(lines)
    d.text((0, 0), lines, fill=(0, 0, 0), font=font)
    return trimImage(img)


def get_wrapped_text(text: str, font: PIL.ImageFont.ImageFont,
                     line_length: int):
    lines = ['']
    for word in text.split():
        line = f'{lines[-1]} {word}'.strip()
        if font.getlength(line) <= line_length:
            lines[-1] = line
        else:
            lines.append(word)
    return '\n'.join(lines)


def standardizeImage(im: PIL.Image) -> PIL.Image:
    im = im.convert('L')
    if im.width > printerWidth:
        # image is wider than printer resolution; scale it down proportionately
        height = int(im.height * (printerWidth / im.width))
        im = im.resize((printerWidth, height))
    return PIL.ImageOps.invert(im.convert("L"))


def printImage(soc, im):
    # print it so it looks right when spewing out of the mouth
    im = standardizeImage(im).rotate(180).convert("1")

    if im.size[0] % 8:
        im2 = PIL.Image.new('1', (im.size[0] + 8 - im.size[0] % 8,
                                  im.size[1]), 'white')
        im2.paste(im, (0, 0))
        im = im2
    buf = b''.join((bytearray(b'\x1d\x76\x30\x00'),
                    struct.pack('2B', int(im.size[0] / 8 % 256),
                                int(im.size[0] / 8 / 256)),
                    struct.pack('2B', int(im.size[1] % 256),
                                int(im.size[1] / 256)),
                    im.tobytes()))
    initilizePrinter(soc)
    sleep(.5)
    sendStartPrintSequence(soc)
    sleep(.5)
    soc.send(buf)
    sleep(.5)
    sendEndPrintSequence(soc)
    sleep(.5)


if (len(argv) >= 2):
    print("your selected file >>" + argv[1])
    s = socket.socket(socket.AF_BLUETOOTH,
                      socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.connect((printerMACAddress, port))

    print("Connecting to printer...")
    print("Printer Status: \t" + getPrinterStatus(s))
    sleep(0.5)
    getPrinterSerialNumber(s)
    sleep(0.5)
    getPrinterProductInfo(s)
    sleep(0.5)

    # Read Image File
    #img = PIL.Image.open(argv[1])
    if (re.compile(r'^http?s://')):
        try:
            response = requests.get(argv[1], stream=True)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            img = PIL.Image.open(BytesIO(response.content))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching image from URL: {e}")
    else:
        img  = PIL.Image.open(argv[1])

    # Create image from text
    # text = "Line 1\nLine 2\nLine 3"
    # img = create_text(text,font_size=65)

    printImage(s,img)
    s.close()

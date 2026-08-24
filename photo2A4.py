#!/usr/bin/python

import sys
import os
import getopt
import traceback
from PIL import Image


# Output file
resultfile = 'A4.png'

# Open the result after saving
openresult = True

# Size of A4 resulting image
resultsizex = 2480
resultsizey = 3508

# Size of single image on result
photox = 1170
photoy = 1755

# Padding around each image
toppadding = 200
leftpadding = 50
middlepadding = 50
resultpadding = 10

# Crop images to fit
cropmode = False

fillwidth = False
fillheight = False

# Parse arguments
def help():
    print("USAGE:")
    print(sys.argv[0]+" [-c] [image1] [image2] [image3]")
    print("Specify 1-3 image files to combine into an A4 image.")
    print("-c Crop images to fit")
    print("-w Fill width")
    print("-h Fill height")
    return

try:
    optlist, args = getopt.getopt(sys.argv[1:], "cwh")
except getopt.GetoptError as err:
    sys.stderr.write(str(err)+"\n")
    help()
    sys.exit(1)

for o, a in optlist:
    if o == "-c":
        cropmode = True
    elif o == "-w":
        fillwidth = True
    elif o == "-h":
        fillheight = True
    else:
        sys.stderr.write("Unknown option: "+str(o)+"\n")
        sys.exit(1)

if fillwidth and fillheight:
    sys.stderr.write("Only one of fill width (-w) or fill height (-h) can be set at once.\n")
    sys.exit(1)

if len(args) < 1:
    help()
    sys.exit()

if len(args) > 3:
    sys.stderr.write("ERROR: Please specify 1-3 image files.\n")
    help()
    sys.exit(1)

# Create blank result image
result = Image.new('RGB', (resultsizex, resultsizey), 'white')

# Main loop - open each image, resize, crop then paste onto result
imageno = 0
for image in args:
    # Try to open the input image
    try:
        img = Image.open(image)
    except:
        print("ERROR: Cannot open image "+imageno)
        traceback.print_exc()
        sys.exit()

    # Get size
    width, height = img.size
    print("IMAGE "+str(imageno)+" SIZE: "+str(width)+" x "+str(height))

    # Rotate if image is not portrait
    if width > height:
        print("ROTATING IMAGE")
        img = img.rotate(90, expand=True)
        width, height = img.size

    if fillwidth:
        # If image is larger than the target size, scale it down. Else, scale it up.
        if width > photox:
            print("SCALING DOWN")
            r = float(width)/float(photox)
            r = float(height)/float(r)
            img.thumbnail((photox, int(r)), Image.LANCZOS)
        else:
            # If image is smaller, scale it up until it fills the width
            print("SCALING UP TO WIDTH")
            r = float(photox)/float(width)
            r = float(height)*float(r)
            img = img.resize((photox, int(r)), Image.LANCZOS)
    elif fillheight:
        if height > photoy:
            print("SCALING DOWN")
            r = float(height)/float(photoy)
            r = float(width)/float(r)
            img.thumbnail((int(r), photoy), Image.LANCZOS)
        else:
            print("SCALING UP TO HEIGHT")
            r = float(photoy)/float(height)
            r = float(width)*float(r)
            img = img.resize((int(r), photoy), Image.LANCZOS)
    else:
        if height > photoy:
            print("SCALING DOWN")
            r = float(height)/float(photoy)
            r = float(width)/float(r)
            img.thumbnail((int(r), photoy), Image.LANCZOS)
        else:
            # If image is smaller, work out which side is closest to the target size and scale up until it hits the target
            photoxdiff = photox - width
            photoydiff = photoy - height
            if photoxdiff > photoydiff:
                print("SCALING UP TO HEIGHT")
                r = float(photoy)/float(height)
                r = float(width)*float(r)
                img = img.resize((int(r), photoy), Image.LANCZOS)
            else:
                print("SCALING UP TO WIDTH")
                r = float(photox)/float(width)
                r = float(height)*float(r)
                img = img.resize((photox, int(r)), Image.LANCZOS)

        width, height = img.size
        if height > photoy:
            print("SCALING DOWN TO HEIGHT")
            r = float(height)/float(photoy)
            r = float(width)/float(r)
            img.thumbnail((int(r), photoy), Image.LANCZOS)
        elif width > photox:
            print("SCALING DOWN TO WIDTH")
            r = float(width)/float(photox)
            r = float(height)/float(r)
            img.thumbnail((photox, int(r)), Image.LANCZOS)

    # Get new image size
    width, height = img.size

    # Crop the image if we need to
    if cropmode and (width > photox or height > photoy):
        print("CROPPING IMAGE")
        img = img.crop((((width - photox)/2), 0, ((width+photox)/2), photoy))
        width, height = img.size

    print("NEW IMAGE SIZE: "+str(width)+" x "+str(height))

    # Rotate third image
    if imageno == 2:
        img = img.rotate(90, expand=True)
    else:
        bottomimagepos = photoy+(resultpadding*2)+toppadding+middlepadding

    # Paste images onto the result
    if imageno == 0:
        result.paste(img, (resultpadding+leftpadding, resultpadding+toppadding))
    elif imageno == 1:
        result.paste(img, (int((resultsizex/2)+resultpadding), resultpadding+toppadding))
    elif imageno == 2:
        result.paste(img, (resultpadding+leftpadding, bottomimagepos))

    imageno += 1

# Save the result
result.save(resultfile)

if openresult:
    # Windows
    if os.name == "nt":
        os.system('rundll32 "C:\Program Files\Windows Photo Viewer\PhotoViewer.dll" ImageView_Fullscreen '+resultfile)


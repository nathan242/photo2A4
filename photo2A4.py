#!/usr/bin/python

import sys
import os
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


# Parse arguments
def help():
    print "USAGE:"
    print sys.argv[0]+" [image1] [image2] [image3]"
    print "Specify 1-3 image files to combine into an A4 image."
    return

if len(sys.argv) < 2:
    help()
    quit()

if len(sys.argv) > 4:
    print "ERROR: Please specify 1-3 image files."
    help()
    quit()

# Create blank result image
result = Image.new('RGB', (resultsizex, resultsizey), 'white')

# Main loop - open each image, resize, crop then paste onto result
imageno = 0
for image in sys.argv:
    if imageno == 0:
        imageno += 1
        continue

    # Try to open the input image
    try:
        img = Image.open(image)
    except:
        print "ERROR: Cannot open image "+imageno
        traceback.print_exc()
        quit()

    # Get size
    width, height = img.size
    print "IMAGE "+str(imageno)+" SIZE: "+str(width)+" x "+str(height)

    # Rotate if image is not portrait
    if width > height:
        img = img.rotate(90)
        width, height = img.size

    # If image is larger than the target size, scale it down. Else, scale it up.
    if height > photoy:
        print "SCALING DOWN"
        r = float(height)/float(photoy)
        r = float(width)/float(r)
        img.thumbnail((int(r), photoy), Image.ANTIALIAS)
        # Crop the image if we need to
        width, height = img.size
        if width > photox or height > photoy:
            print "CROPPING IMAGE"
            img = img.crop((((width - photox)/2), 0, ((width+photox)/2), photoy))
    else:
        # If image is smaller, work out which side is closest to the target size and scale up until it hits the target
        photoxdiff = photox - width
        photoydiff = photoy - height
        if photoxdiff > photoydiff:
            print "SCALING UP TO HEIGHT"
            r = float(photoy)/float(height)
            r = float(width)*float(r)
            img = img.resize((int(r), photoy), Image.ANTIALIAS)
        else:
            print "SCALING UP TO WIDTH"
            r = float(photox)/float(width)
            r = float(height)*float(r)
            img = img.resize((photox, int(r)), Image.ANTIALIAS)

    # Get new image size
    width, height = img.size
    print "NEW IMAGE SIZE: "+str(width)+" x "+str(height)

    # Rotate third image
    if imageno == 3:
        img = img.rotate(90)
    else:
        bottomimagepos = photoy+(resultpadding*2)+toppadding+middlepadding

    # Paste images onto the result
    if imageno == 1:
        result.paste(img, (resultpadding+leftpadding, resultpadding+toppadding))
    elif imageno == 2:
        result.paste(img, ((resultsizex/2)+resultpadding, resultpadding+toppadding))
    elif imageno == 3:
        result.paste(img, (resultpadding+leftpadding, bottomimagepos))

    imageno += 1

# Save the result
result.save(resultfile)

if openresult:
    # Windows
    if os.name == "nt":
        os.system('rundll32 "C:\Program Files\Windows Photo Viewer\PhotoViewer.dll" ImageView_Fullscreen '+resultfile)

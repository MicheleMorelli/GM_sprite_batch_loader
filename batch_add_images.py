import os
import sys
from PIL import Image
import xml.etree.ElementTree as ET
import re

def setup_directories():
    # Set current working directory to the directory of the script
    CURRDIR = os.path.dirname( os.path.abspath( __file__ ) )
    # create temp work dir
    os.chdir( CURRDIR )
    if (not os.path.isdir('./temp')):
        os.mkdir('temp')
    return CURRDIR + '/in_dir', CURRDIR + '/out_dir', CURRDIR + '/temp'


def decompose_img(filename, out_dir):
    name = re.sub('\.gif','', os.path.basename(filename))
    print("Processing " + name)
    cmd = "convert -coalesce %s %s/%s_%%d.png" % (filename, out_dir, name)
    os.system(cmd)


def remove_background(png_img, in_dir, out_dir):
    cmd = 'convert %s/%s -transparent "rgb(112,204,110)" %s/%s' % (in_dir, png_img, out_dir,png_img)
    os.system(cmd)


def process_image_and_get_info(img, images, INDIR,OUTDIR, TEMPDIR):
    #processes the images (decopmpose, remove background), copies them in the output folder adn returns
    #a dictionary containing all the information on the 
    images[img] = {}
    gif = Image.open(img)
    images[img]['WIDTH'], images[img]['HEIGHT'] = gif.size
    decompose_img(INDIR +"/"+ img, TEMPDIR)
    frame_counter = 0
    for png in os.listdir(TEMPDIR):
        images[img][frame_counter] = png
        frame_counter += 1
        remove_background(png,TEMPDIR, OUTDIR)
        #os.rename( TEMPDIR +"/"+ png, OUTDIR + "/" + png )


def main():
    
    INDIR, OUTDIR, TEMPDIR = setup_directories() 
    # store info for xml in a dictionary
    images_info = {}
    os.chdir(INDIR)
    for image in os.listdir(INDIR):
        process_image_and_get_info(image, images_info, INDIR,OUTDIR, TEMPDIR)   
    
    #TODO change this!
    os.system("rm -rf %s" % TEMPDIR)
    
    print(images_info)


if (__name__ == '__main__'):
    main()

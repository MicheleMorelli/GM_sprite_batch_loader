import os
import shutil
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
    if (not os.path.isdir('./out_dir')):
        os.mkdir('out_dir')
    if (not os.path.isdir('./out_dir/images')):
        os.mkdir('out_dir/images')
    return CURRDIR + '/in_dir', CURRDIR + '/out_dir', CURRDIR + '/out_dir/images', CURRDIR + '/temp', CURRDIR


def decompose_img(filename, out_dir):
    name = re.sub('\.gif','', os.path.basename(filename))
    cmd = "convert -coalesce %s %s/%s_%%d.png" % (filename, out_dir, name)
    os.system(cmd)


def remove_background(png_img, in_dir, out_dir):
    cmd = 'convert %s/%s -transparent "rgb(112,204,110)" %s/%s' % (in_dir, png_img, out_dir,png_img)
    os.system(cmd)


def rm_wildcard(location):
    for f in os.listdir(location):
            os.remove(os.path.join(location,f))



def process_image_and_get_info(img, images, INDIR,OUTDIR, TEMPDIR):
    #processes the images (decopmpose, remove background), copies them in the output folder adn returns
    #a dictionary containing all the information on the 
    images[img] = {}
    gif = Image.open(img)
    images[img]['WIDTH'], images[img]['HEIGHT'] = gif.size
    decompose_img(INDIR +"/"+ img, TEMPDIR)
    images[img]['FRAMES'] = []
    for png in os.listdir(TEMPDIR):
        images[img]['FRAMES'].append(png)
        remove_background(png,TEMPDIR, OUTDIR)
    rm_wildcard(TEMPDIR)  # to remove the pngs from the temp folder once done. 


def create_sprite_gmx(filename,images_info, TEMPLATEDIR, OUTDIR):
    print("Processing %s..." % filename, end="")
    template = TEMPLATEDIR + '/template.gmx'
    target_file = OUTDIR + '/' + re.sub('\.gif','', filename) + ".sprite.gmx"
    shutil.copy(template,target_file)
    tree = ET.parse(target_file)
    root = tree.getroot()
    set_xml_value(root,'width', images_info[filename]['WIDTH']) 
    set_xml_value(root,'height', images_info[filename]['HEIGHT'])
    set_xml_value(root,'bbox_right', images_info[filename]['WIDTH'] - 1)
    set_xml_value(root,'bbox_bottom', images_info[filename]['HEIGHT'] - 1)
    for i in range(len(images_info[filename]['FRAMES'])):
        append_xml_value(root, root.find('frames'), 'frame', "images\\" + images_info[filename]['FRAMES'][i], {'index':str(i)})
    tree.write(target_file)
    print("Done!")

def update_master_gmx(master_gmx_file, images_info):
    tree = ET.parse(master_gmx_file)
    root = tree.getroot()
    for sprite in images_info:
        name = re.sub('\.gif','', sprite)
        append_xml_value(root, root.find('sprites'), 'sprite', "sprites\\" + name, {})
    tree.write(master_gmx_file + "BACKUP")


def set_xml_value(root, tag, new_value):
    for e in root.iter(tag):
        e.text = str(new_value)


def append_xml_value(root, parent, tag, new_value, attrib_dict):
        ET.SubElement(parent, tag , attrib=attrib_dict).text = new_value 

def main():
    
    INDIR, OUTDIR, OUTDIR_IMAGES, TEMPDIR, SCRIPTDIR = setup_directories() 
    # store info for xml in a dictionary
    images_info = {}
    os.chdir(INDIR)
    for image in os.listdir(INDIR):
        process_image_and_get_info(image, images_info, INDIR, OUTDIR_IMAGES, TEMPDIR) 
        create_sprite_gmx(image, images_info, SCRIPTDIR, OUTDIR)

    update_master_gmx(SCRIPTDIR + '/sprite_batch_test.project.gmx', images_info)
    #TODO change this!
    os.system("rm -rf %s" % TEMPDIR)
    
    print(images_info)


if (__name__ == '__main__'):
    main()

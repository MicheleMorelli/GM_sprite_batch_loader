import os
import shutil
import sys
from PIL import Image
import xml.etree.ElementTree as ET
import re
import json



def set_directories():
    PROJECT_DIR, SPRITES_SOURCE_DIR = get_project_and_sprites_dirs()
    print(f"PROJECT: {PROJECT_DIR}\n SPRITES SOURCE DIR: {SPRITES_SOURCE_DIR}")
    return PROJECT_DIR, SPRITES_SOURCE_DIR



def decompose_img(filename, out_dir):
    name = re.sub(r"\.(gif|png)","", os.path.basename(filename))
    cmd = f"convert -coalesce {filename} {out_dir}/{name}.png"
    os.system(cmd)


def remove_background(png_img, in_dir, out_dir):
    cmd = 'convert %s/%s -transparent "rgb(112,204,110)" %s/%s' % (in_dir, png_img, out_dir,png_img)
    os.system(cmd)


def rm_wildcard(location):
    for f in os.listdir(location):
            os.remove(os.path.join(location,f))





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


def get_args():
    '''
    Get the arguments from the commandline. The script expects the first arg
    to be an existing GMS project, and the second argument to be the source
    of the sprites hierarchy to be imported.
    '''
    args = sys.argv
    if (len(args) <= 2):
        abort(f"Please indicate the project and the sprites folder\n"
                f"e.g. {__name__} project.project sprites")
    project = args[1]
    sprite_source = args[2]
    return project, sprite_source
    

def get_project_and_sprites_dirs():
    project, sprites_source = get_args()
    if (valid_project_and_sprites_source(project, sprites_source)):
        return project, sprites_source
    abort("ERROR: something is wrong with the arguments that were passed...")


def valid_project_and_sprites_source(project, sprites_source):
    if (not os.path.isdir(sprites_source)):
        abort(f"ERROR: the indicated sprite source ({sprites_source}) is incorrect."
                f"Aborting...")
    return (is_a_project(project) and os.path.isdir(sprites_source))

def is_a_project(project):
    if (not os.path.isdir(project)):
        abort(f"ERROR: the indicated project ({project}) is incorrect."
                f"Aborting...")
    for fname in os.listdir(project):
        if (fname.endswith('.project.gmx')):
            return True
    abort(f"ERROR: {project} does not look like a GML project."
            f"Aborting...")



def abort(message):
    print(message)
    sys.exit(1)


def process_sprite_hierarchy_element(element, BASE_DIR, hierarchy_dict, PROJECT_DIR):
    '''
    recursively creates a dictionary with all the images and 
    '''
    element_path = f"{BASE_DIR}{element}"
    # is a terminal leaf (ie a png or gif file)?
    if (os.path.isfile(element_path) and re.search("\.(png|gif)$",element)):
        return process_image_and_get_info(element, BASE_DIR, PROJECT_DIR)
    # if it's a directory, keep going down the tree recursively
    elif (os.path.isdir(element_path)):
        NEW_BASE_DIR = f"{BASE_DIR}{element}/"
        return {x: process_sprite_hierarchy_element(x,NEW_BASE_DIR,hierarchy_dict,PROJECT_DIR) for x in os.listdir(NEW_BASE_DIR)} 


def process_image_and_get_info(img, SOURCE_DIR, PROJECT_DIR):
    #processes the images (decopmpose, potentially remove background), copies them in the output folder adn returns
    #a dictionary containing all the information on the 
    d = {}
    gif = Image.open(f"{SOURCE_DIR}/{img}")
    d['WIDTH'], d['HEIGHT'] = gif.size
    #tempdir
    TEMP_DIR = f"{PROJECT_DIR}/___temp"
    if (not os.path.isdir(TEMP_DIR)):
        os.mkdir(TEMP_DIR)
        print(f"TEMP dir created: {TEMP_DIR}")
    decompose_img(f"{SOURCE_DIR}/{img}", TEMP_DIR)
    # count the frames
    d['FRAMES'] = [x for x in os.listdir(TEMP_DIR)]
    # TODO: copy the actualfiles from the temp dir to the real outdir
    rm_wildcard(TEMP_DIR)  # to remove the pngs from the temp folder once done. 
    return d

def main():
    PROJECT_DIR, SPRITES_SOURCE_DIR = set_directories()
    #build_sprites_dictionary(SPRITES_SOURCE_DIR, PROJECT_DIR)
    images_dict = process_sprite_hierarchy_element(".",SPRITES_SOURCE_DIR,{}, PROJECT_DIR)
    print(json.dumps(images_dict,indent=4))




#    for element in os.listdir(SPRITES_SOURCE_DIR):
#        if (element)
#        process_image_and_get_info(image, images_info, INDIR, OUTDIR_IMAGES, TEMPDIR) 
#        create_sprite_gmx(image, images_info, SCRIPTDIR, OUTDIR)



    
#    INDIR, OUTDIR, OUTDIR_IMAGES, TEMPDIR, SCRIPTDIR = setup_directories() 
#    # store info for xml in a dictionary
#    images_info = {}
#    os.chdir(INDIR)
#    for image in os.listdir(INDIR):
#        process_image_and_get_info(image, images_info, INDIR, OUTDIR_IMAGES, TEMPDIR) 
#        create_sprite_gmx(image, images_info, SCRIPTDIR, OUTDIR)
#
#    update_master_gmx(SCRIPTDIR + '/sprite_batch_test.project.gmx', images_info)
#    #TODO change this!
#    os.system("rm -rf %s" % TEMPDIR)
#    
#    print(images_info)
    
    


if (__name__ == '__main__'):
    main()

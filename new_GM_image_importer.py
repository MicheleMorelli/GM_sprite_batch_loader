from typing import List, Dict, Any, Union
import os
import shutil
import sys
from PIL import Image
import xml.etree.ElementTree as ET
import re
import json



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




def get_structure_as_dict(element: str, BASE_DIR: str) -> Dict[str,Any]:
    '''
    Recursively creates a dictionary with the structure of all the images 
    and the directories in the images source dir. 
    '''
    element_path = f"{BASE_DIR}{element}"
    # is a terminal leaf (ie a png or gif file)?
    if (is_an_image_file(element, BASE_DIR, element_path)):
        return {
                "NAME":element, 
                "TYPE":"file", 
                "SOURCE_PATH" : BASE_DIR
                }
    # if it's a directory, keep traversing the tree recursively
    elif (os.path.isdir(element_path)):
        NEW_BASE_DIR = f"{BASE_DIR}{element}/"
        # putting the recursive call in a lambda for readability
        recursive_struct = lambda x: get_structure_as_dict(x, NEW_BASE_DIR)
        return {
                "NAME" : element,
                "TYPE":"directory",
                "SOURCE_PATH" : NEW_BASE_DIR,
                "CONTENTS" : [recursive_struct(x) for x in os.listdir(NEW_BASE_DIR)]
                }


def process_image_nodes_and_update_dict(img_metadata_dict, SOURCE_DIR, PROJECT_DIR):
    '''
    Recursively processes the images (decompose, potentially remove background), 
    copies them in the output folder and updates the structure 
    dictionary with more the information on the images' metadata 
    TODO:
    Heavy IO - asyncio?
    side effects!
    '''
    d: Dict[str, Any] = img_metadata_dict # lazy alias! :-)
    if (d["TYPE"] == "directory"):
        recurse_images = lambda x: process_image_nodes_and_update_dict(x,x["SOURCE_PATH"], PROJECT_DIR) 
        d["CONTENTS"] = list(map(recurse_images, d["CONTENTS"]))
        return d
    elif (d["TYPE"] == "file"):
        filename = d["NAME"] 
        image_path = f"{SOURCE_DIR}/{filename}"
        image: PIL.Image = Image.open(image_path)
        d['WIDTH'], d['HEIGHT'] = image.size
        #tempdir
        TEMP_DIR = f"{PROJECT_DIR}/___temp"
        if (not os.path.isdir(TEMP_DIR)):
            os.mkdir(TEMP_DIR)
            print(f"TEMP dir created: {TEMP_DIR}")
        decompose_img(image_path, TEMP_DIR)
        # count the frames
        d['FRAMES'] = [x for x in os.listdir(TEMP_DIR)]
        # target put dir - check if exists!
        target_output_dir = project_sprites_dirs(PROJECT_DIR)[1]
        copy_all_files(TEMP_DIR,target_output_dir)
        rm_wildcard(TEMP_DIR)  # to remove the pngs from the temp folder once done. 
        return d


def make_all_sprite_gmx_files(sprites_dict: Dict[str, Any], target_dir: str) -> None:
    '''
    Traverses the sprites tree and creates the GMX files
    TODO:
    fix side effects!
    '''
    d: Dict[str, Any] = sprites_dict
    if (d["TYPE"] == "file"):
        create_gmx_resource_file(d, target_dir)
    elif (d["TYPE"] == "directory"):
        for element in d["CONTENTS"]:
            make_all_sprite_gmx_files(element, target_dir) 


def create_gmx_resource_file(data_dict, target_dir) -> None:
    '''
    Creates the GMX resource file from a template
    '''
    d: Dict[str, Any] = data_dict
    filename = d['NAME']
    print(f"Creating GMX Sprite for {filename}...", end="")
    sprite_name = re.sub('\.(gif|png)$','', filename)
    template_dir = os.path.dirname(os.path.realpath(__file__)) 
    template = f"{template_dir}/template.gmx"
    target_file = f"{target_dir}/{sprite_name}.sprite.gmx"
    shutil.copy(template,target_file)
    tree = ET.parse(target_file)
    root = tree.getroot()
    set_xml_value(root,'width', d['WIDTH']) 
    set_xml_value(root,'height', d['HEIGHT'])
    set_xml_value(root,'bbox_right', d['WIDTH'] - 1)
    set_xml_value(root,'bbox_bottom', d['HEIGHT'] - 1)
    for i in range(len(d['FRAMES'])):
        append_xml_value(root, root.find('frames'), 'frame', f"images\\{d['FRAMES'][i]}", {'index':str(i)})
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

def set_directories():
    proj_dir, source_dir = get_project_and_sprites_dirs()
    print(f"PROJECT: {proj_dir}\n SPRITES SOURCE DIR: {source_dir}")
    return proj_dir, source_dir 


def project_sprites_dirs(target_dir):
    # set PROJECT_SPRITES_DIR and PROJECT_SPRITES_IMAGES_DIR
    PROJECT_SPRITES_DIR = f"{target_dir}/sprites"
    PROJECT_SPRITES_IMAGES_DIR = f"{PROJECT_SPRITES_DIR}/images" 
    if (not os.path.isdir(PROJECT_SPRITES_DIR) or 
            not os.path.isdir(PROJECT_SPRITES_IMAGES_DIR)):
        abort(f"ERROR: the script expects the target project sprites directory"
                f"to be in the standard GMS format.\nAborting..."
                f"{PROJECT_SPRITES_DIR}   {PROJECT_SPRITES_IMAGES_DIR}")
    return PROJECT_SPRITES_DIR, PROJECT_SPRITES_IMAGES_DIR
    

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


def copy_all_files(src_dir,target_dir):
    for file_name in os.listdir(src_dir):
        file_path = os.path.join(src_dir, file_name)
        if os.path.isfile(file_path):
            shutil.copy(file_path, target_dir)


def abort(message):
    print(message)
    sys.exit(1)


def is_an_image_file(element:str, BASE_DIR:str, element_path:str) -> bool:
    return os.path.isfile(element_path) and re.search("\.(png|gif)$",element)


def main() -> None:
    PROJECT_DIR, SPRITES_SOURCE_DIR  =  set_directories()
    # Get the structure of the source dir as a dictionary
    source_structure: Dict[str, Any] = get_structure_as_dict(".",SPRITES_SOURCE_DIR)
    #process the images
    processed_structure: Dict[str,Any] = process_image_nodes_and_update_dict(source_structure, SPRITES_SOURCE_DIR, PROJECT_DIR) 
    print(json.dumps(processed_structure,indent=2))
    #create the sprite GMXs for all images in the dictionary
    make_all_sprite_gmx_files(processed_structure,project_sprites_dirs(PROJECT_DIR)[0] )


if (__name__ == '__main__'):
    main()

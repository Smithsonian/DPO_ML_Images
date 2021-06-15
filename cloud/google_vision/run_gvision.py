#!/usr/bin/env python3
#
# Google Vision API based on their reference docs at:
#  https://github.com/googleapis/python-vision/blob/HEAD/samples/snippets/detect/detect.py
#
# To run: python3 run_gvision.py <path to jpg files> 
#

import io, json, sys, os, glob, shutil
#import psycopg2
#from PIL import Image, ImageDraw
#from PIL import ImagePath
from pathlib import Path
from pyfiglet import Figlet


#Script variables
script_title = "Google Vision ML Image Data Extraction"
subtitle = "Digitization Program Office\nOffice of the Chief Information Officer\nSmithsonian Institution\nhttps://dpo.si.edu"
ver = "0.1"
vercheck = "https://raw.githubusercontent.com/Smithsonian/DPO_ML_Images/master/cloud/google_vision/toolversion.txt"
repo = "https://github.com/Smithsonian/DPO_ML_Images/"
lic = "Available under the Apache 2.0 License"


#Check for updates to the script
try:
    with urllib.request.urlopen(vercheck) as response:
       current_ver = response.read()
    cur_ver = current_ver.decode('ascii').replace('\n','')
    if cur_ver != ver:
        msg_text = "{subtitle}\n\n{repo}\n{lic}\n\nver. {ver}\nThis version is outdated. Current version is {cur_ver}.\nPlease download the updated version at: {repo}"
    else:
        msg_text = "{subtitle}\n\n{repo}\n{lic}\n\nver. {ver}"
except:
    msg_text = "{subtitle}\n\n{repo}\n{lic}\n\nver. {ver}"
    cur_ver = ver




f = Figlet(font='slant')
print("\n")
print (f.renderText(script_title))
#print(script_title)
print(msg_text.format(subtitle = subtitle, ver = ver, repo = repo, lic = lic, cur_ver = cur_ver))



#if len(sys.argv) != 3:
    #print("Error: arguments missing. Usage:\n\n ./run_gvision.py <folder with jpgs> <process>")

if len(sys.argv) != 2:
    print("Error: arguments missing. Usage:\n\n ./run_gvision.py <folder with jpgs>")
    sys.exit(1)
else:
    if os.path.isdir(sys.argv[1]) == False:
        print("Error: path to JPG files does not exists.")
        sys.exit(1)
    else:
        path = sys.argv[1]
        #ml_process = sys.argv[2]



#Check if there is a creds.json file
if os.path.isfile("{}/creds.json".format(os.getcwd())) == False:
    print("Error: creds.json missing.")
    sys.exit(1)
else:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "{}/creds.json".format(os.getcwd())


#Load google vision
from google.cloud import vision_v1p3beta1 as vision
client = vision.ImageAnnotatorClient()



#Import database settings from settings.py file
import settings


#Get images
list_of_files = glob.glob('{}/*.jpg'.format(path))
print("\n\nFound {} files.".format(len(list_of_files)))


#Run each file
for filename in list_of_files:
    file_stem = Path(filename).stem
    #Open file
    print("Reading image...")
    with io.open(filename, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content = content)
    results = client.object_localization(image=image)
    objects = results.localized_object_annotations
    with open('{}/{}.json'.format("images", file_stem), 'w') as out:
        out.write(str(objects))


sys.exit(0)

#!/usr/bin/env python3
#
# How to run: python3 object_detection.py [path to JPG files]
#

import io, json, sys, os, glob
from PIL import Image, ImageDraw 
from PIL import ImagePath
from pathlib import Path
import pandas as pd
import csv
from google.cloud import vision
from pyfiglet import Figlet


#Script variables
script_title = "Object Detection using Google Vision"
subtitle = "Digitization Program Office\nOffice of the Chief Information Officer\nSmithsonian Institution\nhttps://dpo.si.edu"
ver = "0.1"
# 2022-05-04
# vercheck = ""
repo = "https://github.com/Smithsonian/"
lic = "Available under the Apache 2.0 License"


# Check for updates to the script
# try:
#     with urllib.request.urlopen(vercheck) as response:
#        current_ver = response.read()
#     cur_ver = current_ver.decode('ascii').replace('\n','')
#     if cur_ver != ver:
#         msg_text = "{subtitle}\n\n{repo}\n{lic}\n\nver. {ver}\nThis version is outdated. Current version is {cur_ver}.\nPlease download the updated version at: {repo}"
#     else:
#         msg_text = "{subtitle}\n\n{repo}\n{lic}\n\nver. {ver}"
# except:
#     msg_text = "{subtitle}\n\n{repo}\n{lic}\n\nver. {ver}"
#     cur_ver = ver


msg_text = "{subtitle}\n\n{repo}\n{lic}\n\nver. {ver}"


f = Figlet(font='slant')
print("\n")
print (f.renderText(script_title))
#print(script_title)
print(msg_text.format(subtitle = subtitle, ver = ver, repo = repo, lic = lic, cur_ver = ver))


# Check if there is a creds.json file
if os.path.isfile("{}/creds.json".format(os.getcwd())) == False:
    print("Error: creds.json missing.")
    sys.exit(1)
else:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "{}/creds.json".format(os.getcwd())


if len(sys.argv) != 2:
    print("Error: path to JPG files missing.")
    sys.exit(1)
else:
    path = sys.argv[1]


line_buffer = 4
color_breaks = [0.90, 0.80, 0.70]

client = vision.ImageAnnotatorClient()


if os.path.exists('object_extracted') == False:
    os.mkdir('object_extracted')
if os.path.exists('csv') == False:
    os.mkdir('csv')
if os.path.exists('object_response') == False:
    os.mkdir('object_response')

#Get images
list_of_files = glob.glob('{}/*.jpg'.format(path))
print("\n\nFound {} files.".format(len(list_of_files)))


for filename in list_of_files:
    with open(filename, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content = content)
    response = client.object_localization(image = image)
    print('Number of objects found: {}'.format(len(response.localized_object_annotations)))
    response = response.localized_object_annotations
    # PIL
    im = Image.open(filename)
    data_file = '{}.csv'.format(Path(filename).stem)
    with open('object_response/{}.txt'.format(Path(filename).stem), 'w') as out:
        out.write(str(response))
    list_of_objects = pd.DataFrame(columns = ['name', 'score'])
    for object_ in response:
        # write object and confidence to df
        list_of_objects.loc[len(list_of_objects)] = [object_.name, object_.score]
        # write box to image
        if object_.score > color_breaks[0]:
            linecolor = "#66ff33"
        elif object_.score <= color_breaks[0] and object_.score > color_breaks[1]:
            linecolor = "#ffdb4d"
        elif object_.score <= color_breaks[1] and object_.score > color_breaks[2]:
            linecolor = "#ffa366"
        elif object_.score <= color_breaks[2]:
            linecolor = "#ff6666"
        draw = ImageDraw.Draw(im)
        draw.line([(float(object_.bounding_poly.normalized_vertices[0].x)*int(im.size[0]) - line_buffer, float(object_.bounding_poly.normalized_vertices[0].y)*int(im.size[1]) - line_buffer), (float(object_.bounding_poly.normalized_vertices[1].x)*int(im.size[0]) + line_buffer, float(object_.bounding_poly.normalized_vertices[1].y)*int(im.size[1]) + line_buffer)], fill = linecolor, width = line_buffer)
        draw.line([(float(object_.bounding_poly.normalized_vertices[1].x)*int(im.size[0]) - line_buffer, float(object_.bounding_poly.normalized_vertices[1].y)*int(im.size[1]) - line_buffer), (float(object_.bounding_poly.normalized_vertices[2].x)*int(im.size[0]) + line_buffer, float(object_.bounding_poly.normalized_vertices[2].y)*int(im.size[1]) + line_buffer)], fill = linecolor, width = line_buffer)
        draw.line([(float(object_.bounding_poly.normalized_vertices[2].x)*int(im.size[0]) - line_buffer, float(object_.bounding_poly.normalized_vertices[2].y)*int(im.size[1]) - line_buffer), (float(object_.bounding_poly.normalized_vertices[3].x)*int(im.size[0]) + line_buffer, float(object_.bounding_poly.normalized_vertices[3].y)*int(im.size[1]) + line_buffer)], fill = linecolor, width = line_buffer)
        draw.line([(float(object_.bounding_poly.normalized_vertices[3].x)*int(im.size[0]) - line_buffer, float(object_.bounding_poly.normalized_vertices[3].y)*int(im.size[1]) - line_buffer), (float(object_.bounding_poly.normalized_vertices[0].x)*int(im.size[0]) + line_buffer, float(object_.bounding_poly.normalized_vertices[0].y)*int(im.size[1]) + line_buffer)], fill = linecolor, width = line_buffer)
        del draw
    img_file = 'object_extracted/{}.jpg'.format(Path(filename).stem)
    # Save cropped image
    im.save(img_file, "JPEG")
    data_file = 'csv/{}.csv'.format(Path(filename).stem)
    list_of_objects.to_csv(data_file, quoting=csv.QUOTE_NONNUMERIC, index=False)
    print(list_of_objects)


sys.exit(0)

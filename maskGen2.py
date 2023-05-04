import os
import cv2
import json
import numpy as np

source_folder = os.path.join(os.getcwd(), "images")
# Relative to root directory
count = 0                                           # Count of total images saved
# Dictionary containing polygon coordinates for mask
file_bbs = {}
# Dimensions should match those of ground truth image
MASK_WIDTH = 1101
MASK_HEIGHT = 750

#Path of JSON files
json_folder = os.path.join(os.getcwd(), "json_folder")
subMaskCount = []

def add_to_dict(data, itr, key, count, file_bbs):
    print(itr, count)
    try:
        x_points = data[itr]["regions"][count]["shape_attributes"]["all_points_x"]
        y_points = data[itr]["regions"][count]["shape_attributes"]["all_points_y"]
    except:
        print("No BB. Skipping", key)
        return
    all_points = []
    for i, x in enumerate(x_points):
        all_points.append([x, y_points[i]])
    file_bbs[key] = all_points


for file_name in os.listdir(source_folder):
    # Get JSON file name
    json_file = file_name[:-4] + ".json"
    json_path = os.path.join(json_folder, json_file)
    print(json_path)
     # Create folders
    to_save_folder = os.path.join(source_folder, file_name[:-4])
    image_folder = os.path.join(to_save_folder, "images") 
    mask_folder = os.path.join(to_save_folder, "masks")
    os.mkdir(to_save_folder)
    os.mkdir(image_folder)
    os.mkdir(mask_folder)
    
    with open(json_path) as f:
        data = json.load(f)
        
    file_bbs = {}
    for itr in data:
        file_name_json = data[itr]["filename"]
        sub_count = 0               # Contains count of masks for a single ground truth image
        if len(data[itr]["regions"]) > 1:
            for _ in range(len(data[itr]["regions"])):
                key = file_name_json[:-4] + "*" + str(sub_count+1)
                add_to_dict(data, itr, key, sub_count, file_bbs)
                sub_count += 1
        else:
            add_to_dict(data, itr, file_name_json[:-4], 0, file_bbs)
        subMaskCount.append(len(data[itr]["regions"]))
    print("\nDict size: ", len(file_bbs))
    
    for itr in file_bbs:
        num_masks = itr.split("*")
        to_save_folder = os.path.join(source_folder, num_masks[0])
        mask_folder = os.path.join(to_save_folder, "masks")
        mask = np.zeros((MASK_WIDTH, MASK_HEIGHT))
        try:
            arr = np.array(file_bbs[itr])
        except:
            print("Not found:", itr)
            continue
        count += 1
        cv2.fillPoly(mask, [arr], color=(255))
        if len(num_masks) > 1:
            cv2.imwrite(os.path.join(
                mask_folder, itr.replace("*", "_") + ".png"), mask)
        else:
            cv2.imwrite(os.path.join(mask_folder, itr + ".png"), mask)
    print("Images saved:", count)
print(subMaskCount)

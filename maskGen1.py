import os
import cv2
import json
import numpy as np
image_folder = os.path.join(os.getcwd(), "images")
json_folder = os.path.join(os.getcwd(), "json_folder")
count = 0  # Count of total images saved
file_bbs = {}  # Dictionary containing polygon coordinates for mask
MASK_WIDTH = 572
MASK_HEIGHT = 572
# Extract X and Y coordinates if available and update dictionary
def add_to_dict(data, itr, key):
    try:
        x_points = data[itr]["shape_attributes"]["all_points_x"]
        y_points = data[itr]["shape_attributes"]["all_points_y"]
    except:
        print("No BB. Skipping", key)
        return
    all_points = []
    for i, x in enumerate(x_points):
        all_points.append([x, y_points[i]])
    file_bbs[key] = all_points
subMaskCount = []
for filename in os.listdir(json_folder):
    with open(os.path.join(json_folder, filename)) as f:
        data = json.load(f)
    file_name_json = os.path.splitext(filename)[0]
    sub_count = 0  # Contains count of masks for a single ground truth image
    if len(data[itr]["regions"]) > 1:
        for _ in range(len(data["regions"])):
            key = file_name_json + "*" + str(sub_count + 1)
            add_to_dict(data, sub_count, key)
            sub_count += 1
    else:
        add_to_dict(data, 0, file_name_json)
    subMaskCount.append(len(data["regions"]))
print("\nDict size: ", len(file_bbs))
for file_name in os.listdir(image_folder):
    to_save_folder = os.path.join(image_folder, os.path.splitext(file_name)[0])
    mask_folder = os.path.join(to_save_folder, "masks")
    curr_img = os.path.join(image_folder, file_name)
    # make folders and copy image to new location
    os.mkdir(to_save_folder)
    os.mkdir(mask_folder)
    os.rename(curr_img, os.path.join(to_save_folder, file_name))
# For each entry in dictionary, generate mask and save in corresponding
# folder
for itr in file_bbs:
    num_masks = itr.split("*")
    to_save_folder = os.path.join(image_folder, num_masks[0])
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








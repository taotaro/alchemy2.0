import easyocr
from PIL import Image, ImageStat
import glob
import cv2
import time
import pandas as pd
import numpy as np
from collections import Counter
from YOLOv6 import run_obj_detection as run_object
from scipy.spatial import KDTree
import webcolors
import sys
from library import shopee_lib_2 as shopee
import os
from alive_progress import alive_bar

sys.path.insert(1, "YOLOv6")


time_str = time.strftime("%Y-%m-%d")


class ProcessImageData:
    def __init__(self, imageLoc):
        try:
            self.img = cv2.imread(imageLoc, 1)
        except:
            self.img = imageLoc
        self.manual_count = {}
        self.w, self.h, self.channels = self.img.shape
        self.total_pixels = self.w * self.h

    def count(self):
        for y in range(0, self.h):
            for x in range(0, self.w):
                RGB = (self.img[x, y, 2], self.img[x, y, 1], self.img[x, y, 0])
                if RGB in self.manual_count:
                    self.manual_count[RGB] += 1
                else:
                    self.manual_count[RGB] = 1

    def average_colour(self):
        red = 0
        green = 0
        blue = 0
        sample = 10
        for top in range(0, sample):
            red += self.number_counter[top][0][0]
            green += self.number_counter[top][0][1]
            blue += self.number_counter[top][0][2]

        average_red = red / sample
        average_green = green / sample
        average_blue = blue / sample
        return (average_red, average_green, average_blue)

    def twenty_most_common_colors(self):
        colors_list = []
        for rgb, value in self.number_counter:
            color_name = self.convert_rgb_to_names(rgb)
            colors_list.append(
                [color_name, value, ((float(value) / self.total_pixels) * 100)]
            )
        return colors_list

    def twenty_most_common(self):
        self.count()
        self.number_counter = Counter(self.manual_count).most_common(20)

    def detect(self):
        self.twenty_most_common()
        res = (0,0,0)
        try:
            self.percentage_of_first = float(self.number_counter[0][1]) / self.total_pixels
            res = self.average_colour()
        except:
            self.percentage_of_first = 0
        if self.percentage_of_first > 0.5:
            res = self.number_counter[0][0]
        return res

    def blur_check(self, image_path):
        i = image_path
        image_file = i

        # Doc anh tu file
        image_path = cv2.imread(image_file)
        gray = cv2.cvtColor(image_path, cv2.COLOR_BGR2GRAY)

        # Tinh toan muc do focus cua anh
        focus_measure = cv2.Laplacian(gray, cv2.CV_64F).var()
        return focus_measure

    def brightness_check(self, image_path):
        brightness_results = []
        input_image = Image.open(image_path)
        # 1st approach
        image = input_image.convert("L")
        stat = ImageStat.Stat(image)
        brightness_results.append(stat.mean[0])

        # 2nd approach
        stat = ImageStat.Stat(image)
        brightness_results.append(stat.rms[0])

        result = sum(brightness_results) / 2

        return result

    def pixel_difference_width(self, image, start_pixel, end_pixel, height, step=1):
        is_border = False
        for pixel in range(start_pixel, end_pixel, step):
            pixel1_coordinates = [pixel, int(height / 2)]
            pixel2_coordinates = [pixel + step, int(height / 2)]
            (b1, g1, r1) = image[pixel1_coordinates[0], pixel1_coordinates[1]]
            (b2, g2, r2) = image[pixel2_coordinates[0], pixel2_coordinates[1]]
            if b1 != b2 or g1 != g2 or r1 != r2:
                for j in range(int(height / 2), int(height / 1.25)):
                    pixel3_coordinates = [pixel1_coordinates[0], j]
                    pixel4_coordinates = [pixel2_coordinates[0], j + 1]
                    (b1, g1, r1) = image[pixel3_coordinates[0], pixel3_coordinates[1]]
                    (b2, g2, r2) = image[pixel4_coordinates[0], pixel4_coordinates[1]]
                    if b1 != b2 or g1 != g2 or r1 != r2:
                        is_border = True
                    else:
                        is_border = False
                        break
                if is_border:
                    break
        return is_border

    def pixel_difference_height(self, image, start_pixel, end_pixel, width, step=1):
        is_border = False
        for pixel in range(start_pixel, end_pixel, step):
            pixel1_coordinates = [int(width / 2), pixel]
            pixel2_coordinates = [int(width / 2), pixel + step]
            (b1, g1, r1) = image[pixel1_coordinates[0], pixel1_coordinates[1]]
            (b2, g2, r2) = image[pixel2_coordinates[0], pixel2_coordinates[1]]

            if b1 != b2 or g1 != g2 or r1 != r2:
                for j in range(int(width / 2), int(width / 1.25)):
                    pixel3_coordinates = [j + 1, pixel1_coordinates[1]]
                    pixel4_coordinates = [j + 1, pixel2_coordinates[1]]
                    (b1, g1, r1) = image[pixel3_coordinates[0], pixel3_coordinates[1]]
                    (b2, g2, r2) = image[pixel4_coordinates[0], pixel4_coordinates[1]]
                    if b1 != b2 or g1 != g2 or r1 != r2:
                        is_border = True
                    else:
                        is_border = False
                        break
                if is_border:
                    break
        return is_border

    def border_check(self, image_path):
        image = cv2.imread(image_path)
        width, height = image.shape[:2]
        left_side = self.pixel_difference_width(image, 1, int(width / 4), height)
        if not left_side:
            return 0
        right_side = self.pixel_difference_width(
            image, width - 1, int(width * 0.75), height, step=-1
        )
        if not right_side:
            return 0
        upper_side = self.pixel_difference_height(image, 1, int(height / 4), width)
        if not upper_side:
            return 0
        down_side = self.pixel_difference_height(
            image, height - 1, int(width * 0.75), width, step=-1
        )
        if (int(left_side) + int(right_side) + int(upper_side) + int(down_side)) >= 4:
            return 1
        else:
            return 0

    def check_contrast(self, image_path):
        i = image_path
        # read image
        img = cv2.imread(i)

        # convert to LAB color space
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

        # separate channels
        L, A, B = cv2.split(lab)

        # compute minimum and maximum in 5x5 region using erode and dilate
        kernel = np.ones((5, 5), np.uint8)
        min = cv2.erode(L, kernel, iterations=1)
        max = cv2.dilate(L, kernel, iterations=1)

        # convert min and max to floats
        min = min.astype(np.float64)
        max = max.astype(np.float64)

        # compute local contrast
        contrast = (max - min) / (max + min)

        # get average across whole image
        average_contrast = 100 * np.mean(contrast)
        return average_contrast

    def contrast_calc(self, image_path):
        img = cv2.imread(image_path)
        img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        contrast = img_grey.std()
        return contrast

    def convert_rgb_to_names(self, rgb_tuple):
        # a dictionary of all the hex and their respective names in css3
        css3_db = webcolors.CSS3_HEX_TO_NAMES
        names = []
        rgb_values = []
        for color_hex, color_name in css3_db.items():
            names.append(color_name)
            rgb_values.append(webcolors.hex_to_rgb(color_hex))

        kdt_db = KDTree(rgb_values)
        distance, index = kdt_db.query(rgb_tuple)
        return str(names[index])

    def text_extract(self, image_path):
        image_width, image_height = cv2.imread(image_path).shape[:2]
        total_num_pixels = image_width * image_height
        img = image_path
        img_1 = cv2.imread(image_path)

        reader = easyocr.Reader(["en"])
        output = reader.readtext(
            img, min_size=100, rotation_info=[90, 180, 270], width_ths=5
        )

        text_pixels = 0
        text_color = []
        # print(f"TOTAL PIXELS {totapip l_num_pixels}")
        for (bbox, text, prob) in output:
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = (int(top_left[0]), int(top_left[1]))
            top_right = (int(top_right[0]), int(top_right[1]))
            bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
            bottom_left = (int(bottom_left[0]), int(bottom_left[1]))

            cropped_image = img_1[
                top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]
            ]
            # cv2.imshow("crop", cropped_image)
            w, h = cropped_image.shape[:2]
            # print(f"text_pixels={text_pixels}, h= {h}, w={w}")
            text_pixels = text_pixels + (w * h)
            text_image = ProcessImageData(cropped_image)
            bg_color_of_text = text_image.detect()
            # print(bg_color_of_text)
            text_bg_color_name = text_image.convert_rgb_to_names(bg_color_of_text)
            colors = text_image.twenty_most_common_colors()
            for color in colors:
                if color[0] != text_bg_color_name:
                    text_color.append(color[0])
            # print(f"[INFO] {prob:.2f} = {text}")
        if text_pixels == 0:
            text_percentage_of_image = 0
        else:
            text_percentage_of_image = (text_pixels / total_num_pixels) * 100
        return output, text_percentage_of_image, text_color

    def slope(self, x1, y1, x2, y2):
        if x1 == x2:
            return 0
        slope = (y2 - y1) / (x2 - x1)
        theta = np.rad2deg(np.arctan(slope))
        return theta

    def orientation_calculation(self, image_path):
        img = cv2.imread(image_path)
        textImg = img.copy()

        small = cv2.cvtColor(textImg, cv2.COLOR_BGR2GRAY)

        # find the gradient map
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        grad = cv2.morphologyEx(small, cv2.MORPH_GRADIENT, kernel)

        # Binarize the gradient image
        _, bw = cv2.threshold(grad, 0.0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # connect horizontally oriented regions
        # kernal value (9,1) can be changed to improved the text detection
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1))
        connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)

        # using RETR_EXTERNAL instead of RETR_CCOMP
        # _ , contours, hierarchy = cv2.findContours(connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        contours, hierarchy = cv2.findContours(
            connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
        )  # opencv >= 4.0

        mask = np.zeros(bw.shape, dtype=np.uint8)
        # cumulative theta value
        cummTheta = 0
        # number of detected text regions
        ct = 0
        for idx in range(len(contours)):
            x, y, w, h = cv2.boundingRect(contours[idx])
            mask[y : y + h, x : x + w] = 0
            # fill the contour
            cv2.drawContours(mask, contours, idx, (255, 255, 255), -1)
            # ratio of non-zero pixels in the filled region
            r = float(cv2.countNonZero(mask[y : y + h, x : x + w])) / (w * h)

            # assume at least 45% of the area is filled if it contains text
            if r > 0.45 and w > 8 and h > 8:
                # cv2.rectangle(textImg, (x1, y), (x+w-1, y+h-1), (0, 255, 0), 2)

                rect = cv2.minAreaRect(contours[idx])
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(textImg, [box], 0, (0, 0, 255), 2)

                # we can filter theta as outlier based on other theta values
                # this will help in excluding the rare text region with different orientation from ususla value
                theta = self.slope(box[0][0], box[0][1], box[1][0], box[1][1])
                cummTheta += theta
                ct += 1

        # find the average of all cumulative theta value
        if ct == 0:
            orientation = 0
        else:
            orientation = cummTheta / ct
        # print("Image orientation in degrees: ", orientation)
        return orientation


def get_images_data(path):
    images_data = {
        "ID_and_Image_Number": [],
        "Brightness": [],
        "Background_Color": [],
        "Closest Color Name": [],
        "20 common colors": [],
        "Blurriness": [],
        "Contrast (Michelson)": [],
        "Contrast": [],
        "Text": [],
        "Text Covered Area": [],
        "Text colors": [],
        "Angle": [],
        "Pixels (Height, Width)": [],
        "Borders exist": [],
    }

    images = glob.glob(f"{path}/*.jpg")
    # print(len(images))
    for image in images:
        name = image.replace(".jpg", "")
        width, height = cv2.imread(image).shape[:2]
        height_and_width = [height, width]
        process_image = ProcessImageData(image)
        bg_color = process_image.detect()
        colors = process_image.twenty_most_common_colors()
        brightness_result = process_image.brightness_check(image)
        contrast_res_v1 = process_image.check_contrast(image)
        blur_res = process_image.blur_check(image)
        contrast_res_v2 = process_image.contrast_calc(image)
        closest_name = process_image.convert_rgb_to_names(bg_color)
        border = process_image.border_check(image)
        image_text, text_covered_area, text_colors = process_image.text_extract(image)
        angle = process_image.orientation_calculation(image)

        images_data["Closest Color Name"].append(closest_name)
        images_data["20 common colors"].append(colors)
        images_data["ID_and_Image_Number"].append(
            name.split("/")[-1] + name.split("-number")[0]
        )
        images_data["Brightness"].append(brightness_result)
        images_data["Background_Color"].append(bg_color)
        images_data["Blurriness"].append(blur_res)
        images_data["Contrast (Michelson)"].append(contrast_res_v1)
        images_data["Contrast"].append(contrast_res_v2)
        images_data["Text"].append(image_text)
        images_data["Text Covered Area"].append(text_covered_area)
        images_data["Text colors"].append(text_colors)
        images_data["Angle"].append(angle)
        images_data["Pixels (Height, Width)"].append(height_and_width)
        images_data["Borders exist"].append(border)
        # for i in images_data.keys():
        #     print(f"{i} ==== {len(images_data[i])}")

    return pd.DataFrame(images_data)


def run_image_processing(image_path):
    images_data_file = get_images_data(image_path)
    images_data_file.to_csv(f"{image_path}/images_features.csv")

    # images = glob.glob(f"{image_path}/*.jpg")
    # dict_image_content = {}
    # 
    # for image in images:
    #     print(f"Detecting {image}")
    #     run_object.args["weights"] = "YOLOv6/weights/yolov6n.pt"
    #     run_object.args["yaml"] = "YOLOv6/data/coco.yaml"
    #     run_object.args["font"] = "YOLOv6/yolov6/utils/Arial.ttf"
    #     run_object.args["source"] = image
    #     dict_image_content = run_object.run_object_detection()

    #     image_contents = pd.DataFrame(dict_image_content)
    #     image_contents.to_csv(f"{image_path}/images_objects.csv")

    #     result = pd.concat([images_data_file, image_contents], axis=1)
    #     result.to_csv(f"{image_path}/image_result_data.csv")


if __name__ == "__main__":
    category_list, subcategory_list = shopee.category_tree_search()
    for category in category_list:
        keyword = category['name']
        path = shopee.create_folder(keyword)
        image_path = os.path.join(path, "images")
        shopee.create_folder(f"{keyword}/images")
        run_image_processing(image_path)

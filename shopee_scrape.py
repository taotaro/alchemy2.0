import logging
import time
import os
import sys
import pandas as pd
import glob
from library import constants
from library import shopee_lib_2 as shopee
from library.product_class import Product
from library import image_lib as img
from library import shopee_class
import options
import traceback
from alive_progress import alive_bar

time_str = time.strftime("%Y-%m-%d")
logging.basicConfig(filename=f"logs/run-{time_str}.log", level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")

def query_yes_no(question, default="yes"):
    # Ask a yes/no question via raw_input() and return their answer.

    # "question" is a string that is presented to the user.
    # "default" is the presumed answer if the user just hits <Enter>.
    #         It must be "yes" (the default), "no" or None (meaning
    #         an answer is required of the user).

    # The "answer" return value is True for "yes" or False for "no".
    
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


def scraper():
    # logs to mark starting time
    start_time = time.time()
    logging.info("Getting general information: Start...")

    # get category and subcategory names list
    category_list, subcategory_list = shopee.category_tree_search()
    for category in category_list:
        # search keyword with category names
        keyword = category['name']
        print(f"Searching {keyword}")
        logging.info(f"Searching {keyword}")
        df_result, json_result = shopee.global_search(keyword)

        # arrange saved files
        path = shopee.create_folder(keyword)
        csv_path = shopee.create_file(time_str + keyword.replace(" ", "_"), "csv", path)
        json_path = shopee.create_file(time_str + keyword.replace(" ", "_"), "json", path)
        df_result.to_csv(csv_path)
        shopee.to_json(json_path, json_result)
        shopee_class.to_db(df_result)
        logging.info(f"{keyword} saved in {path}")

        for subcategory in subcategory_list:
            # search matching subcategories in the categories
            if subcategory['parent_catid'] == category['catid']:
                keyword_sub = subcategory['name']
                print(f"Searching {keyword_sub}")
                logging.info(f"Searching {keyword_sub}")
                df_result_sub, json_result_sub = shopee.global_search(keyword_sub)

                # arrange saved files and folders
                path_sub = shopee.create_folder(keyword_sub, f"data/{keyword}")
                csv_path_sub = shopee.create_file(time_str + keyword_sub.replace(" ", "_"), "csv", path_sub)
                json_path_sub = shopee.create_file(time_str + keyword_sub.replace(" ", "_"), "json", path_sub)
                df_result_sub.to_csv(csv_path_sub)
                shopee.to_json(json_path_sub, json_result_sub)
                shopee_class.to_db(df_result_sub)
                logging.info(f"{keyword_sub} saved in {path_sub}")

    # logs to mark ending time
    logging.info("Getting general information: done!")
    logging.info(f"--- {time.time() - start_time} seconds for general information ---")


def download():
    # logs to mark starting time
    start_time = time.time()
    logging.info("Getting images: Start...")

    main_path = os.path.join(os.getcwd(), "data")
    csv_files = glob.glob(f"{main_path}/*/*.csv")
    for file in csv_files:
        print(f"File retrieved: {file}")
        folder = os.path.dirname(file)
        print(f"Folder retrieved: {folder}")
        shopee.download_images(file, folder)

    csv_files_sub = glob.glob(f"{main_path}/*/*/*.csv")
    for file_sub in csv_files_sub:
        print(f"File retrieved: {file_sub}")
        folder_sub = os.path.dirname(file_sub)
        print(f"Folder retrieved: {folder_sub}")
        shopee.download_images(file_sub, folder_sub)

    # logs to mark ending time
    logging.info("Getting images: done!")
    logging.info(f"--- {time.time() - start_time} seconds for images ---")


def upload():
    # logs to mark starting time
    start_time = time.time()
    logging.info("Uploading images: Start...")

    main_path = os.path.join(os.getcwd(), "data")
    csv_files = glob.glob(f"{main_path}/*/*.csv")
    for file in csv_files:
        print(f"File retrieved: {file}")
        folder = os.path.dirname(file)
        print(f"Folder retrieved: {folder}")
        shopee.upload_images(file, folder)

    csv_files_sub = glob.glob(f"{main_path}/*/*/*.csv")
    for file_sub in csv_files_sub:
        print(f"File retrieved: {file_sub}")
        folder_sub = os.path.dirname(file_sub)
        print(f"Folder retrieved: {folder_sub}")
        shopee.upload_images(file_sub, folder_sub)

    # logs to mark ending time
    logging.info("Uploading images: done!")
    logging.info(f"--- {time.time() - start_time} seconds for images ---")


def process():
    main_path = os.path.join(os.getcwd(), "data")
    image_folders = glob.glob(f"{main_path}/*/images/")
    for folder in image_folders:
        print(f"Folder: {folder}")
        img.run_image_processing(folder)

    # image_folders_sub = glob.glob(f"{main_path}/*/*/images/")
    # for folder_sub in image_folders_sub:
    #     print(f"{folder_sub}")
    #     img.run_image_processing(folder_sub)


if __name__ == "__main__":
    # choose modes from cmd line input
    # input_scrape = query_yes_no("Scrape?")
    # input_download = query_yes_no("Download?")
    # input_process = query_yes_no("Process?")

    # choose modes from options.py file
    input_scrape = options.INPUT_SCRAPE
    input_download = options.INPUT_DOWNLOAD
    input_process = options.INPUT_PROCESS

    if input_scrape:
        try:
            shopee_class.init_db()
            scraper()
        except:
            print(f"SCRAPER FAILED\n{traceback.format_exc()}")
        shopee_class.discon_db()
    else:
        print("No scaper")

    if input_download:
        try:
            download()
        except:
            print(f"DOWNLOAD FAILED\n{traceback.format_exc()}")
    else:
        print("No download")

    if input_process:
        try:
            process()
        except:
            print(f"PROCESS FAILED\n{traceback.format_exc()}")
    else:
        print("No process")

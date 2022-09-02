import csv
import logging
import time
import os
import pandas as pd
from library import constants
from library import shopee_lib_2 as shopee
from library.product_class import Product

time_str = time.strftime("%Y-%m-%d")
logging.basicConfig(filename=f"logs/run-{time_str}.log", level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")


def main():
    # logs to mark starting time
    start_time = time.time()
    logging.info("Getting general information: Start...")
    
    # # scrape using keyword global search
    # keyword = "pet food products"
    # df_result, json_result = shopee.global_search(keyword)

    # # arrange saved files
    # path = shopee.create_folder(keyword)
    # csv_path = shopee.create_file(time_str + keyword.replace(" ", "_"), "csv", path)
    # json_path = shopee.create_file(time_str + keyword.replace(" ", "_"), "json", path)
    # df_result.to_csv(csv_path)
    # shopee.to_json(json_path, json_result)

    category_list, subcategory_list = shopee.category_tree_search()
    for category in subcategory_list:
        keyword = category['name']
        print(f"Searching {keyword}")
        df_result, json_result = shopee.global_search(keyword)

        # arrange saved files
        path = shopee.create_folder(keyword)
        csv_path = shopee.create_file(time_str + keyword.replace(" ", "_"), "csv", path)
        json_path = shopee.create_file(time_str + keyword.replace(" ", "_"), "json", path)
        df_result.to_csv(csv_path)
        shopee.to_json(json_path, json_result)
        
        # download images
        shopee.download_images(csv_path, path)

    # logs to mark ending time
    logging.info("Getting general information: done!")
    logging.info(f"--- {time.time() - start_time} seconds for general information ---")

if __name__ == "__main__":
    main()
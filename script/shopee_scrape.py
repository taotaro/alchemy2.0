import library.shopee_lib as shopee
import logging
import time
import os
from library.product_class import Product
from library import constants
import library.image_lib as image


time_str = time.strftime("%Y-%m-%d")
logging.basicConfig(filename=f"run-{time_str}.log", level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")


if __name__ == "__main__":
    start_time_all = time.time()
    json_list = []
    result = []
    search_mode = constants.MODE_OF_SEARCH

    if search_mode == 1:  # 1 is scrapping using keyword global search
        keyword = "pet products"
        limit_items = "60"
        logging.info("Getting general information: Start...")
        start_time_general = time.time()
        saving_path = shopee.get_global_search(keyword)
        logging.info("Getting general information: done!")
        if constants.PRODUCT_PAGE_SCRAPE_MODE == 1:
            shopee.download_images(saving_path, category_or_keyword=constants.KEYWORD)
            Product(saving_path, keyword)
            image.run_image_processing()
        logging.info("--- %s seconds for general information ---" % (time.time() - start_time_general))

    elif search_mode == 2: # 2 is scrapping using categories search
        logging.info("Getting general information: Start...")
        start_time_general = time.time()
        saving_path, saved_sub_category_names = shopee.get_category_search(constants.CATEGORY_NAME, sub_cat_choice=-3)
        logging.info("--- %s seconds for general information ---" % (time.time() - start_time_general))
        logging.info("Getting general information: done!")
        if constants.PRODUCT_PAGE_SCRAPE_MODE == 1:
            for sub_cat in saved_sub_category_names:
                Product(saving_path, sub_cat)
            shopee.download_images(saving_path, start=0) # start is resume point, to restart in case of crush/block
            image.run_image_processing()

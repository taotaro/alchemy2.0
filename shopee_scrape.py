import logging
import time
from library import constants
# from library import image_lib as image
from library import shopee_lib as shopee
from library.product_class import Product

time_str = time.strftime("%Y-%m-%d")
logging.basicConfig(filename=f"run-{time_str}.log", level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")


def main():
    search_mode = constants.MODE_OF_SEARCH

    # logs to mark starting time
    start_time = time.time()
    logging.info("Getting general information: Start...")
    
    # 1 is scrapping using keyword global search
    if search_mode == 1: 
        keyword = "pet products"
        saved_path = shopee.get_global_search(keyword)
        #if product page needs to be scraped        
        if constants.PRODUCT_PAGE_SCRAPE_MODE:
            shopee.download_images(saved_path, category_or_keyword=constants.KEYWORD)
            Product(saved_path, keyword)
            # image.run_image_processing()

    # 2 is scrapping using categories search
    elif search_mode == 2: 
        saved_path, saved_sub_category_names = shopee.get_category_search(constants.CATEGORY_NAME, sub_cat_choice=-3)
        #if product page needs to be scraped  
        if constants.PRODUCT_PAGE_SCRAPE_MODE:
            for sub_cat in saved_sub_category_names:
                Product(saved_path, sub_cat)
            shopee.download_images(saved_path, start=0) # start is resume point, to restart in case of crush/block
            # image.run_image_processing()

    # logs to mark ending time
    logging.info("Getting general information: done!")
    logging.info(f"--- {time.time() - start_time} seconds for general information ---")

if __name__ == "__main__":
    main()
import requests
import logging
import pandas as pd
import time
import json
from ast import literal_eval
import traceback
import random
import constants
import os
import glob
time_str = time.strftime("%Y-%m-%d")
logging.basicConfig(filename=f"run-{time_str}.log", level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")

def get_product_list_max_pg(keyword):
    '''
    This function returns the number of pages in search
    Parameters:
        - keyword: desired product name
    '''
    response = api_product_list(keyword)
    list_page = response.json()
    num_pages = int(list_page["total_count"]) / 60
    return int(num_pages)


def get_category_list_max_pg(sub_category_id, page_type='search', scenario="PAGE_CATEGORY"):
    '''
    This function returns the number of pages in category
    Parameters:
        - page_type: type of page (search or collection, where search is for category and collection is
                 for collections in category)
        - scenario: type of api (collection or collection)
        - sub_category_id: desired subcategory
    '''
    response = api_category_list(sub_category_id, 0, scenario=scenario, page_type=page_type)
    cat_page = response.json()
    num_pages = int(cat_page["total_count"]) / 60
    return int(num_pages)


def api_category_names():
    '''
    This function calls the shopee API to get the complete list of all category names in shopee
    '''
    url = "https://shopee.sg/api/v4/pages/get_category_tree"
    payload = {}
    headers = {
        'Cookie': 'REC_T_ID=1eebbf57-fb70-11ec-aa39-e642a9121c0f; SPC_F=d2l0o7UqUeWsiM7TOmg6XfWVrmvEOK0u; SPC_R_T_ID=BOoN7lckySNuyWvnjuWgVxB24aHhrbECNT3qHWQ9zMsVGC706kY2zSUgjGj93XjBZcsT2x+gJ2A+gHLRRhLBqJeyicAaRA2JEudV2FNTj1Dbwr/xRpg9wkBPnT7C85sHC6Lz7UZhoPtNu01ZNkYs3YbGD3UpsDGeIOY+A9gL52U=; SPC_R_T_IV=TXpMYnhvb1A3TWZEN3hKSw==; SPC_SI=agC8YgAAAAB4UzJPU2VxZvtu8gAAAAAAd1JNM0xmUkY=; SPC_T_ID=BOoN7lckySNuyWvnjuWgVxB24aHhrbECNT3qHWQ9zMsVGC706kY2zSUgjGj93XjBZcsT2x+gJ2A+gHLRRhLBqJeyicAaRA2JEudV2FNTj1Dbwr/xRpg9wkBPnT7C85sHC6Lz7UZhoPtNu01ZNkYs3YbGD3UpsDGeIOY+A9gL52U=; SPC_T_IV=TXpMYnhvb1A3TWZEN3hKSw=='
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        return response
    except Exception as e:
        logging.error(traceback.format_exc())
        return


def api_category_list(child_id, newest, limit="60", scenario="PAGE_CATEGORY", page_type='search', order="desc"):
    '''
    This function calls the one of the shopee API to get product list from specific category or collection
    Parameters:
        - page_type: type of page (search or collection, where search is for category and collection is
                 for collections in category)
        - scenario: type of api (collection or collection)
        - child_id: desired subcategory id
        - limit_items: return number of items from API, tested maximum number is 150
        - newest: page number
        - scenario: searching method
    '''

    url = f"https://shopee.sg/api/v4/search/search_items?by=relevancy&limit={limit}&match_id={child_id}&newest={newest}&order={order}&page_type={page_type}&scenario={scenario}&version=2"
    payload = {}
    headers = {
        'Cookie': 'REC_T_ID=1eebbf57-fb70-11ec-aa39-e642a9121c0f; SPC_F=d2l0o7UqUeWsiM7TOmg6XfWVrmvEOK0u; SPC_R_T_ID=BOoN7lckySNuyWvnjuWgVxB24aHhrbECNT3qHWQ9zMsVGC706kY2zSUgjGj93XjBZcsT2x+gJ2A+gHLRRhLBqJeyicAaRA2JEudV2FNTj1Dbwr/xRpg9wkBPnT7C85sHC6Lz7UZhoPtNu01ZNkYs3YbGD3UpsDGeIOY+A9gL52U=; SPC_R_T_IV=TXpMYnhvb1A3TWZEN3hKSw==; SPC_SI=agC8YgAAAAB4UzJPU2VxZvtu8gAAAAAAd1JNM0xmUkY=; SPC_T_ID=BOoN7lckySNuyWvnjuWgVxB24aHhrbECNT3qHWQ9zMsVGC706kY2zSUgjGj93XjBZcsT2x+gJ2A+gHLRRhLBqJeyicAaRA2JEudV2FNTj1Dbwr/xRpg9wkBPnT7C85sHC6Lz7UZhoPtNu01ZNkYs3YbGD3UpsDGeIOY+A9gL52U=; SPC_T_IV=TXpMYnhvb1A3TWZEN3hKSw=='
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
    except Exception as e:
        time.sleep(20)
        response = requests.request("GET", url, headers=headers, data=payload)
        logging.error(traceback.format_exc())

    return response


def api_get_collections_id(cat_id):
    '''
    This function calls the one of the shopee API to get id of the all collections in category
    Parameters:
        -cat_id: id of category which contains desired collections
    '''
    url = f"https://shopee.sg/api/v4/pages/get_popular_collection?catid={cat_id}"
    payload = {}
    headers = {'Cookie': 'REC_T_ID=1eebbf57-fb70-11ec-aa39-e642a9121c0f; SPC_F=d2l0o7UqUeWsiM7TOmg6XfWVrmvEOK0u; SPC_R_T_ID=BOoN7lckySNuyWvnjuWgVxB24aHhrbECNT3qHWQ9zMsVGC706kY2zSUgjGj93XjBZcsT2x+gJ2A+gHLRRhLBqJeyicAaRA2JEudV2FNTj1Dbwr/xRpg9wkBPnT7C85sHC6Lz7UZhoPtNu01ZNkYs3YbGD3UpsDGeIOY+A9gL52U=; SPC_R_T_IV=TXpMYnhvb1A3TWZEN3hKSw==; SPC_SI=ggD2YgAAAAByczZQTUNkcU8WiAAAAAAAZ2VEbktOQWs=; SPC_T_ID=BOoN7lckySNuyWvnjuWgVxB24aHhrbECNT3qHWQ9zMsVGC706kY2zSUgjGj93XjBZcsT2x+gJ2A+gHLRRhLBqJeyicAaRA2JEudV2FNTj1Dbwr/xRpg9wkBPnT7C85sHC6Lz7UZhoPtNu01ZNkYs3YbGD3UpsDGeIOY+A9gL52U=; SPC_T_IV=TXpMYnhvb1A3TWZEN3hKSw=='
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        return response
    except:
        logging.info("Get Collections ID API doesn't work")
        logging.error(traceback.format_exc())
        return


def api_product_list(keyword, limit_items="60", newest="0", order="desc", page_type="search", version="2",
                     scenario="PAGE_GLOBAL_SEARCH"):
    '''
    This function calls one of the shopee API to get product list from global search
    Parameters:
        - keyword: desired search item
        - limit_items: return number of items from API, tested maximum number is 150
        - newest: page number
        - order: asc or desc
        - page_type: type of page
        - version: version of api, default is 2
        - scenario: uncertain what this is
    '''

    URL = "https://shopee.sg/api/v4/search/search_items"

    querystring = {
        "by": "relevancy",
        "keyword": keyword,
        "limit": f"{limit_items}",
        "newest": f"{newest}",
        "order": order,
        "page_type": page_type,
        "scenario": scenario,
        "version": version}

    payload = ""
    headers = {
        "cookie": "SPC_F=vC3PSL4kgYTVJBlxCaouUO97FGtq5DnT; REC_T_ID=24edd776-fb71-11ec-a126-b47af14a2e80; "
                  "SPC_R_T_ID=KM2EWNMiOfEZ7WPjqWR0BFO8w8nBqMhvhbFAfODballvF%2BMUCNVI0JPbw04EZqgNfoWqjbUPSFk5C"
                  "%2BleV9HteBl3fcCQDXP1suSNebes0A7nmte5cln2gBPOiaAGPUBMpFm5vrCtXMzt1cZEahjoTxanNhOLfP04v3fTgirEZqI%3D; SPC_R_T_IV=NFg0T0pTQlBoYVB0QjJNbg%3D%3D; SPC_T_ID=KM2EWNMiOfEZ7WPjqWR0BFO8w8nBqMhvhbFAfODballvF%2BMUCNVI0JPbw04EZqgNfoWqjbUPSFk5C%2BleV9HteBl3fcCQDXP1suSNebes0A7nmte5cln2gBPOiaAGPUBMpFm5vrCtXMzt1cZEahjoTxanNhOLfP04v3fTgirEZqI%3D; SPC_T_IV=NFg0T0pTQlBoYVB0QjJNbg%3D%3D; SPC_SI=agC8YgAAAABKVEN5RTVzTFoR8wAAAAAAWEZDTVFVYXo%3D"}

    try:
        response = requests.request("GET", URL, data=payload, headers=headers, params=querystring)
        return response
    except:
        # Return something
        logging.info("API doesn't work")
        logging.error(traceback.format_exc())
        return


def get_category_names(output_file_path=constants.PRODUCT_LIST_CATEGORY_PATH):
    '''
    This function calls the shopee API to get category names and saves it as .csv file
    Parameters:
        - output_file_name: name of the output .csv file that will contain category names
    '''

    column_name = {}
    response = api_category_names()
    category_data = response.json()
    category_name = ''
    for category in category_data['data']['category_list']:
        cat_child = []
        category_name = category["name"]
        category_id = category["catid"]
        for children in category["children"]:
            cat_child.append([children["name"], children["catid"]])
        column_name[category_name] = [[category_id, cat_child]]

    categories = pd.DataFrame(column_name)
    categories.to_csv(f"{output_file_path}/{time_str}-categories.csv")


def get_collection(collection_dict, category_name=constants.CATEGORY_NAME,
                            saving_name=constants.PRODUCT_LIST_FILE_TEMPLATE):
    '''
    This function gets all product listing from collections of category, and returns its saving paths
    and subcategories list that have been used
    '''
    cat_name = category_name.replace(" ", "_")
    directory = constants.PRODUCT_LIST_CATEGORY_FOLDER + f"/{cat_name}/empty"
    path = check_directory(directory, cat_name)
    saved_sub_categories = []
    for key, value in collection_dict.items():
        newest = 0  # newest is starting product to scrape
        shoppe_data_frame_cat = pd.DataFrame()
        json_general_raw = {}
        child_id = int(value)

        # getting number of pages
        num_pages = get_category_list_max_pg(child_id, scenario='PAGE_COLLECTION', page_type='collection') + 1
        result_tmp = []
        logging.info(num_pages)

        for page in range(num_pages):
            logging.info(f"Product Listing stage(collections): page - {page}")

            # increase newest each time to get new product listing
            if num_pages != 1:
                newest = page * 60
                time.sleep(0.2)
            print(f"Product Listing stage(collections): page - {page}")

            # calling api to get json of product listing (each response consists max only 60 products)
            response = api_category_list(child_id, newest, scenario='PAGE_COLLECTION', page_type='collection')
            collected_data = response.json()
            json_general_raw[f"{page}"] = [collected_data]

            # storing data of each product into list
            for product in collected_data['items']:
                # if statement to avoid misreading of data (otherwise from "\r" of string it will read new data/column)
                if "\r" in product['item_basic']['name']:
                    product['item_basic']['name'] = product['item_basic']['name'].replace("\r", " ")
                result_tmp.append(product)
        temp_df = pd.json_normalize(result_tmp)

        # updating dataframe to save all data/ append new 60 products to dataframe each time
        if shoppe_data_frame_cat.empty:
            shoppe_data_frame_cat = temp_df
        else:
            previous = shoppe_data_frame_cat
            shoppe_data_frame_cat = pd.concat([previous, temp_df])

        saved_sub_categories.append(key)

        # saving data into .csv and .json file
        with open(f'{path}/{time_str}-{key}-{constants.PRODUCT_LIST_FILE_RAW}.json', 'w') as raw:
            json.dump(json_general_raw, raw)
        shoppe_data_frame_cat.to_csv(f"{path}/{time_str}-{key}-{saving_name}.csv")
    return path, saved_sub_categories


def get_global_search(keyword=constants.KEYWORD, saving_name=constants.PRODUCT_LIST_FILE_TEMPLATE):
    '''
    This function scrapes product listing based on KEYWORD
    Parameters:
        - keyword: desired search term
        - saving_name: output .csv file name for general information of product listing
    '''
    # initialize variables
    collected_data = None
    newest = 0
    num_pages = get_product_list_max_pg(keyword)
    json_general_raw = {}
    json_list = []
    result = []
    k = keyword

    #checking directory for saving data
    directory = constants.PRODUCT_LIST_CATEGORY_FOLDER + f"/{k.replace(' ', '_')}/empty"
    path = check_directory(directory, keyword, path=constants.PRODUCT_LIST_SEARCH_FOLDER)

    if num_pages != 0:

        for page in range(num_pages):
            time.sleep(random.uniform(0.0, 3.0))

            # increase newest each time to get new product listing in each loop
            if num_pages != 1:
                newest = str(page * 60)
            else:
                newest = 0

            # calling api
            response = api_product_list(keyword, newest=newest)
            collected_data = response.json()
            json_general_raw[f"{page}"] = [collected_data]
            json_list.append(collected_data)

            # store product's data into list
            for product in collected_data['items']:
                result.append(product)

        # saving all data into .csv and .json
        shoppe_data_frame = pd.json_normalize(result)
        shoppe_data_frame["Combined"] = result
        with open(f'{path}/{time_str}-{constants.PRODUCT_LIST_FILE_RAW}.json', 'w') as raw:
            json.dump(json_general_raw, raw)
        shoppe_data_frame.to_csv(f"{path}/{time_str}-{saving_name}.csv")

        # deleting folder called "empty"
        os.rmdir(directory)
        return path
    else:
        logging.info("no pages, quitting")
        quit()


def check_directory(file_path, folder_name, path=constants.PRODUCT_LIST_CATEGORY_FOLDER):
    '''
    This function checks if provided directory exists or not, and creates that directory if it does not exist
    Parameters:
        - file_path: desired direcrory/file for existence check
        - folder_name: name of the folder which is gonna be created
        - path: path that exist and will be used to create new directory
    '''
    mode = 0o666
    print(file_path)
    if not os.path.isdir(file_path):
        os.makedirs(file_path, mode)
        path_to_create = path + f"/{folder_name}"
    else:
        path_to_create = path + f"/{folder_name}"
    path_to_create.replace(" ", "_")
    return path_to_create


def get_category_search(category_name=constants.CATEGORY_NAME, sub_cat_choice=5,
                        saving_name=constants.PRODUCT_LIST_FILE_TEMPLATE):
    '''
    This function generates a full list of products based on CATEGORY
    Parameters:
        - category_name: desired category name
        - sub_cat_choice: order number of subcategory under category that will be scraped (-1 is all subcategories, order start from 0)
        - saving_name: output .csv file name for general information
    '''

    collection_dict = {}
    cat_name = category_name.replace(" ", "_")
    category_name = category_name.replace("_", " ")
    directory = constants.PRODUCT_LIST_CATEGORY_FOLDER + f"/{cat_name}/empty"
    path = check_directory(directory, cat_name)
    saved_sub_categories = []

    # check if categories.csv file exist
    if not os.path.exists(f"{constants.PRODUCT_LIST_CATEGORY_PATH}/{time_str}-categories.csv"):
        get_category_names()

    # read file with category names, sub category and id
    category = pd.read_csv(f"{constants.PRODUCT_LIST_CATEGORY_PATH}/{time_str}-categories.csv")
    category_list = literal_eval(category[category_name][0])

    # iterate through each subcategory
    for sub_cat in category_list[1]:
        newest = 0
        shoppe_data_frame_cat = pd.DataFrame()
        json_general_raw = {}

        # -1: for scrapping all subcategories; -2:for scrapping main page of category; -3: for scrapping collections
        if sub_cat_choice != -1:
            if sub_cat_choice == -2 and sub_cat == category_list[1][-1]:
                sub_cat = [category_name, category_list[0]]
            elif sub_cat_choice == -3:
                if sub_cat == category_list[1][-1]:
                    collection = api_get_collections_id(category_list[0]).json()['data']["popular_collection_list"][1]["collection_list"]
                    for i in collection:
                        collection_dict[i["title"]] = i["collection_id"]
                    path, saved_sub_categories = get_collection(collection_dict)
                    return path, saved_sub_categories
                else:
                    continue
            elif sub_cat != category_list[1][sub_cat_choice]:
                continue

        child_id = int(sub_cat[1])

        # getting number of pages in specific subcategory
        num_pages = get_category_list_max_pg(child_id) + 1
        result_tmp = []
        logging.info(num_pages)

        # loop number of pages times to get all data
        for page in range(num_pages):
            logging.info(f"Product Listing stage: page - {page}")

            # increase newest each time to get new product listing in each loop
            if num_pages != 1:
                newest = page * 60
                time.sleep(0.2)
            print(f"Product Listing stage: page - {page}")

            # calling api to get data
            response = api_category_list(child_id, newest)
            collected_data = response.json()
            json_general_raw[f"{page}"] = [collected_data]

            # storing data of each product into list
            for product in collected_data['items']:

                # if statement to avoid misreading of data (otherwise from "\r" of string it will read new data/column)
                if "\r" in product['item_basic']['name']:
                    product['item_basic']['name'] = product['item_basic']['name'].replace("\r", " ")

                result_tmp.append(product)
        temp_df = pd.json_normalize(result_tmp)

        # update dataframe to store all product
        if shoppe_data_frame_cat.empty:
            shoppe_data_frame_cat = temp_df
        else:
            previous = shoppe_data_frame_cat
            shoppe_data_frame_cat = pd.concat([previous, temp_df])

        # saving data
        saved_sub_categories.append(sub_cat[0])
        with open(f'{path}/{time_str}-{sub_cat[0]}-{constants.PRODUCT_LIST_FILE_RAW}.json', 'w') as raw:
            json.dump(json_general_raw, raw)
        shoppe_data_frame_cat.to_csv(f"{path}/{time_str}-{sub_cat[0]}-{saving_name}.csv")

    # deleting folder called "empty"
    os.rmdir(directory)
    return path, saved_sub_categories


def download_images(path, category_or_keyword=constants.CATEGORY_NAME, start=0):
    '''
  This function downloads locally images from provided category/keyword search
  Parameters:
    - path: directory where data of each sub category is saved
    - category_or_keyword: string that shows search method
    - start: resuming point (image number) if code crashes
  '''
    files = glob.glob(f"{path}/2022-07-29-Pet Grooming & Hygiene-product_list.csv")
    files = [f for f in files if time_str in f]
    path += "/Images/empty"
    check_directory(path, "Images")
    number_file = 0

    for file in files:
        number_file += 1
        print(f"Total = {len(files)}/file number - {number_file}")

        product_list = pd.read_csv(file, index_col=None)

        image_url = "https://cf.shopee.sg/file/"
        image_column = product_list["item_basic.images"]
        product_id_column = product_list["itemid"]
        number_products = len(image_column)

        for i in range(start, number_products):
            print(f"Current FILE = {number_file}|Total {number_products}; Currentt={i}")
            images = literal_eval(image_column[i])
            if type(images) is bool:
                continue

            product_id = product_id_column[i]
            try:
                response = requests.get(f"{image_url}{images[0]}", timeout=100)
                img_data = response.content
                print("got content")
            except Exception as e:
                time.sleep(20)
                response = requests.get(f"{image_url}{images[0]}", timeout=100)
                img_data = response.content
                logging.error(traceback.format_exc())
                print(traceback.format_exc())
                print("got content, but with problems")

            with open(f'{constants.PRODUCT_LIST_CATEGORY_FOLDER}/{category_or_keyword}/Images/{product_id}.jpg', 'wb') as handler:
                handler.write(img_data)

    os.rmdir(path)

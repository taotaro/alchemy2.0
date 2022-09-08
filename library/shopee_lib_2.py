import requests
import logging
import pandas as pd
import time
import json
from ast import literal_eval
import traceback
import random
from . import constants
import os
import glob
import oss2

time_str = time.strftime("%Y-%m-%d")
logging.basicConfig(
    filename=f"logs/run-{time_str}.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


def get_product_list_max_page(keyword):
    # '''
    # This function returns the number of pages in search
    # Parameters:
    #     - keyword: desired product name
    # '''
    response = api_product_list(keyword)
    list_page = response.json()
    num_pages = int(list_page["total_count"]) / 60
    return int(num_pages)


def get_category_list_max_page(
    sub_category_id, page_type="search", scenario="PAGE_CATEGORY"
):
    # '''
    # This function returns the number of pages in category
    # Parameters:
    #     - page_type: type of page (search or collection, where search is for category and collection is
    #              for collections in category)
    #     - scenario: type of api (collection or collection)
    #     - sub_category_id: desired subcategory
    # '''
    response = api_category_list(
        sub_category_id, 0, scenario=scenario, page_type=page_type
    )
    cat_page = response.json()
    num_pages = int(cat_page["total_count"]) / 60
    return int(num_pages)


def api_category_names():
    # '''
    # This function calls the shopee API to get the complete list of all category names
    # '''
    url = "https://shopee.sg/api/v4/pages/get_category_tree"
    payload = {}
    headers = {"Cookie": constants.COOKIE}
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        return response
    except Exception as e:
        logging.error(traceback.format_exc())
        return


def api_category_list(
    child_id,
    newest,
    limit="60",
    scenario="PAGE_CATEGORY",
    page_type="search",
    order="desc",
):
    # '''
    # This function calls the one of the shopee API to get product list from specific category or collection
    # Parameters:
    #     - page_type: type of page (search or collection, where search is for category and collection is
    #              for collections in category)
    #     - scenario: type of api (collection or collection)
    #     - child_id: desired subcategory id
    #     - limit_items: return number of items from API, tested maximum number is 150
    #     - newest: page number
    #     - scenario: searching method
    # '''
    url = f"https://shopee.sg/api/v4/search/search_items?by=relevancy&limit={limit}&match_id={child_id}&newest={newest}&order={order}&page_type={page_type}&scenario={scenario}&version=2"
    payload = {}
    headers = {"Cookie": constants.COOKIE}
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
    except Exception as e:
        time.sleep(20)
        response = api_category_list(child_id, newest, limit, scenario, page_type, order)
        logging.error(traceback.format_exc())

    return response


def api_get_collections_id(cat_id):
    # '''
    # This function calls the one of the shopee API to get id of the all collections in category
    # Parameters:
    #     -cat_id: id of category which contains desired collections
    # '''
    url = f"https://shopee.sg/api/v4/pages/get_popular_collection?catid={cat_id}"
    payload = {}
    headers = {"Cookie": constants.COOKIE}
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        return response
    except:
        logging.error(traceback.format_exc())
        return


def api_product_list(
    keyword,
    limit_items="60",
    newest="0",
    order="desc",
    page_type="search",
    version="2",
    scenario="PAGE_GLOBAL_SEARCH",
):
    # '''
    # This function calls one of the shopee API to get product list from global search
    # Parameters:
    #     - keyword: desired search item
    #     - limit_items: return number of items from API, tested maximum number is 150
    #     - newest: page number
    #     - order: asc or desc
    #     - page_type: type of page
    #     - version: version of api, default is 2
    #     - scenario: uncertain what this is
    # '''

    url = "https://shopee.sg/api/v4/search/search_items"

    querystring = {
        "by": "relevancy",
        "keyword": keyword,
        "limit": f"{limit_items}",
        "newest": f"{newest}",
        "order": order,
        "page_type": page_type,
        "scenario": scenario,
        "version": version,
    }

    payload = {}
    headers = {"Cookie": constants.COOKIE_1}

    try:
        response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
        return response
    except:
        # Return something
        logging.error(traceback.format_exc())
        return

def global_search(keyword):
    #initialize
    df_result = []
    json_result = {}
    # get number of pages for product search
    pages = get_product_list_max_page(keyword)

    if pages > 0:
        for page in range(pages):
            response = api_product_list(keyword, newest=page)
            products = response.json()['items']
            print(f"Page {page} - {len(products)} Items Found")
            for product in products:
                # remove unnecessary parts
                del product['item_basic']['deep_discount_skin']
                del product['item_basic']['add_on_deal_info']
                ts_product = {
                  "ts": time_str,
                  "product": product['item_basic']
                }
                df_result.append(ts_product)
                json_result[page] = [ts_product]
            print(f"Page {page} - Done")
    else:
        print("no pages found")

    df_result = pd.json_normalize(df_result)
    return df_result, json_result

# convert data to json and save
def to_json(path, result):
    with open(path, "w") as file:
        json.dump(result, file)

# find folder destination and create one if it doesn't exist
def create_folder(folder_name, parent_folder="data"):
    if " " in folder_name:
        folder_name = folder_name.replace(" ", "_")
    folder_path = os.path.join(os.getcwd(), parent_folder, folder_name)
    #if folder does not exist, create one
    if os.path.exists(folder_path):
        print(f"Directory existed: {folder_path}")
    else:
        try:
            os.makedirs(folder_path)
            print(f"Directory created: {folder_path}")
        except IsADirectoryError:
            print(f"Directory existed: {folder_path}")
        
    return folder_path


def create_file(filename, type, path=""):
    full_filename = filename + "." + type
    full_path = os.path.join(path, full_filename)
    return full_path

# get category names and the tree list
def category_tree_search():
    category_list = []
    subcategory_list = []

    response = api_category_names()
    categories = response.json()['data']['category_list']
    for category in categories:
        temp_parent = {
            "level": category['level'],
            "parent_catid": category['parent_catid'],
            "catid": category['catid'],
            "name": category['name'],
            "num_children": len(category['children'])
        }
        category_list.append(temp_parent)
        
        for child in category['children']:
            if child['children'] != None:
                num_children = len(child['children'])
            else:
                num_children = 0
            temp_child = {
                "level": child['level'],
                "parent_catid": child['parent_catid'],
                "catid": child['catid'],
                "name": child['name'],
                "num_children": num_children
            }
            subcategory_list.append(temp_child)
        
    return category_list, subcategory_list


def download_images(csv_path, path):
    try:
        file = pd.read_csv(csv_path)
    except:
        print(f"File not found - {csv_path}")
        return

    try:
        os.makedirs(f"{path}/images/")
    except Exception as e:
        print(f"Directory existed: {path}/images/")
    base_url = "https://cf.shopee.sg/file"

    if file["product.images"].any():
        for image_list in file['product.images']:
            images = literal_eval(image_list)

            for image in images:
                if os.path.exists(f"{path}/images/{image}.jpg"):
                    print(f"Image skipped - {image}")
                else:
                    image_url = f"{base_url}/{image}"
                    response = requests.get(image_url).content
                    try:
                        with open(f"{path}/images/{image}.jpg", "wb") as handler:
                            handler.write(response)
                            print(f"Image downloaded - {image}")
                    except Exception as e:
                        print(f"Image failed to download - {image}")
    else:
      print("No images")

    return


# def upload_images(csv_path, keyword):
#     file = pd.read_csv(csv_path)
#     base_url = "https://cf.shopee.sg/file"
#     auth = oss2.Auth(constants.OSS_ACCESS_ID, constants.OSS_SECRET_KEY)
#     bucket = oss2.Bucket(auth, constants.OSS_ENDPOINT, constants.OSS_BUCKET)

#     if file["product.images"]:
#         for image_list in file['product.images']:
#             images = literal_eval(image_list)

#             for image in images:
#                 image_url = f"{base_url}/{image}"
#                 response = requests.get(image_url).content
#                 try:
#                     bucket.put_object(f"{keyword}/{image}.jpg", response)
#                     print(f"Image uploaded - {image}")
#                 except Exception:
#                     print(f"Image failed to download - {image}")
#     else:
#       print("No images")

#     return
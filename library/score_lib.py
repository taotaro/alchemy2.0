import pandas as pd
import os
import re
import requests
import time
from bs4 import BeautifulSoup
import traceback
from . import constants

def get_shopee_id(url):
    # '''
    # This function retrieves the shop and product id from a shopee URL
    # '''
    shop_id = url.split(".")[-2]
    product_id = url.split(".")[-1].split("?")[0]
    return shop_id, product_id

def api_search_item(shop_id, product_id):
    # '''
    # This function calls a shopee API to get details on one product
    # '''

    url = f"https://shopee.sg/api/v4/item/get?shopid={shop_id}&itemid={product_id}"

    payload = {}
    headers = {"Cookie": constants.COOKIE_1}

    try:
        response = requests.request("GET", url, data=payload, headers=headers)
        return response.json()
    except:
        print(traceback.format_exc())
        return

def get_category_names(response):
    # '''
    # This function gets the categories name of a product from its response
    # '''
    category_folder = []
    categories = response['data']['fe_categories']

    for category in categories:
        cat_name = category['display_name']
        cat_folder = cat_name.replace(" ", "_")
        category_folder.append(cat_folder)
    
    return category_folder
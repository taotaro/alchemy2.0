import pandas as pd
import os
import re
import requests
import time
from bs4 import BeautifulSoup
import traceback
from . import constants
# import constants
from . import process_data_lib
import json
import oss2

auth=oss2.Auth(constants.ACCESS_KEY_ID, constants.ACCESS_KEY_SECRET)
bucket=oss2.Bucket(auth, constants.ENDPOINT, constants.BUCKET)

def get_shopee_id(url):
    # '''
    # This function retrieves the shop and product id from a shopee URL.
    # The shop id is the numbers after "i." and the product is after the shop id
    # 
    # Input: 
    #   - url: shopee link
    # Output:
    #   - shop_id: shopee shop id
    #   - product_id: shopee item/product id
    # '''
    shop_id = url.split(".")[-2]
    product_id = url.split(".")[-1].split("?")[0]
    return shop_id, product_id

def api_search_item(shop_id, product_id):
    # '''
    # This function calls a shopee API to get details on one product
    # 
    # Input: 
    #   - shop_id: shopee shop id
    #   - product_id: shopee item/product id    
    # Output:
    #   - response: website's successful 200 response
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

##read text files in oss bucket

def get_file_from_bucket(bucket, folder, category):
    for obj in oss2.ObjectIteratorV2(bucket, prefix=folder):
        #check if subfolder, if yes ignore
        if obj.is_prefix():
            continue
        else:
            filename=obj.key
            if re.search(category, filename):
                return bucket.get_object(filename)
              

def get_content_from_file(file):
    if file==None:
        print('no files found for category')
        return -1
    content=file.read()
    content_list=[]
    for lines in content.splitlines():
        line=lines.strip(b'\n')
        #convert from bytes to string
        line=line.decode('utf-8')
        content_list.append(line)
    return content_list


def score_product(product, sorted_features,title_related_columns, shopee_related_columns):
    weight=100
    score=0
    title_score=0
    shopee_score=0
    for feature in sorted_features:
        if feature=='Cluster' or feature not in product.columns:
            continue
        weight/=2
        value=product[feature]
        if feature in title_related_columns:
            title_score+=value*weight
        if feature in shopee_related_columns:
            shopee_score+=value*weight
        score+=value*weight
    
    return score, title_score, shopee_score

# def score_product_only_by_title(product, sorted_features,title_related_columns):
#     weight=100
#     score=0
#     for feature in sorted_features:
#         if feature=='Cluster' or feature not in product.columns:
#             continue
#         elif feature in title_related_columns:
            
#             weight/=2
#             value=product[feature]
#             print(feature, weight, value[0])
#             score+=value*weight
#         else:
#             continue
#     return score

# def score_product_only_by_shopee(product, sorted_features,shopee_related_columns):
#     weight=100
#     score=0
#     for feature in sorted_features:
#         if feature=='Cluster' or feature not in product.columns:
#             continue
#         elif feature in shopee_related_columns:
#             weight/=2
#             value=product[feature]
#             print(feature, weight, value)
#             score+=value*weight
#         else:
#            continue
#     return score


def get_score_of_product(url):
    ##### get product information from url
    shop_id, product_id = get_shopee_id(url)
    product_information = api_search_item(shop_id, product_id)
    data = product_information['data']
    #forward selection data only available to main categories 
    category = get_category_names(product_information)[0]
    print(category)

    ##### get processed product with bag of words
    product, title_related_columns, shopee_related_columns=process_data_lib.process_product_from_link(data, bucket, 'Bag_of_words/', category)

    ##### get sorted features for category by forward selection
    features=get_file_from_bucket(bucket, 'Forward_selection/', category)
    sorted_features=get_content_from_file(features)

    ##### final scoring of product
    score, title_score, shopee_score=score_product(product, sorted_features, title_related_columns, shopee_related_columns)
    # shopee_only=score_product_only_by_shopee(product, sorted_features, shopee_related_columns)
    # title_only=score_product_only_by_title(product, sorted_features, title_related_columns)
    return title_related_columns, shopee_related_columns, score, title_score, shopee_score


if __name__=='__main__':
    test_url='https://shopee.sg/NEXGARD-SPECTRA.AUTHENTIC.%E3%80%8B-i.253386617.4334047211?sp_atk=9584be10-ad35-4a62-9552-c117b1291458&xptdk=9584be10-ad35-4a62-9552-c117b1291458'
    title_col, shopee_col, score, title, shopee=get_score_of_product(test_url)
    print('Title_attributes: ', title_col[0:10])
    print('Shopee Attributes: ', shopee_col)
    print('Score:', score)
    print('Title: ', title)
    print('Shopee: ', shopee)
    # print('only t: ', c)
    # print('only s: ', d)



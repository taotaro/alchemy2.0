import pandas as pd
import os
import re
import requests
import time
from bs4 import BeautifulSoup
import traceback
# from . import constants
import constants
import process_data_lib
import json
import oss2

auth=oss2.Auth(constants.ACCESS_KEY_ID, constants.ACCESS_KEY_SECRET)
bucket=oss2.Bucket(auth, constants.ENDPOINT, constants.BUCKET)

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


def score_product(product, sorted_features):
    weight=100
    score=0
    for feature in sorted_features:
        if feature=='Cluster' or feature not in product.columns:
            continue
        weight/=2
        value=product[feature]
        score+=value*weight
    return score

def get_score_of_product(url):
    ##### get product information from url
    id=get_shopee_id(url)
    shop_id=id[0]
    product_id=id[1]
    product_information=api_search_item(shop_id, product_id)
    data=product_information['data']
    #forward selection data only available to main categories 
    category=get_category_names(product_information)[0]
    print(category)

    ##### get processed product with bag of words
    product=process_data_lib.process_product_from_link(data, bucket, 'Bag_of_words/', category)

    ##### get sorted features for category by forward selection
    features=get_file_from_bucket(bucket, 'Forward_selection/', category)
    sorted_features=get_content_from_file(features)

    ##### final scoring of product
    score=score_product(product, sorted_features)
    return score[0]




if __name__=='__main__':
    test_url='https://shopee.sg/Vention-Ethernet-Cable-Cat7-Lan-High-Speed-10Gbps-SFTP-RJ-45-Network-Cable-Patch-Cable-8m-10m-for-Laptop-PC-i.95236751.1578425947?sp_atk=533f4b97-0ce8-4eb0-8d9a-99fc000c4b59&xptdk=533f4b97-0ce8-4eb0-8d9a-99fc000c4b59'
    score=get_score_of_product(test_url)
    print(score)



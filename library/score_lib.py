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
# import process_data_lib
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
def get_content_from_csv_file(file):
    if file==None:
        print('no files found for category')
        return -1
    df=pd.read_csv(file)
    return df


def score_product(product, sorted_features,title_related_columns, shopee_related_columns):
    weight=100
    score=0
    title_score=0
    shopee_score=0
    # print(product)
    for feature in sorted_features:
        if feature=='Cluster' or feature not in product.columns:
            continue
        weight /= 2
        value=product[feature]
        if feature in title_related_columns:
            title_score+=value*weight
        if feature in shopee_related_columns:
            shopee_score+=value*weight
        score+=value*weight
    
    return score, title_score, shopee_score

def score_product_with_user_shopee_features(title_data_list, title_columns, user_shopee_data, sorted_features):
    weight = 100
    score = 0
    title_data=pd.DataFrame(title_data_list, columns=title_columns)
    # shopee_data=pd.DataFrame(user_shopee_data, columns=['Transparent_background', 'Wholesale', 'Bundle_deal', 'Verified', 'Free_shipping'])
    shopee_data = pd.DataFrame({
        'Transparent_background': user_shopee_data[0],
        'Wholesale': user_shopee_data[1],
        'Bundle_deal': user_shopee_data[2],
        'Verified': user_shopee_data[3],
        'Free_shipping': user_shopee_data[4]
    }, index = [0])
    frames = [title_data, shopee_data]
    # print(sorted_features)
    product = pd.concat(frames, axis=1)
    print(product)
    for feature in sorted_features:
        if feature not in product.columns:
            continue
        weight /= 2
        value = product[feature]
        score += value * weight

    return score

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
    product, title_related_columns, shopee_related_columns, title_data = process_data_lib.process_product_from_link(data, bucket, 'Bag_of_words/', category)
    title_data_list=title_data.values.tolist()
    # print(title_data_list)
    # test=pd.DataFrame(title_data_list, columns=title_related_columns)
    # print(test)
    ##### get sorted features for category by forward selection
    features = get_file_from_bucket(bucket, 'Forward_selection/', category)
    sorted_features = get_content_from_file(features)

    scores = get_file_from_bucket(bucket, 'Scores/', category)
    scores_csv = get_content_from_csv_file(scores)
    scores_list = scores_csv['Scores']
    max_score = max(scores_list)
    min_score = min(scores_list)

    ##### final scoring of product
    score, title_score, shopee_score = score_product(product, sorted_features, title_related_columns, shopee_related_columns)
    # shopee_only=score_product_only_by_shopee(product, sorted_features, shopee_related_columns)
    # title_only=score_product_only_by_title(product, sorted_features, title_related_columns)

    result = {
      'title_col': title_related_columns,
      'shopee_col': shopee_related_columns,
      'score': score[0],
      'title': title_score[0],
      'shopee': shopee_score[0],
<<<<<<< HEAD
      'max':max_score, 
      'min':min_score,
      'sorted_features':sorted_features,
      'title_data':title_data_list
=======
      'max': max_score, 
      'min': min_score,
      'sorted_features': sorted_features,
      'title_data': title_data
>>>>>>> 69a5eed (add new score)
    }

    return result


if __name__=='__main__':
    test_url='https://shopee.sg/NEXGARD-SPECTRA.AUTHENTIC.%E3%80%8B-i.253386617.4334047211?sp_atk=9584be10-ad35-4a62-9552-c117b1291458&xptdk=9584be10-ad35-4a62-9552-c117b1291458'
    result=get_score_of_product(test_url)
<<<<<<< HEAD
    print(result['score'], result['title'], result['shopee'])
    # new_shopee_features=pd.DataFrame({
    #     'Transparent_background': 1,
    #     'Wholesale':1,
    #     'Bundle_deal':1,
    #     'Verified':1,
    #     'Free_shipping':1
    # }, index=[0])
    new_shopee_features=[1,1,1,1,1]
    new_score=score_product_with_user_shopee_features(result['title_data'], result['title_col'], new_shopee_features, result['sorted_features'])
    print(new_score[0])
    print(result['sorted_features'])
    # print('only t: ', c)
    # print('only s: ', d)
=======
    new_shopee_features=[1,1,1,1,1]
    new_score=score_product_with_user_shopee_features(result['title_data'], new_shopee_features, result['sorted_features'])

>>>>>>> 69a5eed (add new score)



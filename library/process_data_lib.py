from re import L
from types import NoneType
import pandas as pd
import numpy as np
import string
from textblob import TextBlob
from nltk.corpus import stopwords
import os
import warnings
import file_read_lib
stop_words=set(stopwords.words('english'))
warnings.filterwarnings('ignore')

def get_title_length(title):
    words=sum([word.strip(string.punctuation).isalpha() for word in title.split()])
    title_length=int(words)

    #take max title length as 20 and min title length as 0 to scale length
    scaled_length=(title_length)/18
    return scaled_length

def check_if_brand_in_title(title, brand):
    #if brand column is na
    if (type(brand)==float and pd.isna(brand)) or type(brand)==NoneType:
        return 0
  
    if brand in title:
        return 1
    else:
        return 0

def get_mood_of_title(title):
    sentiment_score=TextBlob(str(title)).sentiment.polarity
    sentiment=np.select([sentiment_score<0, sentiment_score==0, sentiment_score>0], ['neg', 'neu', 'pos'])
    if sentiment=='neg':
        return 0
    elif sentiment=='pos':
        return 1
    else:
        return 0.5

def check_if_number_in_title(title):
    if any(char.isdigit() for char in title):
        return 1
    else:
        return 0

def get_title_related_data(title, brand, label, rating):
    df_title_related=pd.DataFrame({
        'Title_length':get_title_length(title),
        'Brand_in_title':check_if_brand_in_title(title, brand),
        'Mood_in_title': get_mood_of_title(title),
        'Label_in_title':int(label),
        'Rating':rating/5
    }, index=[0])
    return df_title_related

def check_if_transparent_background(background_image):
    if background_image!=0:
        return 1
    else:
        return 0

def get_shopee_related_data(background_image, wholesale, bundle_deal, verified_label, free_shipping):
    df_shopee_related=pd.DataFrame({
        'Transparent_backgound':check_if_transparent_background(background_image),
        'Wholesale':int(wholesale),
        'Bundle_deal':int(bundle_deal),
        'Verified':int(verified_label),
        'Free_shipping':int(free_shipping)
    }, index=[0])
    return df_shopee_related

def process_product_from_link( data, bucket, folder, category):
    ######## NEED TO CHECK PROPER NAMING OF ITEMS ON RESPONSE JSON FILE
    df_list=[]
    title=data['name']
    if 'brand' in data:
        brand=data['brand']
    else:
        brand='test'
    if 'show_official_shop_label_in_title' in data:
        label=data['show_official_shop_label_in_title']
    else:
        label=False
    if 'item_rating' in data:
        rating=data['item_rating']
        if 'rating_star' in rating:
            rating_star=rating['rating_star']
    else:
        rating_star=0
    df_list.append(get_title_related_data(title, brand, label, rating_star))

    if 'transparent_background_image' in data:
        background_image=data['transparent_background_image']
    else:
        background_image=False
    if 'can_use_wholesale' in data:
        wholesale=data['can_use_wholesale']
    else:
        wholesale=False
    if 'can_use_bundle_deal' in data:
        bundle_deal=data['can_use_bundle_deal']
    else:
        bundle_deal=False
    if 'shopee_verified' in data:
        verified_label=data['shopee_verified']
    else:
        verified_label=False
    if 'show_free_shipping' in data:
        free_shipping=data['show_free_shipping']
    else:
        free_shipping=False
    # print((background_image, wholesale, bundle_deal, verified_label, free_shipping))
    df_list.append(get_shopee_related_data(background_image, wholesale, bundle_deal, verified_label, free_shipping))

    df_bag_of_words=pd.DataFrame()
    bag_of_words_file=file_read_lib.get_file_from_bucket(bucket, folder, category)
    bag_of_words=file_read_lib.get_content_from_file(bag_of_words_file)
    for word in bag_of_words:
        common_words_in_title=[]
        if word in title:
            common_words_in_title.append(1)
        else:
            common_words_in_title.append(0)
        df_bag_of_words[word]=common_words_in_title
    df_list.append(df_bag_of_words)
    combined_df=pd.concat(df_list, axis=1)
    return combined_df
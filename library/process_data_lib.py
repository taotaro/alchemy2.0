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
    if type(brand)==float and pd.isna(brand):
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

def process_product_from_link( data, category, folder):
    df_list=[]
    title=data['name']
    brand='test'
    label=data['show_official_shop_label_in_title']
    rating=4.968
    df_list.append(get_title_related_data(title, brand, label, rating))

    background_image=0
    wholesale=False
    bundle_deal=False
    verified_label=True
    free_shipping=True
    df_list.append(get_shopee_related_data(background_image, wholesale, bundle_deal, verified_label, free_shipping))

    df_bag_of_words=pd.DataFrame()
    bag_of_words=file_read_lib.get_list_from_text_file(category, folder)
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
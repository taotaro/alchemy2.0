from re import L
import re
import pandas as pd
import numpy as np
import string
from nltk.corpus import stopwords
import os
import warnings
stop_words=set(stopwords.words('english'))
warnings.filterwarnings('ignore')
from textblob import TextBlob
import os
from . import score_lib
# import score_lib
from collections import Counter
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.util import ngrams
from nltk.tokenize.treebank import TreebankWordDetokenizer
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt
from mlxtend.feature_selection import SequentialFeatureSelector as sfs
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm

#forward selection for product category
def sort_features_based_on_relevance(data, target, significance_level=0.05):
    initial_features=data.columns.tolist()
    best_features=[]
    while(len(initial_features)>0):
        remaining_features=list(set(initial_features)-set(best_features))
        new_pval=pd.Series(index=remaining_features, dtype='float64')
        for new_column in remaining_features:
            model=sm.OLS(target, sm.add_constant(data[best_features+[new_column]])).fit()
            new_pval[new_column]=model.pvalues[new_column]
        min_p_value=new_pval.min()
        if(min_p_value<significance_level):
            best_features.append(new_pval.idxmin())
        else:
            break
    return best_features

def forward_selection(data, name='test', folder='test'):
    #product_id not relevant in forward selection
    if 'Product_id' in data.columns:
        data=data.drop('Product_id', axis=1)
    X=data.drop('Sales',axis=1)
    y=data['Sales']
    ordered_features=sort_features_based_on_relevance(X, y)
    file_path=os.path.join(folder, name+'.txt')
    with open(file_path, 'w') as fp:
        fp.write('\n'.join(str(item) for item in ordered_features))
        fp.close()

# bag of words for product category
def associated_bag_of_words(data, occurences, folder, name):
    title_data=data['product.name'].fillna('')
    phrase_counter=Counter()
    title_list=[]

    #get most common associated words
    for title in title_data:
        title_list.append(title.lower())
        for sentence in sent_tokenize(title):
            words=word_tokenize(sentence)
            for phrase in ngrams(words, 3):
                phrase_counter[TreebankWordDetokenizer().detokenize(phrase)]+=1
    most_common_words=phrase_counter.most_common(occurences)
    most_common_words_list=[]
    for word, occurence in most_common_words:
        most_common_words_list.append(word)
    file_path=os.path.join(folder, name+'.txt')
    with open(file_path, 'w') as fp:
        fp.write('\n'.join(str(item) for item in most_common_words_list))
        fp.close()
    return most_common_words_list

def bag_of_words(data, occurences):
    title_data=data['name']
    vectorizer=CountVectorizer(ngram_range=(1,1), stop_words='english')
    title_vectorized=vectorizer.fit_transform(title_data)
    title_df=pd.DataFrame(title_vectorized.toarray(), columns=vectorizer.get_feature_names())
    total_occurences=[]
    occurence_position=[]
    for i in range(len(title_df.columns)):
        location=title_df.iloc[:,i]
        total_occurences.append(location.sum())
        occurence_position.append(i)
    occurence_df=pd.DataFrame({'position':occurence_position, 'Occurence':total_occurences})
    occurence_df=occurence_df.sort_values(by=['Occurence'], ascending=False)
    occurence_list=occurence_df['position'].tolist()
    bag_of_words_df=pd.DataFrame()
    for j in range(occurences):
        bag_of_words_df[title_df.columns[occurence_list[j]]]=title_df[title_df.columns[occurence_list[j]]]
    return bag_of_words_df


#process product data
def get_title_length(title):
    words=sum([word.strip(string.punctuation).isalpha() for word in title.split()])
    title_length=int(words)

    #take max title length as 20 and min title length as 0 to scale length
    scaled_length=(title_length)/18
    return scaled_length

def check_if_brand_in_title(title, brand):
    #if brand column is na
    if (type(brand)==float and pd.isna(brand)) or type(brand)==type(None):
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

def get_rgb(rgb_data):
    num=re.findall('\d*\.?\d+', rgb_data)
    if float(num[0])>200:
        red=1
    else:
        red=0
    if float(num[0])>200:
        blue=1
    else:
        blue=0
    if float(num[0])>200:
        green=1
    else:
        green=0
    return red, green, blue

def get_height_and_width(height_width_data):  
    if type(height_width_data)==str:
        num=re.findall(r'\d+', height_width_data)
        height=num[0]
        width=num[1]
    else:
        height=0
        width=0
    return height, width

def get_image_related_data(brightness, blurriness, contrast, text_area, angle, borders, height_width, rgb):
    red, green, blue=get_rgb(rgb)
    height, width=get_height_and_width(height_width)
    df_image_related=pd.DataFrame({
        'Brightness':brightness/250,
        'Blurriness':blurriness/1000,
        'Contrast':contrast/50,
        'Text_covered_area':text_area/100,
        'Angle':abs(angle)/180,
        'Borders_exist':borders,
        'Height':height/1024,
        'Width':width/1024,
        'Red':red,
        'Green':green,
        'Blue':blue
    })
    return df_image_related


def process_product_from_link(data, bucket, folder_bag_of_words, category, image_id, folder_image_data):

    print('image id: ', image_id)
    df_list=[]
    df_list_title_related=[]
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
    title_data=get_title_related_data(title, brand, label, rating_star)
    df_list.append(title_data)
    df_list_title_related.append(title_data)

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
    shopee_data=get_shopee_related_data(background_image, wholesale, bundle_deal, verified_label, free_shipping)
    df_list.append(shopee_data)


    ###### REQUIRED FOR IMAGE DATA (CURRENTLY NOT AVAILABLE FOR SINGLE PRODUCT--COMMENTED OUT)
    # image_data_file=score_lib.get_file_from_bucket(bucket, folder_image_data, category)
    # image_data=pd.read_csv(image_data_file, index_col=0)
    # brightness=image_data['Brightness']
    # blurriness=image_data['Blurriness']
    # contrast=image_data['Contrast']
    # text_area=image_data['Text Covered Area']
    # angle=image_data['Angle']
    # borders=image_data['Borders exist']
    # height_width=image_data['Pixels (Height, Width)']
    # rgb=image_data['Background_Color'].astype(str)
    # image_features_data=get_image_related_data(brightness, blurriness, contrast, text_area, angle, borders, height_width, rgb)
    # print(image_features_data)
    # df_list.append(image_features_data)
    
    df_bag_of_words=pd.DataFrame()
    bag_of_words_file=score_lib.get_file_from_bucket(bucket, folder_bag_of_words, category)
    bag_of_words=score_lib.get_content_from_file(bag_of_words_file)
    for word in bag_of_words:
        common_words_in_title=[]
        if word in title:
            common_words_in_title.append(1)
        else:
            common_words_in_title.append(0)
        df_bag_of_words[word]=common_words_in_title
    df_list.append(df_bag_of_words)
    df_list_title_related.append(df_bag_of_words)

    title_related_column=[]
    shopee_related_column=[]
    for column in title_data:
        title_related_column.append(column)
    for column in df_bag_of_words:
        title_related_column.append(column)
    for column in shopee_data:
        shopee_related_column.append(column)
    combined_df=pd.concat(df_list, axis=1)
    combined_df_tite_related = pd.concat(df_list_title_related, axis = 1 )
  
    return combined_df, title_related_column, shopee_related_column, combined_df_tite_related


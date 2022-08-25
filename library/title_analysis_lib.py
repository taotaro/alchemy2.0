import pandas as pd
from textblob import TextBlob
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import warnings
import string
from nltk.tokenize import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer
import re
from nltk.corpus import stopwords

stop_words = set(stopwords.words("english"))
warnings.filterwarnings("ignore")

# check if brand_name (extracted from API) exists in the title
def brand_name_in_title(title, brand):
    if brand not in title:
        return False
    else:
        return True

# check if numbers are present in the title
def has_numbers(title):
    return any(char.isdigit() for char in title)

# classifies title as neutral, positive, or negative
def sentiment_analysis(title_data):
    data["sentiment_score"] = title_data.apply(
        lambda x: TextBlob(str(x)).sentiment.polarity
    )
    data["sentiment"] = np.select(
        [
            data["sentiment_score"] < 0,
            data["sentiment_score"] == 0,
            data["sentiment_score"] > 0,
        ],
        ["neg", "neu", "pos"],
    )
    mood = data["sentiment"]
    return mood

# bag of words for title and outputs top k words (value attribute)
def bog(title_data, value):
    # vectorize the data and compile into dataframe
    cv = CountVectorizer(ngram_range=(1, 1), stop_words="english")
    title_cd = cv.fit_transform(title_data)
    title_df = pd.DataFrame(title_cd.toarray(), columns=cv.get_feature_names())

    # initialize
    column_len = len(title_df.columns)
    words_list = []
    occ = []

    # extract top k words
    for i in range(column_len):
        loc = title_df.iloc[:, i]
        words_list.append(loc.sum())
        occ.append(i)

    occ_df = pd.DataFrame({"item": occ, "Occurence": words_list})
    occ_df = occ_df.sort_values(by=["Occurence"], ascending=False)
    occ_list = occ_df["item"].tolist()
    bog_df = pd.DataFrame()

    for j in range(value):
        bog_df[title_df.columns[occ_list[j]]] = title_df[title_df.columns[occ_list[j]]]

    return bog_df


# balance dataset (same number of good and bad sales)
def balance_df(df_title):
    df_title_bad = df_title[df_title["Sales"] == 0]
    df_title_good = df_title[df_title["Sales"] == 1]
    title_diff = abs(len(df_title_bad.index) - len(df_title_good.index))
    df_title_new = df_title.drop(df_title_bad.tail(title_diff).index, axis=0)
    return df_title_new


# compile all lists into a df
def make_df(
    product_id,
    brand_in_title,
    mood,
    number_in_title,
    bog,
    mall_label_in_title,
    sales,
    title_len,
):
    df = pd.DataFrame(
        {
            "Product_id": product_id,
            "Title_length": title_len,
            "Brand_in_title": brand_in_title,
            "Mood": mood,
            "Number_in_title": number_in_title,
            "Label_in_title": mall_label_in_title,
        }
    )
    df_title = pd.concat(
        [df.reset_index(drop=True), bog.reset_index(drop=True)], axis=1
    )
    df_title.insert(len(df_title.columns), "Sales", sales)
    df_title = balance_df(df_title)
    return df_title


# make a df with the title included
def df_with_title(
    product_id,
    brand_in_title,
    mood,
    number_in_title,
    bog,
    mall_label_in_title,
    sales,
    title_len,
    title_data,
):
    title_list = []
    for i in title_data:
        title_list.append(i)

    df = pd.DataFrame(
        {
            "Title": title_list,
            "Product_id": product_id,
            "Title_length": title_len,
            "Brand_in_title": brand_in_title,
            "Mood": mood,
            "Number_in_title": number_in_title,
            "Label_in_title": mall_label_in_title,
        }
    )
    df_title = pd.concat(
        [df.reset_index(drop=True), bog.reset_index(drop=True)], axis=1
    )
    df_title.insert(len(df_title.columns), "Sales", sales)
    # df_title=balance_df(df_title)

    return df_title


# remove brand name from title
def remove_brand(title_data, brand_data):
    title_wo_brand = []
    for i in range(len(title_data)):
        new_title = title_data[i].replace(str(brand_data[i]), "")
        title_wo_brand.append(new_title)
    return title_wo_brand


# preprocess title for clustering (remove brand name, numbers, symbols and stopwords)
def preprocessed_title(title_data, brand_data):
    title_data_new = remove_brand(title_data, brand_data)
    title_list = []
    for i in range(len(title_data_new)):
        title = word_tokenize(title_data_new[i])
        word_list = []
        for word in title:
            title_digits = has_numbers(word)
            if title_digits or word in stop_words:
                continue
            else:
                word_list.append(word)
        detokenized_list = TreebankWordDetokenizer().detokenize(word_list)
        new_title = re.sub(r"[^\w]", " ", detokenized_list)
        title_list.append(new_title.lower())
    return title_list


# classify product as good or bad
def classify_sales(sales_data):
    sales_list = []
    sales_data = sales_data.replace("", 0)
    mean = sales_data.mean()
    sd = sales_data.std()
    for i in range(len(sales_data)):
        if sales_data[i] > (mean + 0.01 * sd):
            sales_list.append(1)
        else:
            sales_list.append(0)
    return sales_list


# main function
def title_analysis(
    title_data, brand_data, label_data, id_data, sales_data, title_include=False
):
    is_brand_in_title = []
    mood_list = []
    number_in_title = []
    mall_label_in_title = []
    item_id_list = []

    title_len_list = []

    mood = sentiment_analysis(title_data)
    bog_df = bog(title_data, 1000)

    sales_list = classify_sales(sales_data)

    # print(test)
    for i in range(len(title_data)):
        item_id_list.append(id_data[i])

        words = sum(
            [i.strip(string.punctuation).isalpha() for i in title_data[i].split()]
        )

        title_len_list.append(str(words))

        # print(title_data[i])
        brand_title = brand_name_in_title(title_data[i], brand_data[i])
        if brand_title:
            is_brand_in_title.append(1)
        else:
            is_brand_in_title.append(0)
        if mood[i] == "neu":
            mood_list.append(0)
        elif mood[i] == "pos":
            mood_list.append(1)
        else:
            mood_list.append(-1)
        number_title = has_numbers(title_data[i])
        if number_title:
            number_in_title.append(1)
        else:
            number_in_title.append(0)
        if label_data[i]:
            mall_label_in_title.append(1)
        else:
            mall_label_in_title.append(0)

    # print(title_len_list)
    if title_include:
        df = df_with_title(
            item_id_list,
            is_brand_in_title,
            mood_list,
            number_in_title,
            bog_df,
            mall_label_in_title,
            sales_list,
            title_len_list,
            title_data,
        )
    else:
        df = make_df(
            item_id_list,
            is_brand_in_title,
            mood_list,
            number_in_title,
            bog_df,
            mall_label_in_title,
            sales_list,
            title_len_list,
        )

    return df


# save df to csv
def df_to_csv(data, csv_name, title_include=False, only_title=False):

    # retrive all columns
    title_data = data["item_basic.name"]
    brand_data = data["item_basic.brand"]
    label_data = data["item_basic.show_official_shop_label_in_title"]
    sales_data = data["item_basic.sold"]
    id_data = data["itemid"]

    brand_data = brand_data.fillna("")
    if only_title:
        title_list = preprocessed_title(title_data, brand_data)
        sales_list = classify_sales(sales_data)
        df = pd.DataFrame(
            {"Title": title_list, "Product_id": id_data, "Sales": sales_list}
        )
        df = balance_df(df)
    else:
        df = title_analysis(
            title_data, brand_data, label_data, id_data, sales_data, title_include
        )
    df.to_csv(csv_name + ".csv")
    return df

#HOW TO USE LIBRARY

# df_to_csv is the only function you have to call
# the attributes are:
# 1. Data
# 2. csv file name (save it so its easy to identify the vertical and what the data is used for)
# 3. title_include (for dnn and kmeans not necessary, but gives ease of access)
# 4. only_title (this attribute is only used for saving data which is used in kmeans)
# Note: df_to_csv(data, '{provide csv file name}') --- is the method used for producing data used in dnn
# df_to_csv(data, '{provide csv file name}', only_title=True) --- is the method used for producing data used in kmeans
# create and save both csvs' for each vertical

# declare the dataset/vertical
data = pd.read_csv("Healthcare.csv")
# get df (pass data, name of csv, whether title should be included in the df and if only title should be included in df)
df_to_csv(data, "kmeans_healthcare_data", only_title=True).head()

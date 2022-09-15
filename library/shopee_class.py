from enum import unique
import mongoengine as me
import pandas as pd
import numpy as np
import logging
import time

time_str = time.strftime("%Y-%m-%d")
logging.basicConfig(filename=f"logs/run-{time_str}.log", level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")

def init_db():
    '''
    # This function initializes connection to the scrape mongodb.
    #
    #
    '''
    try:
        me.connect(alias='alchemy',
                    db='alchemy',
                    username='devuser',
                    password='1000Sunny',
                    authentication_source='alchemy',
                    host='externaltaotarodb1.mongodb.rds.aliyuncs.com',
                    port=3717
                    )
        logging.debug('Connection to MongoDB: initialized')
        print('Connection to MongoDB: initialized')
    except:
        print('Connection to MongoDB unsuccessful')
    return


def discon_db():
    '''
    This function disconnects from the mongoDB database
    '''
    me.disconnect(alias='alchemy')
    return


def correct_encoding(dictionary):
    # Correct the encoding of python dictionaries so they can be encoded to mongodb
    # inputs
    # -------
    # dictionary : dictionary instance to add as document
    # output
    # -------
    # new : new dictionary with (hopefully) corrected encodings

    new = {}
    for key1, val1 in dictionary.items():
        # Nested dictionaries
        if isinstance(val1, dict):
            val1 = correct_encoding(val1)

        if isinstance(val1, np.bool_):
            val1 = bool(val1)

        if isinstance(val1, np.int64):
            val1 = int(val1)

        if isinstance(val1, np.float64):
            val1 = float(val1)

        new[key1] = val1

    return new


class shopeeProduct(me.Document):
    meta = {'db_alias': 'alchemy', 'collection': 'shopeeProducts'}
    ts = me.DateField()
    product = me.DictField()
    product.itemid = me.IntField(unique=True)
    product.shopid = me.IntField()
    product.name = me.StringField()
    product.label_ids = me.StringField()
    product.image = me.StringField()
    product.images = me.StringField()
    product.currency = me.StringField()
    product.price = me.StringField()
    product.price_min = me.StringField()
    product.price_max = me.StringField()
    product.price_min_before_discount = me.StringField()
    product.price_max_before_discount = me.StringField()
    product.price_before_discount = me.StringField()
    product.stock = me.StringField()
    product.status = me.StringField()
    product.ctime = me.StringField()
    product.sold = me.StringField()
    product.historical_sold = me.StringField()
    product.catid = me.StringField()

def save_product(dic):
    product_obj = shopeeProduct()
    product_obj.ts = dic["ts"]
    product = {
        "itemid": dic["product.itemid"],
        "shopid": dic["product.shopid"],
        "name": dic["product.name"],
        "label_ids": dic["product.label_ids"],
        "image": dic["product.image"],
        "images": dic["product.images"],
        "currency": dic["product.currency"],
        "price": dic["product.price"],
        "price_min": dic["product.price_min"],
        "price_max": dic["product.price_max"],
        "price_min_before_discount": dic["product.price_min_before_discount"],
        "price_max_before_discount": dic["product.price_max_before_discount"],
        "price_before_discount": dic["product.price_before_discount"],
        "stock": dic["product.stock"],
        "status": dic["product.status"],
       "ctime": dic["product.ctime"],
        "sold": dic["product.sold"],
        "historical_sold": dic["product.historical_sold"],
        "catid": dic["product.catid"],
    }
    product_obj.product = product
    try:
        product_obj.save()
        print(f"Saved -- {dic['product.itemid']}")
    except:
        print(f"Not saved -- {dic['product.itemid']}")
    return

def to_db(df):
    for i in np.arange(len(df)):
        temp = correct_encoding(df.iloc[i])
        save_product(temp)
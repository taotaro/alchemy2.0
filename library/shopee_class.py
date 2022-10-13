from enum import unique
from math import prod
import mongoengine as me
from pymongo import MongoClient
import pandas as pd
import numpy as np
import logging
import time
from alive_progress import alive_bar

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
        print('Connection to MongoDB through mongoengine: initialized')
    except:
        print('Connection to MongoDB unsuccessful')
    return


def connect_db():
    try:
      client = MongoClient('mongodb://devuser:1000Sunny@externaltaotarodb1.mongodb.rds.aliyuncs.com:3717,externaltaotarodb2.mongodb.rds.aliyuncs.com:3717/alchemy?authSource=alchemy&replicaSet=mgset-28314303&readPreference=primary&ssl=false')
      db = client.alchemy
      db.create_collection('ts_shopee', 
        timeseries={ 
          'timeField': 'timestamp', 
          'metaField': 'metadata', 
          'granularity': 'days' 
        })
      print('Connection to MongoDB through pymongo: initialized')
      return db
    except:
      print('Connection to MongoDB unsuccessful')


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


# class shopeeProduct(me.Document):
#     meta = {'db_alias': 'alchemy', 'collection': 'shopeeProducts'}
#     ts = me.DateField()
#     cat_id = me.IntField()
#     cat_name = me.StringField()
#     products = me.ListField()
#     products.product = me.DictField()
#     products.product.itemid = me.IntField(unique=True)
#     products.product.shopid = me.IntField()
#     products.product.name = me.StringField()
#     products.product.label_ids = me.StringField()
#     products.product.image = me.StringField()
#     products.product.images = me.StringField()
#     products.product.currency = me.StringField()
#     products.product.price = me.StringField()
#     products.product.price_min = me.StringField()
#     products.product.price_max = me.StringField()
#     products.product.price_min_before_discount = me.StringField()
#     products.product.price_max_before_discount = me.StringField()
#     products.product.price_before_discount = me.StringField()
#     products.product.stock = me.StringField()
#     products.product.status = me.StringField()
#     products.product.ctime = me.StringField()
#     products.product.sold = me.StringField()
#     products.product.historical_sold = me.StringField()
#     products.product.catid = me.StringField()


class shopeeProduct(me.Document):
    meta = {'db_alias': 'alchemy', 'collection': 'sProducts'}
    ts = me.DateField()
    cat_id = me.IntField()
    cat_name = me.StringField()
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


# def save_product(dic, cat_id, cat_name):
#     # find object with same date and category to update
#     try:
#       product_obj = shopeeProduct.objects(ts=dic['ts'], cat_id=cat_id, cat_name=cat_name).get()
#     except:
#       product_obj = {}

#     product = [{
#           "itemid": dic["product.itemid"],
#           "shopid": dic["product.shopid"],
#           "name": dic["product.name"],
#           "label_ids": dic["product.label_ids"],
#           "image": dic["product.image"],
#           "images": dic["product.images"],
#           "currency": dic["product.currency"],
#           "price": dic["product.price"],
#           "price_min": dic["product.price_min"],
#           "price_max": dic["product.price_max"],
#           "price_min_before_discount": dic["product.price_min_before_discount"],
#           "price_max_before_discount": dic["product.price_max_before_discount"],
#           "price_before_discount": dic["product.price_before_discount"],
#           "stock": dic["product.stock"],
#           "status": dic["product.status"],
#           "ctime": dic["product.ctime"],
#           "sold": dic["product.sold"],
#           "historical_sold": dic["product.historical_sold"],
#           "catid": dic["product.catid"],
#     }]

#     if product_obj != {}:
#         success = product_obj.update(add_to_set__products=product)
#         print(success)
#         # old_product_obj = shopeeProduct.objects(ts=dic['ts'], cat_id=cat_id, cat_name=cat_name).update_one(products=products.append(product))
#     else:
#         new_product_obj = shopeeProduct()
#         new_product_obj.ts = dic["ts"]
#         new_product_obj.cat_id = cat_id
#         new_product_obj.cat_name = cat_name
#         new_product_obj.products = [product]
#         new_product_obj.save()
#     return

def save_product(dic, cat_id, cat_name):
    product_obj = shopeeProduct()

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

    product_obj.ts = dic["ts"]
    product_obj.cat_id = cat_id
    product_obj.cat_name = cat_name
    product_obj.product = product
    product_obj.save()
    print(f"Saved -- {dic['product.itemid']}")
    return

# TO-DO: create proper time series collection
def to_db(df, cat_id, cat_name):
    for i in np.arange(len(df)):
        temp = correct_encoding(df.iloc[i])
        save_product(temp, cat_id, cat_name)

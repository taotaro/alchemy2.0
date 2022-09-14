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
    me.connect(alias='alchemy',
                db='alchemy',
                username='devtest',
                password='1000$unny',
                authentication_source='scrape',
                host='externaltaotarodb1.mongodb.rds.aliyuncs.com',
                port=3717
                )
    logging.debug('Connection to MongoDB: initialized')
    return


def discon_db():
    '''
    This function disconnects from the mongoDB database
    '''
    me.disconnect(alias='alchemy')
    return

class shopeeProduct(me.Document):
    meta = {'db_alias': 'alchemy', 'collection': 'shopeeProducts'}
    ts = me.DateField()
    product = me.DictField()
    product.itemid = me.IntField()
    product.shopid = me.IntField()
    product.name = me.StringField()
    product.label_ids = me.ListField()
    product.image = me.StringField()
    product.images = me.ListField()
    product.currency = me.StringField()
    product.price = me.DecimalField()
    product.price_min = me.DecimalField()
    product.price_max = me.DecimalField()
    product.price_min_before_discount = me.DecimalField()
    product.price_max_before_discount = me.DecimalField()
    product.price_before_discount = me.DecimalField()
    product.stock = me.IntField()
    product.status = me.IntField()
    product.ctime = me.IntField()
    product.sold = me.IntField
    product.historical_sold = me.IntField()
    product.catid = me.IntField()

def save_product(dic):
    product_obj = shopeeProduct()
    product_obj.ts = dic["ts"]
    product_obj.product = dic["product"]
    product_obj.save()
    print(f"Saved -- {dic['product'].itemid}")
    return

def to_db(df):
    for row in df:
        save_product(row)
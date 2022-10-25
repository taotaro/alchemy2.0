from urllib import request
import pymongo
import pandas as pd
import json
import re
from shopee_class import shopeeProduct
import requests
import mongoengine as me

class productDataShopee(me.Document):
    meta = {'db_alias': 'alchemy', 'collection': 'sProducts'}
    ts = me.DateField()
    cat_id = me.IntField()
    cat_name = me.StringField()
    product = me.DictField()

def get_data_from_database(category):
  try:
    me.connect(alias='alchemy',
                db='alchemy',
                username='devuser',
                password='1000Sunny',
                authentication_source='alchemy',
                host='externaltaotarodb1.mongodb.rds.aliyuncs.com',
                port=3717
              )
    print('Connection to MongoDB: initialized')
  except:
    print('Connection to MongoDB unsuccessful')
  res = productDataShopee.objects(cat_name=category).to_json()
  return res


def get_data_cleaned(data):
  category_data = []
  for item in data:
    if 'item_rating' and 'discount' in item['product']:
      category_data.append(item)
  
  return category_data

def get_data_for_scatter_plot(data):
  data_updated = []
  for item in data:
    new_data = {}
    new_data['x'] = round(item['product']['item_rating']['rating_star'], 2)
    new_data['y'] = item['product']['sold']
    data_updated.append(new_data)
  json_data = json.dumps(data_updated)
  return json_data

def get_data_for_bar_graph(data):
  data_updated = []
  for item in data:
    new_data = {}
    new_data['product'] = item['product']['name'][0 : 20]
    new_data['sales'] = item['product']['sold']
    new_data['historicalSales'] = item['product']['historical_sold']
    new_data['discount'] =  int(str(item['product']['discount']).strip('%'))
    new_data['ratingCount'] = item['product']['item_rating']['rating_count']
    new_data['likesCount'] = item['product']['liked_count']
    data_updated.append(new_data)
  json_data = json.dumps(data_updated)
  return json_data

def get_data_for_swarm_graph(data):
  data_updated = []
  for item in data:
    new_data = {}
    new_data['id'] = item['product']['itemid']
    new_data['group'] = str(item['product']['shopee_verified'])
    new_data['data'] = item['product']['sold']
    new_data['discount'] =  int(str(item['product']['discount']).strip('%'))
    data_updated.append(new_data)
  json_data = json.dumps(data_updated)
  return json_data

def get_data_for_bar_revenue(data):
  data_updated = []
  for item in data:
    new_data = {}
    new_data['product'] = item['product']['itemid']
    new_data['revenue'] = item['product']['sold'] * item['product']['price'] / 100000
    data_updated.append(new_data)
  json_data = json.dumps(data_updated)
  return json_data

def get_data_for_pie_chart(data, name):
  data_updated = []
  user_data = []
  label = ['1 star', '2 stars', '3 stars', '4 stars', '5 stars']
  id = ["*", "**", "***", "****", "*****"]

  for item in data:
    if item['product']['name'] == name:
      user_data = item['product']['item_rating']['rating_count']

  for i in range(len(user_data)):
    new_data = {}
    # first value on list is total count
    if i == 0:
      continue
    new_data['id'] = id[i - 1]
    new_data['label'] = label[i - 1]
    new_data['value'] = user_data[i]
    new_data['key'] = i - 1
    data_updated.append(new_data)
  json_data = json.dumps(data_updated)
  return json_data

def get_product_specifications(data, name):
  user_data = {}
  for item in data:
    if item['product']['name'] == name:
      user_data['sales'] = item['product']['sold']
      user_data['rating'] = item['product']['item_rating']['rating_star']
      user_data['revenue'] = item['product']['sold'] * item['product']['price'] / 100000
      user_data['likes'] = item['product']['liked_count']
    
  json_data = json.dumps(user_data)
  return json_data
  



### MAIN FUNCTION
def get_graph_data(category, product_name):
  data = get_data_from_database(category)
  data_in_json = json.loads(data)
  category_data = get_data_cleaned(data_in_json)
  
  # remove none values
  for item in category_data:
    for key in item['product']:
      if item['product'][key] is None:
        item['product'].update({ key : 0 })
      else:
        continue

  scatter_data = get_data_for_scatter_plot(category_data)
  bar_data = get_data_for_bar_graph(category_data)
  swarm_data = get_data_for_swarm_graph(category_data)
  revenue_data = get_data_for_bar_revenue(category_data)
  pie_data = get_data_for_pie_chart(category_data, product_name)

  product_specs = get_product_specifications(category_data, product_name)

  return scatter_data, bar_data, swarm_data, revenue_data, pie_data, product_specs
  




if __name__ == "__main__":
  
  test_product = 'Athena Crop Top'
  test_scatter, test_bar, test_swarm, test_revenue, test_pie, test_specs=get_graph_data("Tops", test_product)
  # print(test_pie)
  # print(test_bar, test_swarm, test_pie, test_revenue)



  
    
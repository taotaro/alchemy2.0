import pymongo
import pandas as pd
import json
import re

def get_data(uri, folder, file):
  client = pymongo.MongoClient(uri)
  db = client[folder]
  col = db[file]
  return col


def get_data_for_category(data, category):
  print('looking')
  category_data = []
  for i in data:
    if i['cat_name'] == category:
     if 'item_rating' and 'discount' in i['product']:
      category_data.append(i)
  print('done')
  return category_data

def get_data_for_scatter_plot(data):
  data_updated = []
  for i in data:
    new_data = {}
    new_data['x'] = round(i['product']['item_rating']['rating_star'], 2)
    new_data['y'] = i['product']['sold']
    data_updated.append(new_data)
  json_data = json.dumps(data_updated)
  return json_data

def get_data_for_bar_graph(data):
  data_updated = []
  for i in data:
    new_data = {}
    new_data['product'] = i['product']['name'][0:20]
    new_data['sales'] = i['product']['sold']
    new_data['historicalSales'] = i['product']['historical_sold']
    new_data['discount'] =  int(str(i['product']['discount']).strip('%'))
    new_data['ratingCount'] = i['product']['item_rating']['rating_count']
    new_data['likesCount'] = i['product']['liked_count']
    data_updated.append(new_data)
  json_data = json.dumps(data_updated)
  return json_data

def get_data_for_swarm_graph(data):
  data_updated = []
  for i in data:
    new_data = {}
    new_data['id'] = i['product']['itemid']
    new_data['group'] = str(i['product']['shopee_verified'])
    new_data['data'] = i['product']['sold']
   
    new_data['discount'] =  int(str(i['product']['discount']).strip('%'))
   
    data_updated.append(new_data)
  json_data = json.dumps(data_updated)
  return json_data

def get_data_for_bar_revenue(data):
  data_updated = []
  for i in data:
    new_data = {}
    new_data['product'] = i['product']['itemid']
    new_data['revenue'] = i['product']['sold'] * i['product']['price'] /100000
    data_updated.append(new_data)
  json_data = json.dumps(data_updated)
  return json_data

def get_data_for_pie_chart(data, name):
  data_updated = []
  user_data = []
  label = [
    '1 star', '2 star', '3 star', '4 star', '5 star'
  ]

  id = ["*", "**", "***", "****", "*****"]

  for i in data:
    if i['product']['name'] == name:
      user_data = i['product']['item_rating']['rating_count']


  for i in range(len(user_data)):
    new_data={}
    if i==0:
      continue
    new_data['id'] = id[i-1]
    new_data['label'] = label[i-1]
    new_data['value'] = user_data[i]
    new_data['key'] = i-1
    data_updated.append(new_data)
  json_data = json.dumps(data_updated)
  return json_data

def get_graph_data(client, category, product_name):
  data = get_data(client, 'alchemy', 'sProducts')
  category_data = get_data_for_category(data.find(), category)

  for i in category_data:
    for j in i['product']:
      if i['product'][j] is None:
        i['product'].update({j:0})
      else:
        continue

  

  scatter_data = get_data_for_scatter_plot(category_data)
  bar_data = get_data_for_bar_graph(category_data)
  swarm_data = get_data_for_swarm_graph(category_data)
  revenue_data = get_data_for_bar_revenue(category_data)
  pie_data = get_data_for_pie_chart(category_data, product_name)

  return scatter_data, bar_data, swarm_data, revenue_data, pie_data
  




if __name__ == "__main__":

  client = "mongodb://root:1000Sunny@externaltaotarodb1.mongodb.rds.aliyuncs.com:3717,externaltaotarodb2.mongodb.rds.aliyuncs.com:3717/admin?authSource=admin&replicaSet=mgset-28314303&readPreference=primary&ssl=false"
  test_product = 'Athena Crop Top'
  test_scatter, test_bar, test_swarm, test_revenue, test_pie=get_graph_data(client, 'Tops', test_product)
  print(test_scatter)


  # data = get_data(client, 'alchemy', 'sProducts')
  # category_data = get_data_for_category(data.find(), 'Tops')

  # print('category len: ', len(category_data))
  # scatter_data = get_data_for_scatter_plot(category_data)
  # print(scatter_data)
  # bar_data = get_data_for_bar_graph(category_data)
  # print(bar_data)
  # swarm_data = get_data_for_swarm_graph(category_data)
  # print(swarm_data)
  # revenue_data = get_data_for_bar_revenue(category_data)
  # print(revenue_data)
  
  # test_product = 'Athena Crop Top'
  

  # pie_data = get_data_for_pie_chart(category_data, test_product)
  # print(pie_data)
    
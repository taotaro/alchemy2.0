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
  category_data = []
  count = 10
  for i in data:
    if i['cat_name'] == category:
     if 'item_rating' and 'discount' in i['product']:
       category_data.append(i)
  return category_data




def get_data_for_scatter_plot(data):
  data_updated = []
  for i in data:
    new_data = {}
    new_data['x'] = i['product']['item_rating']['rating_star']
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
    if i['product']['discount'] is not None:
      new_data['discount'] =  i['product']['discount'].strip('%')
    else:
      new_data['discount'] = 0
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
    if i['product']['discount'] is not None:
      new_data['discount'] =  i['product']['discount'].strip('%')
    else:
      new_data['discount'] = 0
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

def get_data_for_pie_chart(data, position, id, label):
  data_updated = []
  user_data = data[position]['product']['item_rating']['rating_count']
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



if __name__ == "__main__":

  client = "mongodb://root:1000Sunny@externaltaotarodb1.mongodb.rds.aliyuncs.com:3717,externaltaotarodb2.mongodb.rds.aliyuncs.com:3717/admin?authSource=admin&replicaSet=mgset-28314303&readPreference=primary&ssl=false"
  data = get_data(client, 'alchemy', 'sProducts')
  category_data = get_data_for_category(data.find(), 'Tops')

  print('category len: ', len(category_data))
  scatter_data = get_data_for_scatter_plot(category_data)
  print(scatter_data)
  bar_data = get_data_for_bar_graph(category_data)
  print(bar_data)
  swarm_data = get_data_for_swarm_graph(category_data)
  print(swarm_data)
  revenue_data = get_data_for_bar_revenue(category_data)
  print(revenue_data)
  pieLabels = [
    ("ShopeeGraph.dashboard.pieChart.labels.oneStar"),
    ("ShopeeGraph.dashboard.pieChart.labels.twoStar"),
    ("ShopeeGraph.dashboard.pieChart.labels.threeStar"),
    ("ShopeeGraph.dashboard.pieChart.labels.fourStar"),
    ("ShopeeGraph.dashboard.pieChart.labels.fiveStar"),
  ]

  pieIds = ["*", "**", "***", "****", "*****"]

  pie_data = get_data_for_pie_chart(category_data, 2, pieIds, pieLabels)
  print(pie_data)
    
from cgi import test
from crypt import methods
from turtle import title
from unittest import result
from flask import Flask
from flask_restful import request
from flask_cors import CORS
import pandas as pd
import ast
from library import score_lib
import traceback

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/check', methods=['GET'])
def health_check():
    return "Alchemy is working!"

@app.route('/score/test', methods=['GET'])
def score_test():
    test_url = 'https://shopee.sg/Vention-Ethernet-Cable-Cat7-Lan-High-Speed-10Gbps-SFTP-RJ-45-Network-Cable-Patch-Cable-8m-10m-for-Laptop-PC-i.95236751.1578425947?sp_atk=533f4b97-0ce8-4eb0-8d9a-99fc000c4b59&xptdk=533f4b97-0ce8-4eb0-8d9a-99fc000c4b59'
    test_score = score_lib.get_score_of_product(test_url)
    print(test_score)
    return test_score

@app.route('/score/link', methods=['POST'])
def score_link():
    body = request.get_json()
    print(body['url'])
    if "url" in body:
      try: 
        final_score = score_lib.get_score_of_product(body['url'])
        print(final_score)
        return final_score
      except:
        print(traceback.format_exc())
        return "url invalid"
    else:
      return "No url detected"

@app.route('/score/user', methods=['POST'])
def score_user():
    body = request.get_json()
    if body:
      try:
        new_score = score_lib.score_product_with_user_shopee_features(body['title_data_list'], body['title_columns'], body['user_shopee_data'], body['sorted_features'])
        return new_score
      except:
        print(traceback.format_exc())
        return "input invalid"
    else:
      return "No input detected"

if __name__ == '__main__':
    app.run(
      host="0.0.0.0", 
      port=5000, 
      debug=True, 
      threaded=True, 
      ssl_context=('/etc/letsencrypt/live/taotaroapp.com/fullchain.pem', '/etc/letsencrypt/live/taotaroapp.com/privkey.pem')
    )  # run our Flask app

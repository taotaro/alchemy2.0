from cgi import test
from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast
from library import score_lib

app = Flask(__name__)
api = Api(app)

class Check(Resource):
  def get(self):
    return "Alchemy is working!"

class Score(Resource):
  def get(self):
    test_url = 'https://shopee.sg/Vention-Ethernet-Cable-Cat7-Lan-High-Speed-10Gbps-SFTP-RJ-45-Network-Cable-Patch-Cable-8m-10m-for-Laptop-PC-i.95236751.1578425947?sp_atk=533f4b97-0ce8-4eb0-8d9a-99fc000c4b59&xptdk=533f4b97-0ce8-4eb0-8d9a-99fc000c4b59'
    final_score = score_lib.get_score_of_product(test_url)
    print(final_score)
    return final_score
  
api.add_resource(Check, '/check') # entry point for Health Check
api.add_resource(Score, '/score') # entry point for Score

if __name__ == '__main__':
    app.run()  # run our Flask app
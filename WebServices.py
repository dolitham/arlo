from flask import json, request
from flask_restful import Resource
from services import *


class ListOperations (Resource):

    def get(self):
        operations = list_data_json()
        return json.loads(operations)


class CategorizeOperations(Resource):

    def post(self):
        ids = request.json['transaction_ids']
        category = request.json['category']

        result = categorize(ids, category)
        return {"status" : result}


class FetchOperations(Resource):

    def get(self):
        #refresh_data()
        return {"status" : 'SUCCESS'}

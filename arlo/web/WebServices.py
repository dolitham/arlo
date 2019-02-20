from flask import json, request
from flask_restful import Resource

from arlo.web.services import *


class ListOperations (Resource):

    @staticmethod
    def get():
        refresh = request.args.get('refresh')
        cycle = request.args.get('cycle')
        operations = list_data_json(cycle=cycle, refresh=refresh)
        return json.loads(operations)


class CategorizeOperations(Resource):

    @staticmethod
    def post():
        ids = request.json['transaction_ids']
        category = request.json['field_value']
        result = categorize(ids, category)
        return {"status": result}


class NameOperations(Resource):

    @staticmethod
    def post():
        ids = request.json['transaction_ids']
        category = request.json['field_value']
        result = name(ids, category)
        return {"status": result}


class ChangeCycle(Resource):

    @staticmethod
    def post():
        ids = request.json['transaction_ids']
        category = request.json['field_value']
        result = change_cycle(ids, category)
        return {"status": result}


class CreateManualTransaction(Resource):

    @staticmethod
    def post():
        json_input = request.json
        result = create_manual_transaction(json_input)
        return {"status": result}


class RefreshOperations(Resource):

    @staticmethod
    def get():
        result = force_refresh()
        return {"status": result}


class LinkTwoTransactions(Resource):

    @staticmethod
    def post():
        ids = request.json['transaction_ids']
        result = link_ids(ids)
        return {"status": result}


class GetRecap(Resource):

    @staticmethod
    def get():
        cycle = request.args.get('cycle')
        recap = get_recap_categories(cycle=cycle)
        return json.loads(recap)


class GetBalances(Resource):

    @staticmethod
    def get():
        cycle = request.args.get('cycle')
        recap = get_balances(cycle=cycle).reset_index()
        return json.loads(recap.to_json(orient="records"))


class MakeRecurring(Resource):
    @staticmethod
    def post():
        # name, amount, account = [request.json[field] for field in ['name', 'amount', 'account']]
        result = create_recurring_transaction(request.json['name'])
        return {"status": result}


class GetRecurring(Resource):
    @staticmethod
    def get():
        cycle = request.args.get('cycle')
        return json.loads(json.dumps(get_list_recurring(cycle)))


class GetAllCycles(Resource):
    @staticmethod
    def get():
        return json.loads(all_cycles())

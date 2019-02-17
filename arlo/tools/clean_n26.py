import requests

from arlo.parameters.credentials import login_N26
from arlo.parameters.param import n26_url


def get_token(name):
    values_token = {'grant_type': 'password', 'username': login_N26[name].username, 'password': login_N26[name].password}
    headers_token = {'Authorization': 'Basic YW5kcm9pZDpzZWNyZXQ='}
    response_token = requests.post(n26_url + '/oauth/token', data=values_token, headers=headers_token)
    token_info = response_token.json()
    if 'access_token' not in token_info:
        return False, ''
    return True, token_info['access_token']


def get_balance(name):
    if name not in login_N26:
        return False
    valid_token, access_token = get_token(name)
    headers = {'Authorization': 'bearer' + str(access_token)}
    req_balance = requests.get(n26_url + '/api/accounts', headers=headers)
    return req_balance.json()


def get_n_last_transactions(name, limit=10):
    if name not in login_N26:
        return False
    valid_token, access_token = get_token(name)
    if not valid_token:
        return False, ''
    headers = {'Authorization': 'bearer' + str(access_token)}
    req_transactions = requests.get(n26_url + '/api/smrt/transactions?limit=' + str(limit), headers=headers)
    return True, req_transactions.json()
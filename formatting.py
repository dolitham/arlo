import math
from collections import defaultdict

import pandas as pd

from param import *
from crud import read_data
from autofill_name import *

import numpy as np
import hashlib


def parse_ids(transaction_ids):
    try:
        transaction_ids = list(transaction_ids.replace(' ', '').split(','))
    except ValueError:
        return 'invalid ID', []
    data = read_data()
    ids = list(data['id'])
    if set(transaction_ids) & set(ids) != set(transaction_ids):
        return 'transaction not found', []
    return '', transaction_ids


def convert_timestamp_to_datetime(timestamp):
    return pd.datetime.fromtimestamp(timestamp // 1e3)


def make_bank_name(row):
    merchant, partner, reference, trans_type = [row[u].strip() for u in ['merchantName', 'partnerName', 'referenceText', 'type']]
    if merchant:
        return merchant
    if trans_type == 'DD':
        return '#PRLV ' + partner
    if reference:
        return row['referenceText'] + ' #VIR'
    return '#VIR ' + ['to ', 'from '][row['amount'] > 0] + partner


def remove_original_amount(row):
    if row['originalCurrency'] == 'EUR':
        return np.NaN
    return row['originalAmount']


def remove_original_currency(row):
    if row['originalCurrency'] == 'EUR':
        return ''
    return row['originalCurrency']


def make_cycle(row):
    month = str(row['date'].month_name())
    year = str(row['date'].year)
    return month[:3]+year[-2:]


def dataframe_formatter(df, account):
    df['bank_name'] = df.replace(np.NaN, '').apply(lambda row: make_bank_name(row), axis=1)
    df['name'] = df['bank_name'].apply(autofill_name)
    df['date'] = df['visibleTS'].apply(convert_timestamp_to_datetime)
    df['account'] = account
    df['category'] = df['name'].apply(autofill_cat)
    df['comment'] = '-'
    df['link'] = '-'
    df['pending'] = df['type'] == 'AA'
    df['originalAmount'] = df.apply(lambda row: remove_original_amount(row), axis=1)
    df['originalCurrency'] = df.apply(lambda row: remove_original_currency(row), axis=1)
    df['cycle'] = df.apply(lambda row: make_cycle(row), axis=1)
    return df[column_names]


def type_to_method(row):
    type = row['type']
    amount = row['amount']
    account = row['account']
    if type in ['PT', 'AA', 'AE']:
        return 'card'
    if type in ['DT', 'CT']:
        return 'transfer'
    if math.isnan(amount) or account == 'Cash':
        return 'cash'
    return 'card'


def create_id(name, timestamp, amount, account):
    letters_name = name
    string = '*'.join([letters_name, str(int(timestamp * 1000000)), str(int(amount * 100)), account])
    return hashlib.md5(string.encode()).hexdigest()


def make_a_csv_line(transaction_fields):
    timestamp = pd.datetime.timestamp(pd.datetime.now())
    name, account = [transaction_fields[u] for u in mandatory_fields]

    if transaction_fields['amount'] == '':
        amount = transaction_fields['originalAmount']
    else:
        amount = transaction_fields['amount']

    transaction_fields['id'] = create_id(name, timestamp, amount, account)

    if 'originalAmount' in transaction_fields and 'originalCurrency' not in transaction_fields:
        transaction_fields['originalCurrency'] = "USD"

    if 'date' not in transaction_fields:
        transaction_fields['date'] = convert_timestamp_to_datetime(1000 * timestamp)
    if 'category' not in transaction_fields:
        transaction_fields['category'] = '-'

    fields = defaultdict(lambda: "")
    for u in transaction_fields:
        fields[u] = transaction_fields[u]

    return ','.join(str(fields[col]) for col in column_names)

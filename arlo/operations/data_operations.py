import pandas as pd

from arlo.operations.types_operations import df_field_to_numeric_with_sign
from arlo.parameters.param import data_columns_mandatory_fields
from arlo.read_write.file_manager import read_data
from operations.df_operations import filter_df_on_id, get_one_field
from operations.series_operations import get_first_value_from_series


def set_amounts_to_numeric(df, is_positive=True):
    fields = ['amount', 'originalAmount']

    for field in fields:
        df_field_to_numeric_with_sign(df, field, is_positive)


def remove_already_present_id(df, account, limit=None):
    data_account = read_data()
    data_account = data_account[data_account['account'] == account]
    if limit:
        data_account = data_account.head(limit)
    present_ids = data_account['id']
    return df[df['id'].isin(present_ids) == False]


def missing_valid_amount(df):
    try:
        valid_amount = pd.isnull(df['amount']) == False
        # valid_original = (pd.isnull(df['originalAmount']) == False) & (pd.isnull(df['originalCurrency']) == False)
        # amounts = pd.DataFrame({'valid_amount': valid_amount, 'valid_original': valid_original})
        return not valid_amount.any(axis=None)  # amounts.any(axis=None)
    except KeyError:
        return True


def missing_mandatory_field(df):
    try:
        missing_fields = pd.DataFrame({field: pd.isnull(df[field]) for field in data_columns_mandatory_fields})
        return missing_fields.any(axis=None)
    except KeyError:
        return True


def get_bank_name_from_id(id):
    transaction = filter_df_on_id(read_data(), id)
    return get_first_value_from_series(get_one_field(transaction, 'bank_name'))


import pandas as pd
from numpy import NaN

from arlo.operations.data_operations import set_amounts_to_numeric
from arlo.operations.date_operations import timestamp_to_datetime, string_to_datetime, angular_string_to_timestamp, \
    datetime_to_timestamp, now
from arlo.operations.df_operations import drop_other_columns, add_prefix_to_column, remove_invalid_ids, \
    apply_function_to_field_overrule, add_field_with_default_value, sort_df_by_descending_date, \
    apply_function_to_field_no_overrule, assign_new_column, disable_chained_assignment_warning, \
    enable_chained_assignment_warning, assign_value_to_empty_in_existing_column, both_series_are_true, get_one_field, \
    assign_value_to_loc
from arlo.operations.formatting import make_bank_name
from arlo.operations.types_operations import encode_id, clean_parenthesis
from arlo.parameters.param import *
from arlo.tools.autofill_df import add_new_column_autofilled, fill_existing_column_with_autofill
from arlo.tools.cycle_manager import date_to_cycle
from read_write.file_manager import default_value
from read_write.writer import write_df_to_csv


def create_id(df):
    disable_chained_assignment_warning()
    if 'timestamp' not in df.columns:
        apply_function_to_field_overrule(df, 'date', datetime_to_timestamp, destination='timestamp')
    df['id'] = df['name']
    df['id'] += '*' + (1000000*df['timestamp']).astype(int).astype(str)
    df['id'] += '*' + (100*df['amount'].fillna('0').astype(float)).astype(int).astype(str)
    df['id'] += '*' + df['account']
    apply_function_to_field_overrule(df, 'id', encode_id)
    enable_chained_assignment_warning()


def fill_columns_with_default_values(df):
    for field_name in default_values:
        assign_value_to_empty_in_existing_column(df, field_name, default_values[field_name])


def add_missing_data_columns(df):
    for column_name in set(data_columns) - set(df.columns):
        df.insert(0, column_name, NaN)


def add_missing_deposit_columns(df):
    for column_name in set(deposit_columns) - set(df.columns):
        df.insert(0, column_name, NaN)


def format_lunchr_df(lunchr_df):
    lunchr_df.rename(columns=lunchr_dictionary, inplace=True)
    add_missing_data_columns(lunchr_df)

    add_prefix_to_column(lunchr_df, lunchr_id_prefix, 'id')

    remove_invalid_ids(lunchr_df)

    apply_function_to_field_overrule(lunchr_df, 'date', string_to_datetime)
    apply_function_to_field_overrule(lunchr_df, 'date', date_to_cycle, destination='cycle')
    apply_function_to_field_overrule(lunchr_df, 'bank_name', str.upper)

    fill_columns_with_default_values(lunchr_df)

    add_field_with_default_value(lunchr_df, 'account', lunchr_account_name)
    add_field_with_default_value(lunchr_df, "originalAmount", '')
    add_field_with_default_value(lunchr_df, 'originalCurrency', '')

    add_new_column_autofilled(lunchr_df, 'bank_name', 'name', star_fill=True)
    add_new_column_autofilled(lunchr_df, 'name', 'category')
    add_new_column_autofilled(lunchr_df, 'lunchr_type', 'type', star_fill=True)

    sort_df_by_descending_date(lunchr_df)
    drop_other_columns(lunchr_df, data_columns)


def format_n26_df(n26_df, account):
    n26_df['bank_name'] = n26_df.replace(NaN, '').apply(lambda row: make_bank_name(row), axis=1)

    _remove_original_amount_when_euro(n26_df)

    add_field_with_default_value(n26_df, 'account', account)
    add_missing_data_columns(n26_df)

    apply_function_to_field_overrule(n26_df, 'visibleTS', timestamp_to_datetime, destination='date')
    apply_function_to_field_overrule(n26_df, 'date', date_to_cycle, destination='cycle')

    fill_columns_with_default_values(n26_df)

    add_new_column_autofilled(n26_df, 'bank_name', 'name', star_fill=True)
    add_new_column_autofilled(n26_df, 'name', 'category')

    write_df_to_csv(n26_df,
                    directory + 'data/input_n26/' + account + '_' + now().strftime('%Y_%m_%d_%a_%Hh%M') + '.csv')

    return n26_df


def format_manual_transaction(man_df):
    add_missing_data_columns(man_df)

    apply_function_to_field_overrule(man_df, 'angular_date', angular_string_to_timestamp, destination='timestamp')
    apply_function_to_field_overrule(man_df, 'timestamp', timestamp_to_datetime, destination='date')
    apply_function_to_field_no_overrule(man_df, 'date', date_to_cycle, destination='cycle')

    fill_existing_column_with_autofill(man_df, 'account', 'type')
    fill_existing_column_with_autofill(man_df, 'name', 'category')

    set_amounts_to_numeric(man_df, (man_df["isCredit"] == "true").all())

    fill_columns_with_default_values(man_df)
    create_id(man_df)

    drop_other_columns(man_df, data_columns)


def format_recurring_transaction(rec_df):
    add_missing_data_columns(rec_df)
    apply_function_to_field_overrule(rec_df, 'date', angular_string_to_timestamp, destination='timestamp')
    apply_function_to_field_overrule(rec_df, 'timestamp', timestamp_to_datetime, destination='date')
    apply_function_to_field_no_overrule(rec_df, 'date', date_to_cycle, destination='cycle')

    fill_existing_column_with_autofill(rec_df, 'account', 'type')
    fill_existing_column_with_autofill(rec_df, 'name', 'category')

    set_amounts_to_numeric(rec_df, is_positive=False)
    add_prefix_to_column(rec_df, 'rec', 'type')

    fill_columns_with_default_values(rec_df)

    create_id(rec_df)
    drop_other_columns(rec_df, data_columns)


def format_deposit_df(dep_df):
    add_missing_deposit_columns(dep_df)

    add_field_with_default_value(dep_df, 'account', 'HB')
    apply_function_to_field_overrule(dep_df, 'angular_date', angular_string_to_timestamp, destination='timestamp')
    apply_function_to_field_overrule(dep_df, 'timestamp', timestamp_to_datetime, destination='date')
    apply_function_to_field_no_overrule(dep_df, 'date', date_to_cycle, destination='cycle')
    apply_function_to_field_overrule(dep_df, 'name', clean_parenthesis, destination='bank_name')

    fill_existing_column_with_autofill(dep_df, 'name', 'category')

    create_id(dep_df)
    return dep_df[deposit_columns]


def format_for_front(data):
    add_new_column_autofilled(data, 'type', 'method')
    add_linked_column(data)
    add_pending_column(data)
    add_manual_column(data)


def _remove_original_amount_when_euro(df):
    original_amount_is_euro = get_one_field(df, 'originalCurrency') == 'EUR'
    assign_value_to_loc(df, original_amount_is_euro, 'originalCurrency', NaN)
    assign_value_to_loc(df, original_amount_is_euro, 'originalAmount', NaN)


def _calculate_pending_column(data):
    return both_series_are_true(data['type'] == 'AA', data['link'] == default_value('link'))


def _calculate_manual_column(data):
    return data['account'].isin(['T_N26', 'J_N26', 'lunchr']) == False


def _calculate_refund_column(data):
    return both_series_are_true(data['type'].isin(['AE', 'AV']), data['link'] == default_value('link'))


def add_pending_column(data):
    assign_new_column(data, 'pending', _calculate_pending_column(data))


def add_linked_column(data):
    assign_new_column(data, 'linked', data['link'] != '-')


def add_manual_column(data):
    assign_new_column(data, 'manual', _calculate_manual_column(data))


def add_refund_column(data):
    assign_new_column(data, 'refund', _calculate_refund_column(data))


def turn_deposit_data_into_df(deposit_data):
    how_many = len(deposit_data) // 3
    actives = [False for _ in range(how_many)]
    amounts = [0 for _ in range(how_many)]
    names = ['' for _ in range(how_many)]
    ang_date = deposit_data['angular_date'] if deposit_data['angular_date'] else None
    for key, item in deposit_data.items():
        if key[:2] in ['na', 'ac', 'am']:
            key_id = int(key.split('_')[1])
            if key[0] == 'n':
                names[key_id] = item if item else ""
            elif key[:2] == 'ac':
                actives[key_id] = item
            else:
                amounts[key_id] = item
    deposit_df = pd.DataFrame({'amount': amounts, 'name': names, 'angular_date': ang_date})
    return deposit_df[actives]

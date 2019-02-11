import pandas as pd

from arlo.format.date_operations import date_to_cycle, date_now


def sort_df_by_descending_date(df):
    return df.sort_values("date", ascending=False).reset_index(drop=True)


def make_empty_dataframe_based_on_this(df):
    column_names = list(df.head(0))
    data_types = df.dtypes

    empty_df = pd.DataFrame(index=None)
    for col, dtype in zip(column_names, data_types):
        empty_df[col] = pd.Series(dtype=dtype)
    return empty_df


def get_pending_transactions(df):
    return df[df['pending'] == True]


def get_refund_transactions(df):
    refunds = df[df['type'].isin(['AV', 'AE'])]
    refunds = refunds[refunds['link'] == '-']
    return refunds


def apply_function_to_field_no_overrule(df, field, function, destination=''):
    if not destination:
        destination = field

    calculated_values = df[field].apply(function)

    if destination not in df.columns.values:
        df[destination] = calculated_values
    else:
        df.loc[(pd.isnull(df[destination]), destination)] = calculated_values


def set_field_value_no_overrule(df, field, value):
    df.loc[(pd.isnull(df[field]))] = value


def apply_function_to_field_overrule(df, field, function):
    df[field] = df[field].apply(function)


def add_field_with_default_value(df, field, value):
    df[field] = value


def get_ids(df):
    return set(df['id'])


def filter_df_one_value(df, field_name, field_value):
    return df[df[field_name] == field_value]


def filter_df_several_values(df, field_name, field_values):
    return df[df[field_name].isin(field_values)]


def df_is_not_empty(df):
    return df.shape[0] > 0


def extract_line_from_df(index, df):
    line = df.loc[index]
    df.drop(index, inplace=True)
    return line


def change_field_on_several_ids_to_value(df, ids, field_name, field_value):
    df.loc[df['id'].isin(ids), [field_name]] = field_value


def change_field_on_single_id_to_value(df, id, field_name, field_value):
    df.loc[df['id'] == id, [field_name]] = field_value


def read_file_to_df(filename):
    return pd.read_csv(filename)


def result_function_applied_to_field(df, field_name, function):
    return function(df[field_name])


def get_one_field(df, field_name):
    return df[field_name]


def how_many_rows(df):
    return df.shape[0]


def filter_df_on_cycle(df, cycle):
    if cycle == 'all':
        return df

    return df[df['cycle'] == cycle]
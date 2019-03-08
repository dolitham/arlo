from arlo.format.df_operations import sort_df_by_descending_date, change_field_on_several_ids_to_value, concat_lines
from arlo.parameters.param import column_names, directory
from arlo.read_write.reader import read_df_file
from arlo.read_write.writer import write_df_to_csv

data_file = directory + "data.csv"
last_update_file = directory + "last_update.txt"


def read_data():
    return read_data_from_file(data_file)


def read_data_from_file(filename):
    data = read_df_file(filename, parse_dates=['date'])
    return data.dropna(how='all')


def save_data(data):
    save_data_in_file(data, data_file)


def save_data_in_file(data, filename):
    data.dropna(how='all', inplace=True)
    data.drop_duplicates(inplace=True)
    sort_df_by_descending_date(data)
    write_df_to_csv(data[column_names], filename, index=False)


def set_field_to_value_on_ids(ids, field_name, field_value):
    data = read_data()
    change_field_on_several_ids_to_value(data, ids, field_name, field_value)
    save_data(data)


def change_last_update_to_this_date(date):
    with open(last_update_file, mode='w') as file:
        file.write("%s" % date)


def get_last_update_string():
    try:
        with open(last_update_file, mode='r') as file:
            return file.read()
    except FileNotFoundError:
        return "1900-01-01 01:00:00.0"


def add_new_data(new_data):
    data = concat_lines([read_data(), new_data])
    save_data(data)


def get_field_data(field_name):
    data = read_data()
    return data[field_name]


def read_series(filename, parse_dates=False):
    return read_df_file(filename, sep=';', index_col=0, squeeze=True, parse_dates=parse_dates)


def write_dictionary_to_file(dictionary, filename):
    write_df_to_csv(dictionary, filename)

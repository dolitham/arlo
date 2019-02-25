from arlo.format.df_operations import assign_new_column, series_dictioname
from arlo.parameters.param import directory
from arlo.read_write.fileManager import read_series, write_dictionary_to_file


def autofill_directory(filename):
    return directory + 'autofill/' + filename + '.csv'


def read_autofill_dictionary(dictioname):
    return read_series(autofill_directory(dictioname))


def autofill_series(series, dictioname, star_fill=False):
    dictionary = read_autofill_dictionary(dictioname)
    dictionary.index = dictionary.index.str.upper()
    default_fill = '**' + series.str.title() + '**' if star_fill else '-'
    return series.str.upper().map(dictionary).fillna(default_fill)


def add_autofilled_column(data, column_from, column_to, star_fill=False):
    dictioname = column_from + '-to-' + column_to
    column_content = autofill_series(data[column_from], dictioname, star_fill)
    assign_new_column(data, column_to, column_content)


def clean_dictionary(dictionary):
    dictionary = dictionary.reset_index().drop_duplicates()
    dictionary = dictionary.set_index(dictionary.columns.tolist()[0]).squeeze()
    return dictionary.sort_index()


def write_autofill_dictionary(dictionary):
    dictioname = series_dictioname(dictionary)
    dictionary = clean_dictionary(dictionary)
    write_dictionary_to_file(dictionary, autofill_directory(dictioname))

#%% PARAMETERS

from arlo.operations.df_operations import add_field_with_default_value, get_one_field, \
    change_field_on_several_indexes_to_value, assign_new_column, select_columns, drop_columns
from arlo.operations.series_operations import apply_function, is_negative

sign_name, amount_name, o_amount_name, currency_name = 'link_sign', 'link_amount', 'link_o_amount', 'link_currency'

name_field, account_field, amount_field, o_amount_field, o_currency_field = 'bank_name', 'account', 'amount', 'originalAmount', 'originalCurrency'

sep_link_ids = "__"

# %% CALCULATED PARAMETERS

fields_link_ids = dict({'link_id': [sign_name, amount_name, name_field, account_field],
                        'link_id_no_name': [sign_name, amount_name, account_field],
                        'link_id_original_and_name': [sign_name, currency_name, o_amount_name, name_field,
                                                      account_field],
                        'link_id_no_amount': [sign_name, name_field, account_field],
                        'link_id_only_original': [sign_name, currency_name, o_amount_name, account_field]})

link_id_columns = fields_link_ids.keys()


#%% COLUMNS TOOLS

def add_the_sign_to_df(df, normal_sign, reverse_sign):
    add_field_with_default_value(df, sign_name, normal_sign)
    negative_amounts = is_negative(get_one_field(df, amount_field))
    change_field_on_several_indexes_to_value(df, negative_amounts, sign_name, reverse_sign)


def add_the_amount_to_df(df):
    def turn_amount_to_string(series):
        return (100*series.fillna(0)).abs().astype(int).astype(str)
    the_amounts = turn_amount_to_string(get_one_field(df, amount_field))
    assign_new_column(df, amount_name, the_amounts)

    the_o_currency = get_one_field(df, o_currency_field).fillna('EUR')
    assign_new_column(df, currency_name, the_o_currency)

    the_o_amounts = (100 * get_one_field(df, o_amount_field).fillna(get_one_field(df, amount_field))).abs().astype(
        int).astype(str)
    assign_new_column(df, o_amount_name, the_o_amounts)



def add_link_fields(df):
    def join_str(x):
        return sep_link_ids.join(x)

    for field_name, fields in fields_link_ids.items():
        values = apply_function(select_columns(df, fields), join_str).astype(str)
        assign_new_column(df, field_name, values)


def opposite_link_id(link_id):
    replacement_sign = dict({'-': '+', '+': '-'})
    return replacement_sign[link_id[0]] + link_id[1:]


#%%
def add_link_ids(df, normal_sign, reverse_sign):
    add_the_sign_to_df(df, normal_sign, reverse_sign)
    add_the_amount_to_df(df)
    add_link_fields(df)
    drop_columns(df, [sign_name, amount_name, o_amount_name])


def remove_link_ids(df):
    drop_columns(df, link_id_columns)

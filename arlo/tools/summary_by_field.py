from arlo.operations.df_operations import df_is_not_empty, assign_new_column, concat_columns, empty_series, df_is_empty, \
    filter_df_not_these_values, select_columns, concat_lines, filter_df_on_bools, column_is_null, \
    add_column_with_value, reverse_amount
from arlo.operations.series_operations import positive_part, ceil_series, floor_series
from arlo.parameters.column_names import category_col, amount_euro_col, cycle_col, deposit_name_col, account_col
from arlo.parameters.param import budgets_filename, no_recap_categories, deposit_account
from arlo.read_write.reader import read_df_file
from arlo.read_write.select_data import get_data_from_cycle, get_deposit_debits_from_cycle
from arlo.tools.cycle_manager import decode_cycle

"""
def get_euro_amount(row, exchange_rate):
    if math.isnan(row.loc['amount']):
        return row.loc['originalAmount'] * exchange_rate
    return row.loc['amount']
"""

budgets_col = 'budget'


def group_amount_by(df, field_name):
    df = df[[field_name, amount_euro_col]]
    return df.groupby(field_name).apply(lambda x: x.sum(skipna=False))[amount_euro_col]


def sum_no_skip_na(x):
    return x.sum(skipna=False)


def group_by_field(data, field_name):
    if df_is_empty(data):
        return empty_series()
    data = data[[amount_euro_col, field_name]]
    summary = (data.groupby([field_name])).agg({amount_euro_col: sum_no_skip_na})

    return summary


def get_budgets(cycle):
    budgets = read_df_file(budgets_filename, sep=';')
    if cycle != 'all':
        budgets = budgets[budgets[cycle_col] == decode_cycle(cycle)]

    if df_is_not_empty(budgets):
        budgets = budgets.groupby(category_col).apply(sum)[amount_euro_col]
        return budgets.rename(budgets_col)

    return empty_series().rename(budgets_col)


"""
def get_exchange_rate(data):
    cash_withdrawals = data[data['type'] == 'CW']
    if cash_withdrawals.shape[0] == 0:
        return 1
    sum_currency = data['originalAmount'].sum()
    sum_euro = data['amount'].sum()
    try:
        return sum_euro / sum_currency
    except ZeroDivisionError:
        return 1
"""


def recap_by_cat(cycle, round_it=True):
    data = get_data_from_cycle(cycle)
    deposit = get_deposit_debits_from_cycle(cycle)

    field_name = category_col
    selected_columns = [amount_euro_col, field_name]
    data = filter_df_on_bools(data, column_is_null(data, deposit_name_col))
    data = select_columns(data, selected_columns)
    deposit = select_columns(deposit, selected_columns)

    all_output = concat_lines([data, deposit])
    if df_is_empty(all_output):
        return '{}'

    spent = group_by_field(all_output, category_col)
    if df_is_empty(spent):
        return '{}'

    recap = concat_columns([spent, get_budgets(cycle)], keep_index_name=True).round(2).fillna(0).reset_index()
    recap = filter_df_not_these_values(recap, category_col, no_recap_categories)

    over = positive_part(- recap[amount_euro_col] - recap[budgets_col])
    remaining = positive_part(recap[budgets_col] + recap[amount_euro_col])
    spent = positive_part(- recap[amount_euro_col] - over)

    assign_new_column(recap, 'over', ceil_series(over) if round_it else over)
    assign_new_column(recap, 'remaining', floor_series(remaining) if round_it else remaining)
    assign_new_column(recap, 'spent', ceil_series(spent) if round_it else spent)

    return recap


def recap_by_account(cycle):
    field_name = account_col
    selected_columns = [amount_euro_col, field_name]

    cycle = decode_cycle(cycle)
    data = get_data_from_cycle(cycle)

    if cycle != 'all':
        is_deposit = column_is_null(data, deposit_name_col) == False
        deposit_transactions = filter_df_on_bools(data, is_deposit)

        add_column_with_value(deposit_transactions, account_col, deposit_account)
        reverse_amount(deposit_transactions)

        data = select_columns(concat_lines([data, deposit_transactions]), selected_columns)

        deposit = get_deposit_debits_from_cycle(cycle)
        data = concat_lines([deposit, data])

    all_outputs = select_columns(data, selected_columns)
    return group_by_field(all_outputs, field_name).round(decimals=2)

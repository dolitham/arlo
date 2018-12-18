import codecs
import json
import pandas as pd



data_file = "./data/data.csv"


def sort_df_by_descending_date(df):
    return df.sort_values("date", ascending=False).reset_index(drop=True)


def read_data(filename = data_file):
    data = pd.read_csv(filename, na_values=' ')
    data['date'] = pd.to_datetime(data['date'])
    data['pending'] = data.apply(lambda row: row['type'] == 'AA' and row['link'] == '-', axis=1)
    return data


def read_dico(filename):
    dictionary = dict()
    f = codecs.open(filename,'r',encoding='utf8')
    for line in f:
        try:
            line = line.replace('\n', '')
            a, b = line.split(',')
            dictionary[a] = b
        except ValueError:
            pass
    f.close()
    return dictionary


def write_sorted_dico(dico, filename):
    f = open(filename, 'w')
    for d in sorted(dico, key=lambda k: dico[k][1].lower() + dico[k][0].lower()):
        f.write(d + "," + ','.join(dico[d]) + '\n')
    f.close()


def save_data(data, filename = data_file):
    data = sort_df_by_descending_date(data)
    data.to_csv(filename, index=False)


def change_one_field_on_ids(transaction_ids, field_name, field_value):
    data = read_data()
    data.loc[data['id'].isin(transaction_ids), [field_name]] = field_value
    save_data(data_file, data)


def change_last_update_to_now():
    with open("last_update.txt", mode='w') as file:
        file.write("%s" % pd.datetime.now())


def get_delay_since_last_update():
    print('BEGIN DELAY')
    try:
        with open("last_update.txt", mode='r') as file:
            last_update = file.read()
            delta = pd.datetime.now() - pd.datetime.strptime(last_update, '%Y-%m-%d %H:%M:%S.%f')
            print(delta)
            return delta.total_seconds()//60
    except FileNotFoundError:
        return 1000000


def add_data_line(line):
    with open(data_file, 'r+') as f:
        content = f.readlines()
        content.insert(1, line + "\n")
        f.seek(0)
        f.write("".join(content))


def write_json_dict(filename, dico):
    with open(filename, 'w') as f:
        json.dump(dico, f, separators=[",\n", ":"])


def read_json_dict(filename):
    with open(filename, "r") as read_file:
        data = json.load(read_file)
    return data


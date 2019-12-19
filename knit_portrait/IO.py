import numpy as np
import json


def save_string_order(string_order, filename='./string_order.csv'):
    np.savetxt(filename, np.asarray([[ind, val[0], val[1]] for ind, val in enumerate(string_order)]),
               delimiter=',', fmt='%i')


def load_string_order(filename='./string_order.csv'):
    return np.loadtxt(filename, delimiter=',').astype(int)


def load_config(filename='./config.json'):
    with open(filename) as json_file:
        return json.load(json_file)


def save_config(config, filename='./config.json'):
    with open(filename, 'w') as outfile:
        json.dump(config, outfile)
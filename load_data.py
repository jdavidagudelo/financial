import pickle
from datetime import datetime
from dateutil import parser
import pandas as pd
from statsmodels.tsa.arima_model import ARIMA
from matplotlib import pyplot as plt


def load_pickle(file_name):
    with open(file_name, mode='rb') as pickle_file:
        data = pickle.load(pickle_file)
    result = []
    epoch = datetime.utcfromtimestamp(0)
    for value in data:
        dt = parser.parse(value.get('date'))
        timestamp = int((dt - epoch).total_seconds() * 1000.0)
        v = value.get('value')
        v = v.replace(',', '')
        v = float(v)
        result.append({'timestamp': timestamp, 'value': v})
    with open(file_name, mode='wb') as pickle_file:
        pickle.dump(result, pickle_file)
    return result


def load_data_to_pandas(file_name, column_name):
    with open(file_name, mode='rb') as pickle_file:
        data = pickle.load(pickle_file)
    series = pd.Series(data=[d['value'] for d in data], index=[datetime.utcfromtimestamp(d['timestamp'] / 1000) for d in data],
                       name=column_name)
    return series


def merge_time_series(s1, s2):
    return pd.merge(left=s1, right=s2, left_index=True, right_index=True)


def create_data():
    data_names = ['dow_jones', 'euro', 'igbc', 'mexico', 'sao_paulo', 'trm', 'bancolombia']
    merged = load_data_to_pandas('pickle_data/{0}.pickle'.format('uvr'), 'uvr')
    merged = merged.to_frame('uvr')
    for data_name in data_names:
        data = load_data_to_pandas('pickle_data/{0}.pickle'.format(data_name), data_name)
        data = data.to_frame(data_name)
        merged = merge_time_series(merged, data)
    return merged


def arima_plot(data_name, predicted_count=200):
    current_data = load_data_to_pandas('pickle_data/{0}.pickle'.format(data_name), data_name)
    X = current_data.values
    size = int(len(X) * 1)
    train, test = X[0:size], X[size:len(X)]
    history = [x for x in train]
    predictions = list()
    for t in range(predicted_count):
        model = ARIMA(history, order=(5,1,0))
        model_fit = model.fit(disp=0)
        output = model_fit.forecast()
        that = output[0]
        predictions.append(that)
        # obs = test[t]
        history.append(that)
        print('predicted=%f, expected=%f' % (that, that))
    #plt.plot(test)
    plt.plot(predictions, color='red')
    plt.show()


def update_csv(file_name):
    pass
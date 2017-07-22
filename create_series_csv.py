import csv
from dateutil import parser
import pandas as pd
import math
import os
from scipy.stats.stats import pearsonr

CSV_ROOT = 'xls/csv/'
DIVIDEND_ROOT = 'xls/dividends/'


def merge_time_series(s1, s2, on='date'):
    return pd.merge(left=s1, right=s2, on=on)


def convert_float(value) -> float:
    return float(value)


def get_stock_dividend_file_name_from_quote(quote):
    return '{0}{1}.csv'.format(DIVIDEND_ROOT, quote)


def get_stock_file_name_from_quote(quote):
    return '{0}{1}.csv'.format(CSV_ROOT, quote)


def downside_deviation(daily_returns, mar=-0.05):
    valid_values = [d for d in daily_returns if d >= mar]
    count = len(valid_values)
    return math.sqrt(sum([(d - mar) ** 2 for d in valid_values]) / count)


def sharpe_ratio_from_file(file_name, data_type='last', start_date=None, end_date=None):
    daily_returns = get_daily_returns(file_name, data_type, start_date, end_date)
    return sharpe_ratio(daily_returns)


def sortino_ratio(daily_returns, mar=-0.05):
    period = len(daily_returns)
    df = pd.DataFrame(daily_returns)
    return float(math.sqrt(period) * df.mean() / downside_deviation(daily_returns, mar))


def sharpe_ratio(daily_returns):
    period = len(daily_returns)
    df = pd.DataFrame(daily_returns)
    return float(math.sqrt(period) * df.mean() / df.std())


def get_daily_returns(file_name, data_type='last', start_date=None, end_date=None):
    dictionary, index = load_series(file_name, start_date, end_date)
    data = dictionary.get(data_type)
    daily_returns = []
    for i in range(1, len(data)):
        daily_returns.append(data[i] / data[i - 1] - 1)
    return daily_returns


def optimize_four_quotes(start_date, end_date, quotes, delta=0.1, function=None):
    function = sharpe_ratio if function is None else function
    w1 = 0.0
    max_sharpe_ratio = None
    max_weights = None
    expected_return = None
    while w1 <= 1.0:
        w2 = 0.0
        while w1 + w2 <= 1.0:
            w3 = 0.0
            while w1 + w2 + w3 <= 1.0:
                w4 = 1.0 - w1 - w2 - w3
                current_sharpe_ratio, current_return = simulate(start_date, end_date, quotes, [w1, w2, w3, w4],
                                                                function=function)
                if max_sharpe_ratio is None:
                    max_sharpe_ratio = current_sharpe_ratio
                    expected_return = current_return
                if current_sharpe_ratio >= max_sharpe_ratio:
                    max_sharpe_ratio = current_sharpe_ratio
                    max_weights = (w1, w2, w3, w4)
                    expected_return = current_return
                w3 += delta
            w2 += delta
        w1 += delta
    return max_sharpe_ratio, max_weights, expected_return


def optimize_three_quotes(start_date, end_date, quotes, delta=0.1, function=None):
    function = sharpe_ratio if function is None else function
    w1 = 0.0
    max_sharpe_ratio = None
    max_weights = None
    expected_return = None
    while w1 <= 1.0:
        w2 = 0.0
        while w1 + w2 <= 1.0:
            w3 = 1.0 - w1 - w2
            current_sharpe_ratio, current_return = simulate(start_date, end_date, quotes, [w1, w2, w3],
                                                            function=function)
            if max_sharpe_ratio is None:
                max_sharpe_ratio = current_sharpe_ratio
                expected_return = current_return
            if current_sharpe_ratio >= max_sharpe_ratio:
                max_sharpe_ratio = current_sharpe_ratio
                max_weights = (w1, w2, w3)
                expected_return = current_return
            w2 += delta
        w1 += delta
    return max_sharpe_ratio, max_weights, expected_return


def optimize_two_quotes(start_date, end_date, quotes, delta=0.1, function=None):
    function = sharpe_ratio if function is None else function
    w1 = 0.0
    max_sharpe_ratio = None
    max_weights = None
    expected_return = None
    while w1 <= 1.0:
        w2 = 1.0 - w1
        current_sharpe_ratio, current_return = simulate(start_date, end_date, quotes, [w1, w2],
                                                        function=function)
        if max_sharpe_ratio is None:
            max_sharpe_ratio = current_sharpe_ratio
            expected_return = current_return
        if current_sharpe_ratio >= max_sharpe_ratio:
            max_sharpe_ratio = current_sharpe_ratio
            max_weights = (w1, w2)
            expected_return = current_return
        w1 += delta
    return max_sharpe_ratio, max_weights, expected_return


def simulate(start_date, end_date, quotes, weights, data_type='last', function=None):
    if function is None:
        function = sharpe_ratio
    merged = None
    for quote in quotes:
        data_frame = load_pandas_data_frame_from_csv(quote=quote, start_date=start_date,
                                                     end_date=end_date, data_type=data_type)
        if merged is None:
            merged = data_frame
        else:
            merged = merge_time_series(merged, data_frame)
    daily_returns = []
    last_values = None
    for value in merged.iterrows():
        values = value[1]
        if last_values is None:
            last_values = {quote: getattr(values, quote) for quote in quotes}
        else:
            day_return = 0.0
            for i in range(0, len(quotes)):
                quote = quotes[i]
                weight = weights[i]
                current_value = getattr(values, quote)
                previous_value = last_values.get(quote)
                day_return += ((current_value / previous_value) - 1.0) * weight
            daily_returns.append(day_return)
            last_values = {quote: getattr(values, quote) for quote in quotes}
    return function(daily_returns), sum(daily_returns)


def load_series(quote, start_date=None, end_date=None):
    result = []
    with open(get_stock_file_name_from_quote(quote)) as f:
        x = csv.reader(f)
        for line in x:
            result.append(line)
    result = result[1:]

    result = [r for r in result if start_date <= parser.parse(r[0]) <= end_date]
    dividends = load_dividends_series(quote, start_date, end_date)
    for i in range(len(result)):
        current_date = result[i][0]
        dividend = [d for d in dividends if d[0] == current_date]
        if len(dividend) == 0:
            continue
        result[i][4] = convert_float(result[i][4])
        result[i][4] += convert_float(dividend[0][1])
    dictionary = {
        'last': [convert_float(r[4]) for r in result],
        'max': [convert_float(r[2]) for r in result],
        'min': [convert_float(r[3]) for r in result],
        'open': [convert_float(r[1]) for r in result],
        'volume': [r[6] for r in result],
    }
    index = [parser.parse(r[0]) for r in result]
    return dictionary, index


def load_dividends_series(quote, start_date=None, end_date=None):
    result = []
    try:
        with open(get_stock_dividend_file_name_from_quote(quote)) as f:
            x = csv.reader(f)
            for line in x:
                result.append(line)
        result = result[1:]
        result = [r for r in result if start_date <= parser.parse(r[0]) <= end_date]
    except FileNotFoundError:
        pass
    return result


def load_dividends(file_name, start_date=None, end_date=None):
    result = []
    with open(file_name) as f:
        x = csv.reader(f)
        for line in x:
            result.append(line)
    result = result[1:]
    result = [r for r in result if start_date <= parser.parse(r[0]) <= end_date]
    return sum([convert_float(r[1]) for r in result])


def load_pandas_data_frame_from_csv(quote='value', data_type='last', start_date=None, end_date=None):
    dictionary, index = load_series(quote, start_date, end_date)
    data_frame_data = []
    for i in range(0, len(index)):
        data_frame_data.append({'date': index[i], quote: dictionary.get(data_type)[i]})
    return pd.DataFrame.from_records(data_frame_data)


def load_pandas_from_csv(quote, data_type='last', start_date=None, end_date=None):
    dictionary, index = load_series(quote, start_date, end_date)
    return pd.Series(dictionary.get(data_type, []), index=index)


def get_quotes_count(start_date, end_date, data_type='last'):
    quotes = get_available_quotes()
    result = []
    for quote in quotes:
        data_frame = load_pandas_data_frame_from_csv(quote=quote, start_date=start_date,
                                                     end_date=end_date, data_type=data_type)
        result.append({'count': int(getattr(data_frame.count(), quote)), 'name': quote})
    return result


def get_available_quotes():
    result = []
    for file in os.walk(CSV_ROOT):
        result = file[2]
    return [r.split('.')[0] for r in result]


def get_sorted_quotes(start_date, end_date, function=None):
    function = sharpe_ratio if function is None else function
    quotes = get_available_quotes()
    result = []
    for quote in quotes:
        expected_ratio, expected_return = simulate(start_date, end_date, [quote], [1.0], function=function)
        result.append({'name': quote,
                       'ratio': expected_ratio,
                       'return': expected_return})
    result.sort(key=lambda v: -v.get('ratio'))
    return result


def get_best_four(start_date, end_date, delta=0.1, function=None):
    function = sharpe_ratio if function is None else function
    quotes = get_sorted_quotes(start_date, end_date, function=function)
    max_sharpe_ratio = None
    max_weights = None
    best_return = None
    max_quotes = None
    quotes = [q.get('name') for q in quotes]
    for i in range(len(quotes)):
        for j in range(i + 1, len(quotes)):
            for k in range(j + 1, len(quotes)):
                for l in range(k + 1, len(quotes)):
                    current_sharpe_ratio, weights, expected_return = optimize_four_quotes(
                        start_date, end_date, [quotes[i], quotes[j], quotes[k], quotes[l]],
                        delta=delta, function=function)
                    if max_sharpe_ratio is None:
                        max_sharpe_ratio = current_sharpe_ratio
                    if current_sharpe_ratio >= max_sharpe_ratio:
                        max_sharpe_ratio = current_sharpe_ratio
                        max_weights = weights
                        best_return = expected_return
                        max_quotes = [quotes[i], quotes[j], quotes[k], quotes[l]]
                        print([quotes[i], quotes[j], quotes[k], quotes[l]])
                        print(current_sharpe_ratio)
                        print(expected_return)
                        print(weights)
                        print('###############')
    return max_sharpe_ratio, max_weights, best_return, max_quotes


def get_best_three(start_date, end_date, delta=0.1, function=None):
    function = sharpe_ratio if function is None else function
    quotes = get_sorted_quotes(start_date, end_date, function=function)
    max_sharpe_ratio = None
    max_weights = None
    best_return = None
    max_quotes = None
    quotes = [q.get('name') for q in quotes]
    for i in range(len(quotes)):
        for j in range(i + 1, len(quotes)):
            for k in range(j + 1, len(quotes)):
                current_sharpe_ratio, weights, expected_return = optimize_three_quotes(
                    start_date, end_date, [quotes[i], quotes[j], quotes[k]], delta=delta, function=function)
                if max_sharpe_ratio is None:
                    max_sharpe_ratio = current_sharpe_ratio
                if current_sharpe_ratio >= max_sharpe_ratio:
                    max_sharpe_ratio = current_sharpe_ratio
                    max_weights = weights
                    best_return = expected_return
                    max_quotes = [quotes[i], quotes[j], quotes[k]]
                    print([quotes[i], quotes[j], quotes[k]])
                    print(current_sharpe_ratio)
                    print(expected_return)
                    print(weights)
                    print('###############')
    return max_sharpe_ratio, max_weights, best_return, max_quotes


def get_best_pair(start_date, end_date, delta=0.1, function=None):
    function = sharpe_ratio if function is None else function
    quotes = get_sorted_quotes(start_date, end_date, function=function)
    max_sharpe_ratio = None
    max_weights = None
    best_return = None
    max_quotes = None
    quotes = [q.get('name') for q in quotes]
    for i in range(len(quotes)):
        for j in range(i + 1, len(quotes)):
            current_sharpe_ratio, weights, expected_return = optimize_two_quotes(
                start_date, end_date, [quotes[i], quotes[j]], delta=delta, function=function)
            if max_sharpe_ratio is None:
                max_sharpe_ratio = current_sharpe_ratio
            if current_sharpe_ratio >= max_sharpe_ratio:
                max_sharpe_ratio = current_sharpe_ratio
                max_weights = weights
                best_return = expected_return
                max_quotes = [quotes[i], quotes[j]]
                print([quotes[i], quotes[j]])
                print(current_sharpe_ratio)
                print(expected_return)
                print(weights)
                print('###############')
    return max_sharpe_ratio, max_weights, best_return, max_quotes


def update_csv(file_name):
    result = []
    with open(file_name) as f:
        x = csv.reader(f)
        for line in x:
            result.append(line)
    i = 0
    with open(file_name, 'w') as f:
        writer = csv.writer(f)
        for x in result:
            if i > 0:
                valid_date = x[0].split('-')
                valid_date = '{0}/{1}/{2}'.format(valid_date[2], valid_date[1], valid_date[0])
                x[0] = valid_date
            i += 1
            writer.writerow(x)


def fix_csv(quotes):
    for quote in quotes:
        file_name = '{0}{1}.csv'.format(CSV_ROOT, quote)
        result = []
        with open(file_name) as f:
            x = csv.reader(f)
            for line in x:
                result.append(line)
        i = 0
        with open(file_name, 'w') as f:
            writer = csv.writer(f)
            for x in result:
                if i > 0:
                    for j in range(1, len(x)):
                        try:
                            x[j] = convert_float(x[j])
                        except:
                            pass
                i += 1
                writer.writerow(x)


def standard_form_csv(quotes):
    for quote in quotes:
        file_name = '{0}{1}.csv'.format(CSV_ROOT, quote)
        result = []
        with open(file_name) as f:
            x = csv.reader(f)
            for line in x:
                result.append(line)
        i = 0
        with open(file_name, 'w') as f:
            writer = csv.writer(f)
            for x in result:
                if i == 0:
                    current_row = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
                    writer.writerow(current_row)
                    i += 1
                    continue
                current_row = [x[0], x[4], x[2], x[3], x[1], x[1], x[5]]
                writer.writerow(current_row)


def get_correlation(quote1, quote2, start_date, end_date, data_type='last'):
    merged = None
    for quote in [quote1, quote2]:
        data_frame = load_pandas_data_frame_from_csv(quote=quote, start_date=start_date,
                                                     end_date=end_date, data_type=data_type)
        if merged is None:
            merged = data_frame
        else:
            merged = merge_time_series(merged, data_frame)
    return pearsonr(getattr(merged, quote1), getattr(merged, quote2))

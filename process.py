from bs4 import BeautifulSoup
import pickle


def load_file(file_name):
    with open(file_name) as f:
        data = f.read()
    soup = BeautifulSoup(data, 'html.parser')
    r = soup.find_all('partial-response')
    r = r[0]
    r = r.find_all('changes')[0]
    x = r.find_all('update')[0]
    xs = [x for x in x.childGenerator()]
    x2 = xs[2]
    value = '{0}'.format(x2)
    extra = BeautifulSoup(value, 'html.parser')
    l = [x for x in extra.recursiveChildGenerator() if x.name == 'tr']
    l = l[1:]
    data = []
    for tr in l:
        tds = [c for c in tr.childGenerator()]
        date = [c for c in tds[0].childGenerator()][0].text
        value = [c for c in tds[1].childGenerator()][0].text
        data.append({'date': date, 'value': value})
    return data


def load_trm():
    with open('pickle_data/trm.pickle', mode='rb') as pickle_file:
        data = pickle.load(pickle_file)
    return data


def load_euro():
    with open('pickle_data/euro.pickle', mode='rb') as pickle_file:
        data = pickle.load(pickle_file)
    return data


def load_uvr():
    with open('pickle_data/uvr.pickle', mode='rb') as pickle_file:
        data = pickle.load(pickle_file)
    return data


def load_igbc():
    with open('pickle_data/igbc.pickle', mode='rb') as pickle_file:
        data = pickle.load(pickle_file)
    return data

list_trm_files = ['TRM_RESPONSE(2000-2004).txt', 'TRM_RESPONSE(2005-2009).txt',
                  'TRM_RESPONSE(2010-2014).txt', 'TRM_RESPONSE(2015-2017).txt']
with open('pickle_data/trm.pickle', mode='wb') as pickle_file:
    data = []
    for f in list_trm_files:
        data += load_file(f)
    pickle.dump(data, pickle_file)

list_trm_files = ['EURO_RESPONSE(2000-2004).txt', 'EURO_RESPONSE(2005-2009).txt',
                  'EURO_RESPONSE(2010-2014).txt', 'EURO_RESPONSE(2015-2017).txt']
with open('pickle_data/euro.pickle', mode='wb') as pickle_file:
    data = []
    for f in list_trm_files:
        data += load_file(f)
    pickle.dump(data, pickle_file)

list_trm_files = ['UVR_RESPONSE(2000-2004).txt', 'UVR_RESPONSE(2005-2009).txt',
                  'UVR_RESPONSE(2010-2014).txt', 'UVR_RESPONSE(2015-2017).txt']
with open('pickle_data/uvr.pickle', mode='wb') as pickle_file:
    data = []
    for f in list_trm_files:
        data += load_file(f)
    pickle.dump(data, pickle_file)

list_trm_files = ['IGBC(2000-2004).txt', 'IGBC(2005-2009).txt',
                  'IGBC(2010-2014).txt', 'IGBC(2015-2017).txt']
with open('pickle_data/igbc.pickle', mode='wb') as pickle_file:
    data = []
    for f in list_trm_files:
        data += load_file(f)
    pickle.dump(data, pickle_file)

list_trm_files = ['DOW_JONES(2000-2004).txt', 'DOW_JONES(2005-2009).txt',
                  'DOW_JONES(2010-2014).txt', 'DOW_JONES(2015-2017).txt']

with open('pickle_data/dow_jones.pickle', mode='wb') as pickle_file:
    data = []
    for f in list_trm_files:
        data += load_file(f)
    pickle.dump(data, pickle_file)

list_trm_files = ['MEXICO(2000-2004).txt', 'MEXICO(2005-2009).txt',
                  'MEXICO(2010-2014).txt', 'MEXICO(2015-2017).txt']

with open('pickle_data/mexico.pickle', mode='wb') as pickle_file:
    data = []
    for f in list_trm_files:
        data += load_file(f)
    pickle.dump(data, pickle_file)

list_trm_files = ['SAO_PAULO(2000-2004).txt', 'SAO_PAULO(2005-2009).txt',
                  'SAO_PAULO(2010-2014).txt', 'SAO_PAULO(2015-2017).txt']

with open('pickle_data/sao_paulo.pickle', mode='wb') as pickle_file:
    data = []
    for f in list_trm_files:
        data += load_file(f)
    pickle.dump(data, pickle_file)

list_trm_files = ['BANCOLOMBIA(2000-2004).txt', 'BANCOLOMBIA(2005-2009).txt',
                  'BANCOLOMBIA(2010-2014).txt', 'BANCOLOMBIA(2015-2017).txt']

with open('pickle_data/bancolombia.pickle', mode='wb') as pickle_file:
    data = []
    for f in list_trm_files:
        data += load_file(f)
    pickle.dump(data, pickle_file)

import PySimpleGUI as sg
from datetime import date
from breeze_connect import BreezeConnect
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import pandas as pd
from datetime import datetime
from os import getcwd, name
from dateparser import parse
import yfinance as yf
from itertools import batched

'''create list of secureities'''
resp = urlopen("https://directlink.icicidirect.com/NewSecurityMaster/SecurityMaster.zip")
myzip = ZipFile(BytesIO(resp.read()))
file = myzip.namelist()[3]
list_symbols = []
for line in myzip.open(file).readlines():
    list_symbols.append(line)
    #list_symbols.append(line.decode().replace('"','').split(','))
list_symbols = [item.decode().replace('"','').split(',') for item in list_symbols]
df = pd.DataFrame(list_symbols)
headers = df.iloc[0]
df.columns = [headers]
df = df.drop([0])
list_symbols = df[(                ' ShortName',)].tolist()

'''flags for validation of steps'''
bool_connected = False 
bool_request_validity = False

def validate_request(**kwargs) -> bool:
    '''
    input: {'interval': string, 'from_date': datetime string in ISO format,
            'to_date': datetime string in ISO format,
            'stock_code':string,
            'exchange_code':string,
            'product_type':string,
            'expiry_date': datetime string in ISO format,
            'right':string,
            'strike_price':number as a string
            }
    output: True if valid, False and print() error if invalid
    '''
    print('checking request dictionary validity.')
    if (kwargs.get('exchange_code').lower() in ['nfo', 'bso'] and kwargs.get('product_type').lower() not in ['options', 'futures']) or \
         (kwargs.get('exchange_code').lower() not in ['nfo', 'bso'] and kwargs.get('product_type').lower() in ['options', 'futures']):
        print('exchange and product type mismatch')
        return False
    if kwargs.get('product_type').lower() == 'options' and kwargs.get('right').lower() not in ['call', 'put']:
        print('option right not given')
        return False
    if kwargs.get('product_type').lower() in ['options', 'futures'] and isinstance(kwargs.get('expiry_date'), datetime):
        print('expiry date not given for a derivative')
        return False
    if not(isinstance(parse(kwargs.get('from_date')), datetime)) or not(isinstance(parse(kwargs.get('to_date')), datetime)):
        print('either from- or to- dates are not in the right format')
        return False
    if parse(kwargs.get('from_date')) >= parse(kwargs.get('to_date')):
        print('from- date is greater or equal to than to- date')
        return False
    else:
        bool_request_validity= True
        return bool_request_validity

# 2016-01-01 12:11:13 2023-01-01 12:10:53
def split_dates(dtm_from:datetime, dtm_to:datetime, int_interval:int) -> list:
    '''
    input: dt_from and dt_to must be strings in 'YYYY-MM-DD' format
    output: returns a list of datetime.date() object pairs
    '''
    print('getting date batches') #!debug
    try:
        script = yf.Ticker('^NSEI')
        df_nifty =  script.history(start=dtm_from.strftime("%Y-%m-%d") , end=dtm_to.strftime("%Y-%m-%d"))
        file_data = getcwd()+ ('\\' if name =='nt' else '//') + 'YAHOO' + dict_request.get('stock_code')+'_'+ datetime.now().isoformat().replace(':', '-') +'.csv' #!debug
        df_nifty.to_csv(file_data) #!debug
    except Exception as e:
        print(e)
    print('got yahoo data.') #!debug
    list_dates = df_nifty.index.to_list()
    list_dates = [item.to_pydatetime().replace(tzinfo=None) for item in list_dates]
    del df_nifty #don't want to take up unnecessary memory
    int_days_per_batch = int(1000/int_interval) #int(number of days * (candles/day))/(max candles in 1 call) +1
    list_batched_dates = list(batched(list_dates, int_days_per_batch))
    list_batched_dates = [[item[0], item[-1]] for item in list_batched_dates]
    #! start debug
    file_data = getcwd()+ ('\\' if name =='nt' else '//') + 'BATCHED' + dict_request.get('stock_code')+'_'+ datetime.now().isoformat().replace(':', '-') +'.csv'
    file = open(file_data,'w')
    for item in list_batched_dates:
        file.write(str(item)+"\n")
    file.close()
    #! end debug
    list_batched_dates = [[item[0].replace(hour=0, minute=0, second=0), item[-1].replace(hour=23, minute=59, second=59)] for item in list_batched_dates]
    print('done with batching.') #!debug
    return list_batched_dates

tab1_layout =  [[sg.Text('APP KEY'), sg.InputText(default_text='', key='APP_KEY')], 
            [sg.Text('SECRET KEY'), sg.InputText(default_text='',key='SECRET_KEY')],
            [sg.Text('SESSION ID'), sg.InputText(default_text='', key='SESSION_ID')],
            [sg.Button('CONNECT'), sg.Button('DISCONNECT')]
            ]

tab3_layout = [ [sg.Text('Path: '), sg.InputText(default_text=getcwd(), key='-path-')],
                 [sg.Text('Symbol: '), sg.DropDown(values=list_symbols, size=(20,40), key='-SYMBOL-', default_value='NIFTY')],
                [sg.Text('From Date: '), sg.Input(default_text='', key='-FROM_DATE-'), \
                    sg.CalendarButton(button_text='Pick Date', target='-FROM_DATE-', default_date_m_d_y=(date.today().month, date.today().day-1, date.today().year))],
                [sg.Text('To Date: '), sg.Input(default_text='', key='-TO_DATE-'), \
                    sg.CalendarButton(button_text='Pick Date', target='-TO_DATE-', default_date_m_d_y=(date.today().month, date.today().day, date.today().year))],
                [sg.Text('Exchange: '), sg.OptionMenu(values=['NSE', 'NFO', 'BSE', 'BSO', 'MCX'], key='-EXCHANGE-')],
                [sg.Text('Product: '), sg.OptionMenu(values=['CASH', 'FUTURES', 'OPTIONS'], key='-PRODUCT-')],
                [sg.Text('Interval: '), sg.OptionMenu(values=[ "1second", "1minute", "5minute", "30minute", "1day"], default_value='1minute', key='-INTERVAL-')],               
                [sg.Text('Expiry Date: '), sg.Input(default_text='', key='-EXPIRY-'), sg.CalendarButton(button_text='Pick Date', target='-EXPIRY-')],
                [sg.Text('Strike: '), sg.Input(default_text='0', key='-STRIKE-')],
                [sg.Text('Right: '), sg.OptionMenu(values=['CALL', 'PUT'], key='-RIGHT-')],
                [sg.Button(button_text='VALIDATE', key='-VALIDATE-')], [sg.Button(button_text='DOWNLOAD', key='-DOWNLOAD-')]                
             ]

layout = [[sg.TabGroup([[sg.Tab('Connect', tab1_layout), sg.Tab('Get Data', tab3_layout)]])],
              [sg.Output(size=(80, 20), key='-OUTVIEW-')] ,
              [sg.Button(button_text='Clear Output', key='-CLEAR_OUTPUT-')],
              [sg.Button('Close')]]

window = sg.Window('Breeze Order Slicer', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Close': # if user closes window or clicks cancel
        break
    if event == 'CONNECT':
        print('wait.')
        try:
            breeze = BreezeConnect(api_key=values['APP_KEY'])
            breeze.generate_session(api_secret=values['SECRET_KEY'], session_token=values['SESSION_ID'])
            print("connected.")
            bool_connected=True
        except Exception as e:
            print(type(e))
            print(e.args)
            print('**** NOT CONNECTED ****')
    if event == '-VALIDATE-':
        print('validating request')
        dict_request = {'interval':values['-INTERVAL-'],
                        'from_date':parse(values['-FROM_DATE-']).isoformat(),
                        'to_date':parse(values['-TO_DATE-']).isoformat(),
                        'stock_code':values['-SYMBOL-'],
                        'exchange_code':values['-EXCHANGE-'],
                        'product_type':values['-PRODUCT-'],
                        'expiry_date':parse(values['-EXPIRY-']).isoformat(),
                        'right':values['-RIGHT-'],
                        'strike_price':values['-STRIKE-']
                        }
        bool_request_validity = validate_request(**dict_request)
        if bool_request_validity:
            print('request valid. you may click download.')
            print(dict_request)
        else:
            print('invalid request.')
    if event == '-DOWNLOAD-':
        if bool_connected and bool_request_validity:
            # form a dict for a default historical data request
            dict_request = {'interval':values['-INTERVAL-'],
                        'from_date':parse(values['-FROM_DATE-']),   #date is in ISO format
                        'to_date':parse(values['-TO_DATE-']),       #date is in ISO format
                        'stock_code':values['-SYMBOL-'],
                        'exchange_code':values['-EXCHANGE-'],
                        'product_type':values['-PRODUCT-'],
                        'expiry_date':parse(values['-EXPIRY-']).isoformat(),    #date is in ISO format
                        'right':values['-RIGHT-'],
                        'strike_price':values['-STRIKE-']
                        }
            # use split_dates() to create date pairs to place requests
            dict_intervals = {'1second':22500, '1minute':375, '5minute':75, '30minute':13, '1day':1}
            int_interval = dict_intervals.get(dict_request.get('interval'))
            list_date_pairs = split_dates(dict_request.get('from_date'), dict_request.get('to_date'), int_interval)
            int_total_requests = len(list_date_pairs)
            print(f'this will require {int_total_requests} requests')
            # go over the date pairs and store data in list_hist_data[]
            list_hist_data = []
            int_request_count = 1
            for pair in list_date_pairs:
                dict_request['from_date'] = pair[0].strftime('%Y-%m-%d %H:%M:%S')
                dict_request['to_date'] = pair[-1].strftime('%Y-%m-%d %H:%M:%S')
                print(f'request number {int_request_count} out of {int_total_requests}') #!debug
                dict_data = breeze.get_historical_data_v2(**dict_request)
                if dict_data.get('Success') != None:
                    list_hist_data.extend(dict_data.get('Success'))
                    print(len(list_hist_data))
                else:
                    print('no data received. breaking.') #!debug
				int_request_count+=1
            print('dowloading finished.')  #!debug
            if len(list_hist_data) > 0:
                file_data = getcwd()+ ('\\' if name =='nt' else '//') + dict_request.get('stock_code')+'_'+ dict_request.get('interval') + '_' +\
                    dict_request.get('from_date').replace(':', '-')+'_to_' + dict_request.get('to_date').replace(':', '-') +'_fetched_at_'+ datetime.now().strftime('%Y-%m-%d %H:%M:%S').replace(':', '-') +'.csv'
                df = pd.DataFrame(list_hist_data)
                df.to_csv(file_data, index=False)
                print(f'data saved to {file_data}')
                del df
        else:
            print('not connected or request invalid.') #!debug
    if event =='-CLEAR_OUTPUT-':
        print('clear.')

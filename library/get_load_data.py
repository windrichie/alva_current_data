from firebase.firebase import FirebaseApplication, FirebaseAuthentication
# import ijson
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# import time
from datetime import datetime
from flask import Flask, render_template, request
import io
import base64
# import re

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def main():
    if request.method == 'POST':
        result = fetch_data()  #fetch from Firebasse
        data, columns = organize_data(result)
        load_choice = []
        box = request.form.get('all')
        if box == '1':
            load_choice = 'all'
            # print("checkbox", box)
        else:
            for item in columns:
                # if item != 'timestamp':
                curr_box = request.form.get(item)
                if curr_box == '1':
                    load_choice.append(item)

        # load_choice = request.form['load_choice']
        station_name = request.form['station_name']

        # load_choice = ['Grid','Tablet1']
        data_slice, tail_data = process_data(data, columns, load_choice=load_choice)
        image_url = plot_data(data_slice)  # get graph image url to display

        # cut the tail_data into last 5 measurements
        max_index = max(tail_data, key=int)
        indexes = {max_index, max_index-1, max_index-2, max_index-3, max_index-4}
        cut_data = dict([(key, tail_data[key]) for key in indexes if key in tail_data])
        # print(cut_data)
        return render_template('graph/data_layout.html', station_name=station_name, image_url=image_url, tail_data=cut_data)
        # time.sleep(5)
    elif request.method == 'GET':
        result = fetch_data()  # fetch data from Firebase
        data, columns = organize_data(result)
        load_keys = list(columns)
        i = -1
        # remove 'timestamp' from the dropdown list
        for item in load_keys:
            i += 1
            if item == 'timestamp':
                del load_keys[i]
        return render_template('inheritance/child_template_form.html', loads=load_keys)


def fetch_data():
    print("START")
    SECRET = '2woGLBK6IxfOtDCM553cZshFZJAZxSHVd3mAcGRY'
    DSN = 'https://jakartasmartpark.firebaseio.com/'
    EMAIL = 'tamanhijaujakarta'
    authentication = FirebaseAuthentication(SECRET,EMAIL, True, True)
    firebase = FirebaseApplication(DSN, authentication)
    result = firebase.get('/measurements', None)
    return result
# print(result)


def organize_data(result):
    columns = result.keys()
    # print(columns)
    print("DATA FETCHED")
    status = []
    timestamp = []
    data = []
    for f in columns:
        raw_data = []
        raw_time = result[f]['timestamp']
        real_timestamp = datetime.strptime(raw_time,'%Y-%m-%dT%H:%M:%S.%f') #convert str into datetime object
        #real_timestamp = datetime.strftime(real_timestamp,'%Y-%m-%d %H:%M:%S')
        if (real_timestamp.year > 2017):
            if 'Grid' in result[f]:
                raw_data.append(result[f]['Grid'])
            else:
                raw_data.append('NaN')
            if 'Inverter' in result[f]:
                raw_data.append(result[f]['Inverter'])
            else:
                raw_data.append('NaN')
            if 'Load' in result[f]:
                raw_data.append(result[f]['Load'])
            else:
                raw_data.append('NaN')
            if 'Rpi_Ard_sensors' in result[f]:
                raw_data.append(result[f]['Rpi_Ard_sensors'])
            else:
                raw_data.append('NaN')
            if 'Tablet1' in result[f]:
                raw_data.append(result[f]['Tablet1'])
            else:
                raw_data.append('NaN')
            if 'Tablet2' in result[f]:
                raw_data.append(result[f]['Tablet2'])
            else:
                raw_data.append('NaN')(())
            format_timestamp = datetime.strftime(real_timestamp, '%Y-%m-%d %H:%M:%S')
            real_timestamp = datetime.strptime(format_timestamp, '%Y-%m-%d %H:%M:%S')
            raw_data.append(real_timestamp)
            data.append(raw_data)  # create a new dictionary for the data

    columns = result[f].keys()
    return data, columns


def process_data(data, columns, load_choice):
    status = pd.DataFrame(data, columns=columns)
    tail_dict = status.to_dict('index')
    status = status.set_index('timestamp')
    if load_choice == 'all':
        pass
    else:
        status = status.loc[:, load_choice]
    # print(status['timestamp'].dtype)
    # status = status.loc[:,['Grid','Inverter','Load']]
    status = status.astype(float)

    return status, tail_dict


def plot_data(status):

    img = io.BytesIO()
    plt.gcf().clear()
    # status = status.cumsum()
    status.plot()
    plt.legend(loc='best')
    plt.tight_layout()
    # plt.show()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    # print(plot_url)
    return 'data:image/png;base64,{}'.format(plot_url)

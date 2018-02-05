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


@app.route('/')
def main():
    result = fetch_data()
    data = process_data(result)
    image_url, tail_data = plot_data(data)
    max_index = max(tail_data, key=int)
    indexes = {max_index, max_index-1, max_index-2, max_index-3, max_index-4}
    cut_data = dict([(key, tail_data[key]) for key in indexes if key in tail_data])
    print(cut_data)
    return render_template('graph/data_layout.html', station_name="Monas Smart Station", image_url=image_url, tail_data=cut_data)
    # time.sleep(5)


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


def process_data(result):
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
            format_timestamp = datetime.strftime(real_timestamp, '%Y-%m-%d %H:%M:%S')
            real_timestamp = datetime.strptime(format_timestamp, '%Y-%m-%d %H:%M:%S')
            raw_data.append(real_timestamp)
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
            data.append(raw_data)  # create a new dictionary for the data

    return data


def plot_data(data):
    status = pd.DataFrame(data, columns=["timestamp", "Grid", "Inverter", "Load", "Rpi_Ard_sensors", "Tablet1", "Tablet2"])
    tail_dict = status.to_dict('index')
    status = status.set_index('timestamp')
    # print(status['timestamp'].dtype)
    # status = status.loc[:,['Grid','Inverter','Load']]
    status = status.astype(float)
    img = io.BytesIO()
    # status = status.cumsum()
    status.plot()
    plt.legend(loc='best')
    plt.tight_layout()
    # plt.show()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    print(plot_url)
    return 'data:image/png;base64,{}'.format(plot_url), tail_dict

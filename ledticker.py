import pathlib 
import sys, os

import yaml
import json
import time
import base64
import logging
import math
import copy
import utils

from datetime import datetime

from ledtext import FixedText, ScrollingText
from ledmetric import NumberMetric, PercentMetric
from ledweather import CurrentWeather, ForecastWeather

from samplebase import SampleBase
from rgbmatrix import graphics
from expiringdict import ExpiringDict

from flashlexiot.sdk import FlashlexSDK
from pathlib import Path
import hashlib 
import requests

reqUrl = "http://localhost:5000/message"

db_file = '/home/pi/projects/ledticker-pi/db/led_messages.db'


def get_messages_new():
   # conn = utils.create_connection(db_file)
   # l_m = utils.select_all_messages(conn)
   # utils.delete_all_messages(conn)

   response = requests.request("GET", reqUrl)
   return  json.loads(response.text)



class LedDisplay(SampleBase):

    def __init__(self, *args, **kwargs):
        super(LedDisplay, self).__init__(*args, **kwargs)

        self.cache = ExpiringDict(max_len=20, max_age_seconds=500)

        self.parser.add_argument('--log', type=str, default="INFO", required=False,
                        help='which log level. DEBUG, INFO, WARNING, CRITICAL')
        self.parser.add_argument('--config', type=str, required=True, default='config.yml',
                        help='the name of the configuration section to use.')

    def get_messages_old(self, config):
        conn = utils.create_connection(db_file)  
        l_m = utils.select_all_messages(conn)
        # print(l_m)
        utils.delete_all_messages(conn)
        return l_m

    def run(self):
        """
        decoded message: {"payload": {"message": {"thingId": "b094aed5-52e5-4c40-954e-77a53dae65a0", "thingName": "foobar2"}}, "retain": 0, "mid": 0, "pos": 0, "topic": "ingress/foobar30"}
decoded message: {"payload": {"message": {"thingName": "foobar30", "text": "woopie"}}, "retain": 0, "mid": 0, "pos": 0, "topic": "ingress/foobar30"}
        """

        with open(self.args.config, 'r') as f:
            cfg = yaml.load(f, Loader=yaml.FullLoader)

        while True:
            now = datetime.now()
            date_time = now.strftime("%H:%M")
            decoded_model = {"elapsed": 15, "type": "text", "color": "#0ad800", "font": "sm-1", "behavior": "fixed", "body": date_time}
            text = FixedText(self,decoded_model)
            text.display()

            for message in get_messages_new():
                print('full message: {0}'.format(json.dumps(message)))
                decoded_model = message['message']["payload"]
                print('part to display: {0}'.format(json.dumps(decoded_model)))


                #this needs to be a factory
                if ScrollingText.matches(decoded_model):
                    text = ScrollingText(self,decoded_model)
                    text.display()
                elif FixedText.matches(decoded_model):
                    text = FixedText(self,decoded_model)
                    text.display()
                elif NumberMetric.matches(decoded_model):
                    metric = NumberMetric(self, decoded_model)
                    metric.display()
                elif PercentMetric.matches(decoded_model):
                    metric = PercentMetric(self, decoded_model)
                    metric.display()
                elif CurrentWeather.matches(decoded_model):
                    weather = CurrentWeather(self, decoded_model)
                    weather.display()
                elif ForecastWeather.matches(decoded_model):
                    weather = ForecastWeather(self, decoded_model)
                    weather.display()


            time.sleep(10)


def main(argv):
    print("starting ledticker.")
    ledDisplay = LedDisplay()
    if (not ledDisplay.process()):
        ledDisplay.print_help()

def main_b(argv):
    print("starting db init")
    conn = utils.create_connection(db_file)
    # create_table(conn)
    get_messages(conn)

if __name__ == "__main__":
    main(sys.argv[1:])

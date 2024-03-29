import pathlib
import sys, os

import yaml
import json
import time
import base64
import logging
import math
import copy





from datetime import datetime

from ledtext import FixedText, ScrollingText
from ledmetric import NumberMetric, PercentMetric
from ledweather import CurrentWeather, ForecastWeather

from samplebase import SampleBase
from rgbmatrix import graphics
from expiringdict import ExpiringDict

from flashlexiot.sdk import FlashlexSDK

import hashlib 

class LedDisplay(SampleBase):

    def __init__(self, *args, **kwargs):
        super(LedDisplay, self).__init__(*args, **kwargs)

        self.cache = ExpiringDict(max_len=20, max_age_seconds=500)

        self.parser.add_argument('--log', type=str, default="INFO", required=False,
                        help='which log level. DEBUG, INFO, WARNING, CRITICAL')
        self.parser.add_argument('--config', type=str, required=True, default='config.yml',
                        help='the name of the configuration section to use.')


    def get_messages(self, config):

        fn = "{0}/flashlex-iot-python/keys/config.yml".format(pathlib.Path(__file__).resolve().parents[1])
        sdk = FlashlexSDK(fn)
        cfg = sdk.loadConfig(fn)
        sdk.setConfig(cfg)
        messages = sdk.getSubscribedMessages()

        # process new messages
        for message in messages:
            # recompute hash without ids
            #hashdigest = message['_hash']	
            if 'id' in message: 
               del message['_id']
            if '_hash' in message: 
               del message['_hash']

            md5_hash = hashlib.md5(json.dumps(message).encode()) 
            message['_hash'] = md5_hash.hexdigest()
            print(message['_hash'])

            # if not in the cache then add it
            if(self.cache.get(message['_hash']) == None):
                print("adding to cache", message['_hash'])
                self.cache[message['_hash']] = message
            else:
                print("message already in cache")

            # yield message
            sdk.removeMessageFromStore(message)

        #get all hashes and yield live hashes

        dict2 = copy.deepcopy(self.cache)

        try:
           for key in dict2.keys():
              yield self.cache[key]
        except:
              pass


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

            for message in self.get_messages(cfg):
                print('full message: {0}'.format(json.dumps(message)))
                decoded_model = message['message']["payload"]["message"]
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
    print("starting ledticker with flashlex.")
    ledDisplay = LedDisplay()
    if (not ledDisplay.process()):
        ledDisplay.print_help()


if __name__ == "__main__":
    main(sys.argv[1:])

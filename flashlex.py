import pathlib
import sys, os

import yaml
import json
import time
import base64
import logging
import math
import datetime

from ledtext import FixedText, ScrollingText
from ledmetric import NumberMetric
from samplebase import SampleBase
from rgbmatrix import graphics

from flashlexpi.sdk import FlashlexSDK

class LedDisplay(SampleBase):

    def __init__(self, *args, **kwargs):
        super(LedDisplay, self).__init__(*args, **kwargs)

        self.parser.add_argument('--log', type=str, default="INFO", required=False,
                        help='which log level. DEBUG, INFO, WARNING, CRITICAL')
        self.parser.add_argument('--config', type=str, required=True, default='config.yaml',
                        help='the name of the configuration section to use.')


    def get_messages(self, config):

        while True:
            fn = "{0}/flashlex-pi-python/keys/config.yml".format(pathlib.Path(__file__).resolve().parents[1])
            sdk = FlashlexSDK(fn)
            messages = sdk.getSubscribedMessages()
            for message in messages:
                yield message
                sdk.removeMessageFromStore(message)
                time.sleep(10)

            time.sleep(10)


    def decode_message_model(self, b64encoded_json):
        decoded_data = base64.decodestring(b64encoded_json)
        return json.loads(decoded_data)

    def run(self):
        with open(self.args.config, 'r') as f:
            config = yaml.load(f)

        while True:
            for message in self.get_messages(config):
                decoded_model = message['message']

                print('decoded message: {0}'.format(json.dumps(decoded_model)))

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

            time.sleep(10)


def main(argv):
    print("starting ledticker with flashlex.")
    ledDisplay = LedDisplay()
    if (not ledDisplay.process()):
        ledDisplay.print_help()


if __name__ == "__main__":
    main(sys.argv[1:])
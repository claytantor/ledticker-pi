#!/usr/bin/env python
# coding: utf-8

import sys
import yaml
import json
import time
import os
import boto3
import botocore
import base64
import logging
import argparse
import math
import datetime

from ledtext import FixedText, ScrollingText
from ledmetric import NumberMetric
from samplebase import SampleBase
from rgbmatrix import graphics

# base_dir = os.path.join(os.path.dirname(__file__), 'my_file')

class LedDisplay(SampleBase):

    def __init__(self, *args, **kwargs):
        super(LedDisplay, self).__init__(*args, **kwargs)

        self.parser.add_argument('--log', type=str, default="INFO", required=False,
                        help='which log level. DEBUG, INFO, WARNING, CRITICAL')
        self.parser.add_argument('--config', type=str, required=True, default='config.yaml',
                        help='the name of the configuration section to use.')


    def get_messages_from_queue(self, session, queue_url):
        """Generates messages from an SQS queue.

        Note: this continues to generate messages until the queue is empty.
        Every message on the queue will be deleted.

        :param queue_url: URL of the SQS queue to drain.

        """
        sqs_client = session.client('sqs')

        while True:
            resp = sqs_client.receive_message(
                QueueUrl=queue_url,
                AttributeNames=['All'],
                MaxNumberOfMessages=10
            )

            try:
                for message in resp['Messages']:
                    yield message

            except KeyError:
                return

            entries = [
                {'Id': msg['MessageId'], 'ReceiptHandle': msg['ReceiptHandle']}
                for msg in resp['Messages']
            ]
            print "trying to delete {0} messages".format(len(entries))

            resp = sqs_client.delete_message_batch(
                QueueUrl=queue_url, Entries=entries
            )

            print "{0} messages deleted.".format(len(resp['Successful']))
            if len(resp['Successful']) != len(entries):
                raise RuntimeError(
                    # f"Failed to delete messages: entries={entries!r} resp={resp!r}"
                )

    def decode_message_model(self, b64encoded_json):
        decoded_data = base64.decodestring(b64encoded_json)
        return json.loads(decoded_data)

    def run(self):
        with open(self.args.config, 'r') as f:
            config = yaml.load(f)

        session = boto3.Session(
            aws_access_key_id=config['aws']['credentials']['aws_access_key_id'],
            aws_secret_access_key=config['aws']['credentials']['aws_secret_access_key'],
            region_name=config['aws']['region']
        )

        while True:
            for message in self.get_messages_from_queue(
                session,
                config['aws']['sqs']['message_url']):
                    decoded_model = self.decode_message_model(message['Body'])

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
    print "starting ticker app."

    ledDisplay = LedDisplay()
    if (not ledDisplay.process()):
        ledDisplay.print_help()

if __name__ == "__main__":
    main(sys.argv[1:])

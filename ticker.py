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
from samplebase import SampleBase
from rgbmatrix import graphics

# base_dir = os.path.join(os.path.dirname(__file__), 'my_file')

class RunText(SampleBase):

    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)

        self.parser.add_argument('--log', type=str, default="INFO", required=False,
                        help='which log level. DEBUG, INFO, WARNING, CRITICAL')
        self.parser.add_argument('--config', type=str, required=True, default='config.yaml',
                        help='the name of the configuration section to use.')
        self.parser.add_argument('--font', type=str, required=True, default='./fonts/7x13.bdf',
                        help='the path to the font to use')

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

            resp = sqs_client.delete_message_batch(
                QueueUrl=queue_url, Entries=entries
            )

            if len(resp['Successful']) != len(entries):
                raise RuntimeError(
                    # f"Failed to delete messages: entries={entries!r} resp={resp!r}"
                )

    def get_font_path(self, message):
        print json.dumps(message)
        font_path = os.path.join(os.path.dirname(__file__), 'fonts/7x13.bdf')
        if 'type' in message and message['type'] == 'text':
            font_path =  os.path.join(os.path.dirname(__file__), 'fonts/7x13.bdf')
        elif 'type' in message and message['type'] == 'text_sm':
            font_path =  os.path.join(os.path.dirname(__file__), 'fonts/5x8.bdf')
        #print font_path
        return font_path

    def display_text_scrolling(self, message):

        offscreen_canvas = self.matrix.CreateFrameCanvas()

        font = graphics.Font()

        font.LoadFont(self.get_font_path(message))
        textColor = graphics.Color(255, 255, 0)
        pos = offscreen_canvas.width

        start_time = time.time()
        elapsed_time = time.time() - start_time
        elapsed_time_boundry = 10.0
        if 'elapsed' in message:
            elapsed_time_boundry = message['elapsed']

        while elapsed_time < elapsed_time_boundry:
            #print time.time(), start_time

            offscreen_canvas.Clear()
            len = graphics.DrawText(offscreen_canvas, font, pos, 10, textColor, message['body'])
            pos -= 1
            if (pos + len < 0):
                pos = offscreen_canvas.width

            time.sleep(0.05)
            elapsed_time = time.time() - start_time
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
            #print elapsed_time, elapsed_time_boundry

        offscreen_canvas.Clear()

    def display_text_timed(self, message):

        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont(self.get_font_path(message))
        textColor = graphics.Color(255, 255, 0)

        len = graphics.DrawText(offscreen_canvas, font, 0, 10, textColor, message['body'])

        pos = math.ceil((offscreen_canvas.width-len)/2.0)
        #print offscreen_canvas.width,len,pos

        start_time = time.time()
        elapsed_time = time.time() - start_time
        elapsed_time_boundry = 10.0
        if 'elapsed' in message:
            elapsed_time_boundry = message['elapsed']

        while elapsed_time < elapsed_time_boundry:
            #print time.time(),start_time
            offscreen_canvas.Clear()
            len = graphics.DrawText(offscreen_canvas, font, pos, 10, textColor, message['body'])
            time.sleep(1)
            elapsed_time = time.time() - start_time
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
            #print elapsed_time, elapsed_time_boundry

        offscreen_canvas.Clear()

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
                    print(json.dumps(decoded_model))
                    #this needs to be a factory
                    if 'behavior' not in decoded_model and 'type' not in decoded_model:
                        self.display_text_scrolling(decoded_model)
                    elif decoded_model['type'].startswith('text') and 'behavior' in decoded_model and decoded_model['behavior'] == 'scrolling':
                        self.display_text_scrolling(decoded_model)
                    elif decoded_model['type'].startswith('text') and 'behavior' not in decoded_model:
                        self.display_text_scrolling(decoded_model)
                    elif 'behavior' in decoded_model and decoded_model['behavior'] == 'fixed' and 'elapsed' in decoded_model and decoded_model['type'].startswith('text'):
                        self.display_text_timed(decoded_model)

            time.sleep(10)

def main(argv):
    print "starting ticker app."

    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()

if __name__ == "__main__":
    main(sys.argv[1:])

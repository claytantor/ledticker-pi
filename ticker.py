#!/usr/bin/env python
# coding: utf-8

import sys
import yaml
import json
import time
import boto3
import botocore
import logging
import argparse
from Queue import Queue


from samplebase import SampleBase
from rgbmatrix import graphics


class RunText(SampleBase):

    def __init__(self, config, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        self.config = config
        # self.q = Queue(maxsize=0)

        self.session = boto3.Session(
            aws_access_key_id=config['aws']['credentials']['aws_access_key_id'],
            aws_secret_access_key=config['aws']['credentials']['aws_secret_access_key'],
            region_name=config['aws']['region']
        )

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

    def add_text(self, text):
        self.q.put(text)


    def display_message(self, message):

        #message = self.q.get()

        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("./fonts/7x13.bdf")
        textColor = graphics.Color(255, 255, 0)
        pos = offscreen_canvas.width

        # start_time = time.time()
        # elapsed_time = time.time() - start_time
        display_active = True

        while display_active:
            offscreen_canvas.Clear()
            len = graphics.DrawText(offscreen_canvas, font, pos, 10, textColor, message)
            pos -= 1
            if (pos + len < 0):
                pos = offscreen_canvas.width
                display_active = False

            time.sleep(0.05)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

        offscreen_canvas.Clear()


    def run(self):

        while True:

            for message in self.get_messages_from_queue(
                    self.session,
                    self.config['aws']['sqs']['message_url']):

                print(json.dumps(message))
                #self.q.put(message['Body'])
                self.display_message(message['Body'])

            time.sleep(10)



def main(argv):
    print "starting ticker app."


    with open('config.yaml', 'r') as f:
        config = yaml.load(f)

        run_text = RunText(config)
        if (not run_text.process()):
            run_text.print_help()

if __name__ == "__main__":
    main(sys.argv[1:])

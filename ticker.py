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
import docopt

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', type=str, default="INFO", required=False,
                        help='which log level. DEBUG, INFO, WARNING, CRITICAL')
    parser.add_argument('--config', type=str, required=True, default='config.yaml',
                        help='the name of the configuration section to use.')
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.load(f)
        session = boto3.Session(
            aws_access_key_id=config['aws']['credentials']['aws_access_key_id'],
            aws_secret_access_key=config['aws']['credentials']['aws_secret_access_key'],
            region_name=config['aws']['region']
        )

        while True:
            for message in get_messages_from_queue(
                    session,
                    config['aws']['sqs']['message_url']):

                print(json.dumps(message))

            time.sleep(10)

def get_messages_from_queue(session, queue_url):
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
                #f"Failed to delete messages: entries={entries!r} resp={resp!r}"
            )


if __name__ == "__main__":
    main(sys.argv[1:])

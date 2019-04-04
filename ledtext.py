#!/usr/bin/env python
# coding: utf-8

import sys, traceback
import json
import time
import os
import base64
import logging
import argparse
import math
import datetime
from rgbmatrix import graphics
from utils import hex2rgb

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

class LedText(object):
    def __init__(self, runner, message):
        self.runner = runner
        self.message = message

    def get_font_path(self, message):
        #print json.dumps(message)
        font_path = os.path.join(os.path.dirname(__file__), 'fonts/7x13.bdf')
        if 'font' in message and message['font'] == 'md-1':
            font_path =  os.path.join(os.path.dirname(__file__), 'fonts/7x13.bdf')
        elif 'font' in message and message['font'] == 'sm-1':
            font_path =  os.path.join(os.path.dirname(__file__), 'fonts/5x8.bdf')
        return font_path

    def get_text_color(self, message):
        textColor = graphics.Color(0, 255, 0)


        if 'color' in message:
            print(message['color'])
            try:
                color_tuple = hex2rgb(message['color'])
                textColor = graphics.Color(color_tuple[0],
                                           color_tuple[1],
                                           color_tuple[2])
            except:
                print("problem with color lookup")
                print("-"*60)
                traceback.print_exc(file=sys.stdout)
                print("-"*60)
                pass

        return textColor


class FixedText(LedText):

    def __init__(self, runner, message):
        super(FixedText, self).__init__(runner, message)
        self.name = "Fixed Text"

    @staticmethod
    def matches(message):
        if 'body' in message and 'behavior' in message and message['behavior'] == 'fixed' and message['type'].startswith('text'):
            return True
        else:
            return False

    def display(self):

        offscreen_canvas = self.runner.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont(self.get_font_path(self.message))

        #textColor = graphics.Color(255, 255, 0)
        textColor = self.get_text_color(self.message)

        len = graphics.DrawText(offscreen_canvas, font, 0, 10, textColor, '{0}'.format(self.message['body']))

        pos = math.ceil((offscreen_canvas.width-len)/2.0)
        height = math.ceil(offscreen_canvas.width/2.0)+math.ceil((font.height-2)/2.0)
        # print("height: {0} font.height: {1}".format(height, font.height))

        start_time = time.time()
        elapsed_time = time.time() - start_time
        elapsed_time_boundry = 10.0
        if 'elapsed' in self.message:
            elapsed_time_boundry = self.message['elapsed']

        while elapsed_time < elapsed_time_boundry:
            #print time.time(),start_time
            offscreen_canvas.Clear()
            len = graphics.DrawText(offscreen_canvas, font, pos, height, textColor, '{0}'.format(self.message['body']))
            time.sleep(1)
            elapsed_time = time.time() - start_time
            offscreen_canvas = self.runner.matrix.SwapOnVSync(offscreen_canvas)

        offscreen_canvas.Clear()
        offscreen_canvas = self.runner.matrix.SwapOnVSync(offscreen_canvas)

class ScrollingText(LedText):

    def __init__(self, runner, message):
        super(ScrollingText, self).__init__(runner, message)
        self.name = "Scrolling Text"


    @staticmethod
    def matches(message):
        if 'body' in message and 'behavior' not in message and 'type' not in message:
            return True
        elif 'body' in message and message['type'].startswith('text') and 'behavior' in message and message['behavior'] == 'scrolling':
            return True
        elif 'body' in message and message['type'].startswith('text') and 'behavior' not in message:
            return True
        else:
            return False

    def display(self):
        offscreen_canvas = self.runner.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont(self.get_font_path(self.message))

        #textColor = graphics.Color(255, 255, 0)
        textColor = self.get_text_color(self.message)

        pos = offscreen_canvas.width
        #height = math.ceil(offscreen_canvas.width/2.0) +math.ceil(font.height/2.0)-1
        height = math.ceil(offscreen_canvas.width/2.0)+math.ceil((font.height-2)/2.0)
        scrolling = True

        while scrolling:
            offscreen_canvas.Clear()
            len = graphics.DrawText(offscreen_canvas, font, pos, height, textColor, '{0}'.format(self.message['body']))
            pos -= 1
            if (pos + len < 0):
                pos = offscreen_canvas.width
                scrolling = False

            time.sleep(0.05)
            offscreen_canvas = self.runner.matrix.SwapOnVSync(offscreen_canvas)

        offscreen_canvas.Clear()
        offscreen_canvas = self.runner.matrix.SwapOnVSync(offscreen_canvas)

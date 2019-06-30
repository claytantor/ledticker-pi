import sys
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

class LedMetric(object):
    def __init__(self, runner, message):
        self.runner = runner
        self.message = message


class NumberMetric(LedMetric):
    def __init__(self, runner, message):
        super(NumberMetric, self).__init__(runner, message)
        self.name = "Number Metric"

    @staticmethod
    def matches(message):
        if 'body' in message and 'behavior' in message and message['behavior'] == 'number' and message['type'] == 'metric':
            return True
        else:
            return False

    def get_text_color(self, message):
        textColor = graphics.Color(0, 0, 255)

        if 'color' in message:
            try:
                color_tuple = hex2rgb(message['color'])
                textColor = graphics.Color(color_tuple[0],
                                           color_tuple[1],
                                           color_tuple[2])
            except:
                pass

        return textColor
    def display(self):

        parts = self.message['body'].split(" ")

        offscreen_canvas = self.runner.matrix.CreateFrameCanvas()
        textColor = self.get_text_color(self.message)

        # font for the metric
        fontMetric = graphics.Font()
        font_path_metric =  os.path.join(os.path.dirname(__file__), 'fonts/9x18.bdf')
        fontMetric.LoadFont(font_path_metric)

        lenMetric = graphics.DrawText(offscreen_canvas, fontMetric, 0, 1, textColor, '{0}'.format(parts[1]))

        posMetric = math.ceil((offscreen_canvas.width-lenMetric)/2.0)

        # font for the label
        fontLabel = graphics.Font()
        font_path_label =  os.path.join(os.path.dirname(__file__), 'fonts/5x8.bdf')
        fontLabel.LoadFont(font_path_label)
        posLabel = offscreen_canvas.width
        scrolling = True

        while scrolling:
            #print time.time(),start_time
            offscreen_canvas.Clear()
            lenMetric = graphics.DrawText(offscreen_canvas, fontMetric, posMetric, fontMetric.height+1, textColor, '{0}'.format(parts[1]))

            vPosLabel = fontMetric.height+1+fontLabel.height

            lenLabel = graphics.DrawText(offscreen_canvas, fontLabel, posLabel, vPosLabel, textColor, '{0}'.format(parts[0]))

            posLabel -= 1
            if (posLabel + lenLabel < 0):
                posLabel = offscreen_canvas.width
                scrolling = False

            time.sleep(0.05)
            offscreen_canvas = self.runner.matrix.SwapOnVSync(offscreen_canvas)

        offscreen_canvas.Clear()
        offscreen_canvas = self.runner.matrix.SwapOnVSync(offscreen_canvas)
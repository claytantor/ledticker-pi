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

class PercentMetric(LedMetric):
    def __init__(self, runner, message):
        super(PercentMetric, self).__init__(runner, message)
        self.name = "Percent Metric"
    
    @staticmethod
    def matches(message):
        if 'body' in message and 'behavior' in message and message['behavior'] == 'number' and message['type'] == 'pmetric':
            return True
        else:
            return False

    def display(self):

        parts = self.message['body'].split("|")
        
        percentModel = {
            'metricName':parts[0],
            'value':'{:.0f}'.format(float(parts[2])*100.0),
            'name':parts[1]
        }
        print(percentModel)


        offscreen_canvas = self.runner.matrix.CreateFrameCanvas()
        textColor = self.get_text_color(self.message)

        # fonts to load 
        font_path_metric =  os.path.join(os.path.dirname(__file__), 'fonts/9x18.bdf')
        font_path_sm =  os.path.join(os.path.dirname(__file__), 'fonts/5x8.bdf')
        font_path_sm2 =  os.path.join(os.path.dirname(__file__), 'fonts/4x6.bdf')

        #behavior
        fontBehavior = graphics.Font()
        fontBehavior.LoadFont(font_path_sm2)
        lenBehavior = graphics.DrawText(offscreen_canvas, fontBehavior, 0, 1, textColor, '{0}'.format(percentModel['metricName']))
        posBehavior = offscreen_canvas.width  

        # font for the metric
        fontPercent = graphics.Font()
        fontPercent.LoadFont(font_path_metric)
        v = percentModel['value']
        print(v) 
        lenPercent = graphics.DrawText(offscreen_canvas, fontPercent, 0, 1, textColor, v)
        posMetric = math.ceil((offscreen_canvas.width-lenPercent)/2.0)-2
        
	# the percentage
        fontUnit = graphics.Font()
        fontUnit.LoadFont(font_path_sm)
        wPosUnit = posMetric+lenPercent+1
        tempHeight = math.ceil(offscreen_canvas.width/2.0)+math.ceil((fontPercent.height-2)/2.0)-2
        graphics.DrawText(offscreen_canvas, fontUnit, wPosUnit, tempHeight, textColor, '%')

        # font for the label
        fontLabel = graphics.Font()
        fontLabel.LoadFont(font_path_sm)

        posLabel = offscreen_canvas.width
        scrolling = True

        counter=0
        while scrolling:
            offscreen_canvas.Clear()

            lenPercent = graphics.DrawText(offscreen_canvas, fontPercent, posMetric, tempHeight, textColor, v)
            graphics.DrawText(offscreen_canvas, fontUnit, wPosUnit, tempHeight, textColor, '%')
            hPosBehavior = fontBehavior.height+1

            lenBehavior = graphics.DrawText(offscreen_canvas, fontBehavior, posBehavior, hPosBehavior, textColor, '{0}'.format(percentModel['metricName']))

            vPosLabel = offscreen_canvas.height - 1

            lenLabel = graphics.DrawText(offscreen_canvas, fontLabel, posLabel, vPosLabel, textColor, '{0}'.format(percentModel['name']))

            posLabel -= 1
            if (posLabel + lenLabel < 0):
                posLabel = offscreen_canvas.width


            #lenBehavior = graphics.DrawText(offscreen_canvas, fontBehavior, posBehavior, 1, textColor, '{0}'.format(percentModel['metricName']))
            posBehavior -= 1
            if (posBehavior + lenBehavior < 0):
                posBehavior = offscreen_canvas.width
                counter += 1
                if counter == 2:
                    scrolling = False

            time.sleep(0.05)
            offscreen_canvas = self.runner.matrix.SwapOnVSync(offscreen_canvas)

        offscreen_canvas.Clear()
        offscreen_canvas = self.runner.matrix.SwapOnVSync(offscreen_canvas)

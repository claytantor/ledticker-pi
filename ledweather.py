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

class LedWeather(object):
    def __init__(self, runner, message):
        self.runner = runner
        self.message = message


class CurrentWeather(LedWeather):
    def __init__(self, runner, message):
        super(CurrentWeather, self).__init__(runner, message)
        self.name = "Current Weather"

    @staticmethod
    def matches(message):
        if 'body' in message and 'behavior' in message and message['behavior'] == 'current' and message['type'] == 'weather':
            return True
        else:
            return False

    def get_text_color(self, message):
        textColor = graphics.Color(100, 20, 255)

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

        parts = self.message['body'].split("|")

        offscreen_canvas = self.runner.matrix.CreateFrameCanvas()
        textColor = self.get_text_color(self.message)

        # fonts to load
        font_path_metric =  os.path.join(os.path.dirname(__file__), 'fonts/9x18.bdf')
        font_path_sm =  os.path.join(os.path.dirname(__file__), 'fonts/5x8.bdf')
        font_path_sm2 =  os.path.join(os.path.dirname(__file__), 'fonts/4x6.bdf')

        #behavior
        fontBehavior = graphics.Font()
        fontBehavior.LoadFont(font_path_sm2)
        lenBehavior = graphics.DrawText(offscreen_canvas, fontBehavior, 0, 1, textColor, '{0}'.format(self.message['behavior']))
        posBehavior = math.ceil((offscreen_canvas.width-lenBehavior)/2.0)

        # font for the metric
        fontTemp = graphics.Font()
        fontTemp.LoadFont(font_path_metric)
        lenTemp = graphics.DrawText(offscreen_canvas, fontTemp, 0, 1, textColor, '{0}'.format(parts[1]))
        posMetric = math.ceil((offscreen_canvas.width-lenTemp)/2.0)-2

        fontUnit = graphics.Font()
        fontUnit.LoadFont(font_path_sm)

        # font for the label
        fontLabel = graphics.Font()
        fontLabel.LoadFont(font_path_sm)

        posLabel = offscreen_canvas.width
        scrolling = True

        counter=0
        while scrolling:
            #print time.time(),start_time
            offscreen_canvas.Clear()

            tempHeight = math.ceil(offscreen_canvas.width/2.0)+math.ceil((fontTemp.height-2)/2.0)-2

            lenTemp = graphics.DrawText(offscreen_canvas, fontTemp, posMetric, tempHeight, textColor, '{0}'.format(parts[1]))

            # wPosBehavior = posBehavior
            hPosBehavior = fontBehavior.height+1

            lenBehavior = graphics.DrawText(offscreen_canvas, fontBehavior, posBehavior, hPosBehavior, textColor, '{0}'.format(self.message['behavior']))

            wPosUnit = posMetric+lenTemp+1

            graphics.DrawText(offscreen_canvas, fontUnit, wPosUnit, tempHeight, textColor, '{0}'.format(parts[2]))

            #vPosLabel = fontTemp.height+1+fontLabel.height
            vPosLabel = offscreen_canvas.height - 1

            lenLabel = graphics.DrawText(offscreen_canvas, fontLabel, posLabel, vPosLabel, textColor, '{0}'.format(parts[0]))

            posLabel -= 1
            if (posLabel + lenLabel < 0):
                posLabel = offscreen_canvas.width
                counter += 1
                if counter == 2:
                    scrolling = False

            time.sleep(0.05)
            offscreen_canvas = self.runner.matrix.SwapOnVSync(offscreen_canvas)

        offscreen_canvas.Clear()
        offscreen_canvas = self.runner.matrix.SwapOnVSync(offscreen_canvas)



class ForecastWeather(LedWeather):
    def __init__(self, runner, message):
        super(ForecastWeather, self).__init__(runner, message)
        self.name = "Forecast Weather"

    @staticmethod
    def matches(message):
        print (message)
        if 'body' in message and 'behavior' in message and message['behavior'] == 'forecast' and message['type'] == 'weather':
            return True
        else:
            return False

    def get_text_color(self, message):
        textColor = graphics.Color(100, 20, 255)

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

        parts = self.message['body'].split("|")

        offscreen_canvas = self.runner.matrix.CreateFrameCanvas()
        textColor = self.get_text_color(self.message)

        # fonts to load
        font_path_metric =  os.path.join(os.path.dirname(__file__), 'fonts/8x13.bdf')
        font_path_sm =  os.path.join(os.path.dirname(__file__), 'fonts/5x8.bdf')
        font_path_sm2 =  os.path.join(os.path.dirname(__file__), 'fonts/4x6.bdf')

        # the units font
        fontUnit = graphics.Font()
        fontUnit.LoadFont(font_path_sm)
        lenUnit = graphics.DrawText(offscreen_canvas, fontUnit, 0, 1, textColor, '{0}'.format(parts[3]))

        # high
        fontTemp = graphics.Font()
        fontTemp.LoadFont(font_path_metric)

        posXHigh = 0
        posYHigh = fontTemp.height - 2

        lenTempHigh = graphics.DrawText(offscreen_canvas, fontTemp, 0, 1, textColor, '{0}'.format(parts[1]))

        posXUnitHigh = lenTempHigh + 1
        posYUnitHigh = fontTemp.height - 1

        # low
        lenTempLow = graphics.DrawText(offscreen_canvas, fontTemp, 0, 1, textColor, '{0}'.format(parts[2]))

        posXLow = offscreen_canvas.width - lenTempLow - lenUnit
        posYLow = offscreen_canvas.height - 1

        posXUnitLow = posXLow + lenTempLow
        posYUnitLow = offscreen_canvas.height - 1

        #
        # font for the label
        fontLabel = graphics.Font()
        fontLabel.LoadFont(font_path_sm)
        posYLabel = math.ceil(offscreen_canvas.width/2.0) + math.ceil((fontLabel.height-2)/2.0) + 1

        scrolling = True
        posLabel = offscreen_canvas.width
        counter = 0
        while scrolling:

            offscreen_canvas.Clear()

            # high
            lenTemp = graphics.DrawText(offscreen_canvas, fontTemp, posXHigh, posYHigh, textColor, '{0}'.format(parts[1]))
            graphics.DrawText(offscreen_canvas, fontUnit, posXUnitHigh, posYUnitHigh, textColor, '{0}'.format(parts[3]))

            # low
            lenTemp = graphics.DrawText(offscreen_canvas, fontTemp, posXLow, posYLow, textColor, '{0}'.format(parts[2]))
            graphics.DrawText(offscreen_canvas, fontUnit, posXUnitLow, posYUnitLow, textColor, '{0}'.format(parts[3]))

            condition_forecast = 'next {0}: {1}'.format(parts[4],parts[0])

            lenLabel = graphics.DrawText(offscreen_canvas, fontLabel, posLabel, posYLabel, textColor, condition_forecast)

            posLabel -= 1
            if (posLabel + lenLabel < 0):
                posLabel = offscreen_canvas.width
                counter += 1
                if counter == 2:
                    scrolling = False

            time.sleep(0.05)
            offscreen_canvas = self.runner.matrix.SwapOnVSync(offscreen_canvas)
        #
        offscreen_canvas.Clear()
        offscreen_canvas = self.runner.matrix.SwapOnVSync(offscreen_canvas)

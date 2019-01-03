#!/usr/bin/env python
import time
import sys
import argparse
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image


def main(argv):
    print "starting icon app."

    parser = argparse.ArgumentParser()

    parser.add_argument("-m", "--mapping", action="store", help="Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm" , choices=['regular', 'adafruit-hat', 'adafruit-hat-pwm'], type=str, default="adafruit-hat")

    parser.add_argument("-i", "--icon", action="store", help="Icon name: provide a full path to file", type=str, default="./images/icon1.jpg")

    args = parser.parse_args()

    image = Image.open(args.icon)

    # Configuration for the matrix
    options = RGBMatrixOptions()
    options.rows = 32
    options.chain_length = 1
    options.parallel = 1
    options.hardware_mapping = args.mapping  # If you have an Adafruit HAT: 'adafruit-hat'

    matrix = RGBMatrix(options = options)

    # Make image fit our screen.
    image.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)

    matrix.SetImage(image.convert('RGB'))

    try:
        print("Press CTRL-C to stop.")
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])

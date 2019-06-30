#!/usr/bin/env python
# coding: utf-8
import sys, os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

def hex2rgb(hexcode):
    h = hexcode.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


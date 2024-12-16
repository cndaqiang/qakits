#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
##################################
# Author : cndaqiang             #
# Update : 2021-01-24            #
# Build  : 2021-01-24            #
# What   : 简单计算 #
##################################
"""

import sys
import os
import numpy as np
from math import *

def main():
    #-----Input File
    if len(sys.argv) == 1:
        print( "Usage: "+str(sys.argv[0])+" 1+2")
        exit

    print("{:10s}".format("expr")+" \t = ","value")
    expr=""
    for i in sys.argv[1:]:
        expr=expr+str(i)
    print("{:10s}".format(expr)+" \t = ",eval(expr))


if __name__ == "__main__":
    main()

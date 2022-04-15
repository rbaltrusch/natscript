# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:54:26 2020

@author: Korean_Crimson
"""

import interpret

if __name__ == '__main__':
    tokens = interpret.construct_tokens(filename='test.nat')
    interpret.interpret(tokens)

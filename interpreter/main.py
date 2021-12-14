# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:54:26 2020

@author: Korean_Crimson
"""

from interpret import interpret

def main():
    with open('test.nat') as file:
        file_contents = file.read()
        interpret(file_contents)

if __name__ == '__main__':
    main()

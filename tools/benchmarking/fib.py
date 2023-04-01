# -*- coding: utf-8 -*-
"""Benchmarking code"""
# pylint: skip-file


def fib(lim):
    lim = 1000000
    current = 1
    old = 1
    nums = [old, current]
    while current <= lim:
        new = current + old
        nums.append(new)
        old = current
        current = new
    return nums


def main():
    for _ in range(1000):
        fib(1000000)


main()

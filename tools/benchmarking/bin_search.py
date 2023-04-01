# -*- coding: utf-8 -*-
"""Benchmarking code"""
# pylint: skip-file


def binary_search(l, tar):
    i = len(l) // 2
    val = l[i]
    if tar == val:
        return i
    if tar < val:
        return binary_search(l[:i], tar)
    return binary_search(l[i:], tar) + i


def main():
    for _ in range(100):
        el = [1, 3, 5, 8, 13, 26, 53, 76, 88, 135, 268, 377, 416, 529, 876, 1000]
        for tar in el:
            binary_search(el, tar)


main()

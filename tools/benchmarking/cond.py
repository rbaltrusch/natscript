# -*- coding: utf-8 -*-
"""Benchmarking code"""
# pylint: skip-file

for _ in range(1000):
    a = [1, 1, 1]
    b = [1, 1, 0]
    c = [1, 0, 0]
    d = [0, 0, 0]
    n = [a, b, c, d]

    def f1(x):
        return all(x)

    def f2(x):
        return len([y for y in x if y]) > 1

    def f3(x):
        return any(x)

    def f4(x):
        return not any(x)

    def test(n, f):
        print([f(m) for m in n])

    test(n, f1)
    test(n, f2)
    test(n, f3)
    test(n, f4)

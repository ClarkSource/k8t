# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Clark Germany GmbH

from kinja.values import merge, deep_merge


def test_merge_memory_safety():
    dict_a = dict(foo=1, bar=2)
    dict_b = dict(bar=3, baz=4)

    merge(dict_a, dict_b)

    assert dict_a == dict(foo=1, bar=2)


def test_ltr_merge():
    dict_a = dict(foo=dict(a=1, b=2), bar=dict(a=3))
    dict_b = dict(foo=dict(b=3), baz=4)

    assert (
        merge(dict_a, dict_b) == dict(foo=dict(a=1, b=3), bar=dict(a=3), baz=4))

    dict_b = dict(foo=1)

    assert (
        merge(dict_a, dict_b) == dict(foo=1, bar=dict(a=3)))

def test_deep_merge():
    dict_a = dict(foo=dict(a=1, b=2), bar=dict(a=3))
    dict_b = dict(foo=dict(b=3), baz=4)
    dict_c = dict(foo=dict(b=9), bar=dict(c=9))

    assert (
        deep_merge(dict_a, dict_b, dict_c) == dict(foo=dict(a=1, b=9), baz=4, bar=dict(a=3, c=9)))

    assert (
        deep_merge(dict_a, dict_c, dict_b) == dict(foo=dict(a=1, b=3), baz=4, bar=dict(a=3, c=9)))

    assert (
        deep_merge(dict_c, dict_b, dict_a) == dict(foo=dict(a=1, b=2), baz=4, bar=dict(a=3, c=9)))

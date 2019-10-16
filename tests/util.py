# -*- coding: utf-8 -*-
#
# Copyright © 2018 Clark Germany GmbH
# Author: Aljosha Friemann <aljosha.friemann@clark.de>

import random

from k8t.util import (b64decode, b64encode, deep_merge, hashf, merge,
                      random_password)


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


def test_b64encode():
    string = "foobar"

    encoded = b64encode(string)

    assert encoded != string
    assert b64decode(encoded) == string


def test_random_password():
    length = int(random.uniform(1, 200))

    assert len(random_password(length)) == length
    assert random_password(length) != random_password(length)


def test_hashf():
    string = "foobar"

    assert hashf(string) != string
    assert hashf(string) == hashf(string)
    assert hashf(string) != hashf("foobaz")

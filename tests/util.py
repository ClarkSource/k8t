# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import random

from k8t.util import deep_merge, merge


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

# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

#
# Copyright © 2020 Clark Germany GmbH
# Author: Aljosha Friemann <aljosha.friemann@clark.de>

import random

from k8t.filters import b64decode, b64encode, hashf, random_password


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

# vim: fenc=utf-8:ts=4:sw=4:expandtab

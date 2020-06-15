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
import pytest
from mock import patch

from k8t import config, secret_providers
from k8t.filters import b64decode, b64encode, hashf, random_password, to_bool, get_secret


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


def test_get_secret():
    config.CONFIG = {"secrets": {"provider": "random"}}
    with patch.object(secret_providers, "random") as mock:
        get_secret("any")
        mock.assert_called_with("any", None)
        get_secret("any", 99)
        mock.assert_called_with("any", 99)

    config.CONFIG = {"secrets": {"provider": "ssm"}}
    with patch.object(secret_providers, "ssm") as mock:
        get_secret("any")
        mock.assert_called_with("any", None)
        get_secret("any", 99)
        mock.assert_called_with("any", 99)

    config.CONFIG = {"secrets": {"provider": "nothing"}}
    with pytest.raises(NotImplementedError, match=r"secret provider nothing does not exist."):
        get_secret("any")

    config.CONFIG = {}
    with pytest.raises(RuntimeError, match=r"Secrets provider not configured."):
        get_secret("any")


def test_to_bool():
    assert to_bool(True)
    assert to_bool("Yes")
    assert to_bool("yes")
    assert to_bool("True")
    assert to_bool("true")
    assert to_bool("On")
    assert to_bool("on")
    assert to_bool("1")
    assert to_bool(1)

    assert not to_bool(None)
    assert not to_bool(False)
    assert not to_bool("False")
    assert not to_bool("false")
    assert not to_bool("anything")
    assert not to_bool("0")
    assert not to_bool(0)

# vim: fenc=utf-8:ts=4:sw=4:expandtab

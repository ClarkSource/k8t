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
import bitmath

import pytest  # pylint: disable=E0401
from mock import patch  # pylint: disable=E0401

from k8t import config, secret_providers
from k8t.filters import (
    b64decode,
    b64encode,
    get_secret,
    hashf,
    random_password,
    sanitize_cpu,
    sanitize_label,
    sanitize_memory,
    to_bool,
)


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
    assert to_bool(None) is None

    assert to_bool(True) is True
    assert to_bool("Yes") is True
    assert to_bool("yes") is True
    assert to_bool("True") is True
    assert to_bool("true") is True
    assert to_bool("On") is True
    assert to_bool("on") is True
    assert to_bool("1") is True
    assert to_bool(1) is True

    assert to_bool(False) is False
    assert to_bool("False") is False
    assert to_bool("false") is False
    assert to_bool("0") is False
    assert to_bool(0) is False

    # TODO this is a bad one, probably need to raise an error instead
    assert to_bool("anything") is False


def test_sanitize_label():
    # sanity check
    assert sanitize_label("foobar") == "foobar"

    # check replacement for first and last characters
    assert sanitize_label(",foobar-") == "XfoobarX"

    # check valid characters
    assert sanitize_label(",foobar-baz.com") == "Xfoobar-baz.com"

    # check invalid character replacements
    assert sanitize_label(",foobar-baz$.com") == "Xfoobar-bazX.com"

    # check length
    assert len(sanitize_label("x" * 65)) == 63


def test_sanitize_cpu():
    assert sanitize_cpu("200m") == "200m"
    assert sanitize_cpu("0.5") == "500m"
    assert sanitize_cpu(0.5) == "500m"
    assert sanitize_cpu("1") == "1000m"
    assert sanitize_cpu(1) == "1000m"
    assert sanitize_cpu("92") == "92000m"
    assert sanitize_cpu(92) == "92000m"
    assert sanitize_cpu("1.8") == "1800m"
    assert sanitize_cpu(1.8) == "1800m"
    assert sanitize_cpu("3000m") == "3000m"

    assert sanitize_cpu("0.1") == "100m"
    assert sanitize_cpu(0.1) == "100m"
    assert sanitize_cpu("0.01") == "10m"
    assert sanitize_cpu(0.01) == "10m"
    assert sanitize_cpu("0.001") == "1m"
    assert sanitize_cpu(0.001) == "1m"

    with pytest.raises(ValueError):
        assert sanitize_cpu("0.0001") == "0.1m"
        assert sanitize_cpu(0.0001) == "0.1m"


def test_sanitize_memory():
    def compare(size: str, value: int, precision: float = 0.008) -> bool:
        # precision of 0.008 results in (value +- 1.0e+00)
        return int(bitmath.parse_string(f"{size}B")) == pytest.approx(value, precision)

    assert sanitize_memory("200M") == "200M"

    with pytest.raises(ValueError):
        assert sanitize_memory("100000000m") == "0.1M"

    assert sanitize_memory("1289748") == "1M"
    assert sanitize_memory(1289748) == "1M"
    with pytest.raises(ValueError):
        assert sanitize_memory("128974") == "0M"

    # precision can vary between systems, values should be approximately 129MB
    assert compare(sanitize_memory("129e6"), 129)
    assert compare(sanitize_memory("129M"), 129)
    assert compare(sanitize_memory("128974848"), 129)
    assert compare(sanitize_memory(128974848), 129)
    assert compare(sanitize_memory("128974848000m"), 129)
    assert compare(sanitize_memory("123Mi"), 129)

    with pytest.raises(ValueError):
        # TODO: this is a known limitation
        assert compare(sanitize_memory(129e6), 129)

    assert sanitize_memory("300000000000m") == "300M"
    assert sanitize_memory("20000000000m") == "20M"
    assert sanitize_memory("20005000000m") == "20M"
    assert sanitize_memory("1000000000m") == "1M"

    assert sanitize_memory("2M") == "2M"
    assert sanitize_memory("2G") == "2000M"
    assert sanitize_memory("2T") == "2000000M"
    assert sanitize_memory("2P") == "2000000000M"

    assert sanitize_memory("2Mi") == "2M"
    assert sanitize_memory("2Gi") == "2147M"
    assert sanitize_memory("2Ti") == "2199023M"
    assert sanitize_memory("2Pi") == "2251799813M"

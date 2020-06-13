# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import string

from . import LOGGER

try:
    from secrets import SystemRandom
except ImportError:
    from random import SystemRandom

RANDOM_STORE = {}


def get_secret(key: str, length: int = None) -> str:
    LOGGER.debug("Requesting secret from %s", key)

    if key not in RANDOM_STORE:
        RANDOM_STORE[key] = "".join(
            SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(length or SystemRandom().randint(12, 32))
        )

    if length is not None:
        if len(RANDOM_STORE[key]) != length:
            raise AssertionError("Secret '{}' did not have expected length of {}".format(key, length))

    return RANDOM_STORE[key]
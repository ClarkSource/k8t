# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import boto3

from . import config
from . import LOGGER

DEFAULT_SSM_PREFIX = ""
DEFAULT_SSM_REGION = "eu-central-1"


def get_secret(key: str, length: int = None) -> str:
    prefix = str(config.CONFIG.get("secrets", {}).get("prefix", DEFAULT_SSM_PREFIX))
    key = prefix + key
    LOGGER.debug("Requesting secret from %s", key)

    region = str(config.CONFIG.get("secrets", {}).get("region", DEFAULT_SSM_REGION))
    client = boto3.client("ssm", region_name=region)

    try:
        result = client.get_parameter(Name=key, WithDecryption=True)["Parameter"]["Value"]

        if length is not None:
            if len(result) != length:
                raise AssertionError("Secret '{}' did not have expected length of {}".format(key, length))

        return result
    except client.exceptions.ParameterNotFound:
        raise RuntimeError("Could not find secret: {}".format(key))

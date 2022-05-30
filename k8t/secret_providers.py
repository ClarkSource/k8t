# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import logging
import hashlib
import string

import boto3  # pylint: disable=E0401
import botocore  # pylint: disable=E0401
from k8t import config
from typing import Optional

try:
    from secrets import SystemRandom
except ImportError:
    from random import SystemRandom


LOGGER = logging.getLogger(__name__)
RANDOM_STORE = {}
DEFAULT_SSM_PREFIX = ""
DEFAULT_SSM_REGION = "eu-central-1"


def ssm(key: str, length: Optional[int] = None) -> str:
    secrets_config = config.CONFIG.get("secrets", {})

    prefix = str(secrets_config.get("prefix", DEFAULT_SSM_PREFIX))
    region = str(secrets_config.get("region", DEFAULT_SSM_REGION))
    role_arn = str(secrets_config.get("role_arn", ""))

    client_config = dict(region_name=region)

    if role_arn != '':
        role_creds = _assume_role(role_arn, region)

        client_config.update(dict(
            aws_access_key_id=role_creds['AccessKeyId'],
            aws_secret_access_key=role_creds['SecretAccessKey'],
            aws_session_token=role_creds['SessionToken'],
        ))

    client = boto3.client("ssm", **client_config)

    key = prefix + key

    LOGGER.debug("Requesting secret from %s", key)

    try:
        result = client.get_parameter(Name=key, WithDecryption=True)["Parameter"][
            "Value"
        ]

        if length is not None:
            if len(result) != length:
                raise AssertionError(f"Secret '{key}' did not have expected length of {length}")

        return result
    except (
        client.exceptions.ParameterNotFound,
        botocore.exceptions.ClientError,
    ) as exc:
        raise RuntimeError(f"Failed to retrieve secret {key}: {exc}") from exc


def _assume_role(role_arn: str, region: str) -> dict:
    sts_client = boto3.client('sts', region_name=region)

    LOGGER.debug("assuming role %s", role_arn)

    try:
        assumed_role = sts_client.assume_role(RoleArn=role_arn, RoleSessionName='k8t')

        role_creds = assumed_role.get('Credentials')

        if role_creds is None:
            raise RuntimeError(f"Failed to assume role {role_arn}")

        return role_creds
    except (
        botocore.exceptions.ClientError,
    ) as exc:
        raise RuntimeError(f"Failed to assume role {role_arn}: {exc}") from exc


def random(key: str, length: Optional[int] = None) -> str:
    LOGGER.debug("Requesting secret from %s", key)

    if key not in RANDOM_STORE:
        RANDOM_STORE[key] = "".join(
            SystemRandom().choice(string.ascii_lowercase + string.digits)

            for _ in range(length or SystemRandom().randint(12, 32))
        )

    if length is not None:
        if len(RANDOM_STORE[key]) != length:
            raise AssertionError(f"Secret '{key}' did not have expected length of {length}")

    return RANDOM_STORE[key]


def hash(key: str, length: Optional[int] = None) -> str:
    LOGGER.debug("Requesting secret from %s", key)

    if key not in RANDOM_STORE:
        hashed_key = hashlib.sha1(key.encode()).hexdigest()
        RANDOM_STORE[key] = hashed_key[:length] if length is not None else hashed_key

    return RANDOM_STORE[key]

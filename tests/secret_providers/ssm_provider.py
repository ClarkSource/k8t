# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import boto3
import pytest
from moto import mock_ssm
from k8t import config
from k8t.secret_providers.ssm_provider import get_secret


@mock_ssm
def test_ssm():
    region = "eu-west-1"
    client = boto3.client("ssm", region_name=region)

    client.put_parameter(
        Name="foo",
        Description="Global parameter",
        Value="global_secret_value",
        Type="SecureString",
        KeyId="alias/aws/ssm",
    )

    client.put_parameter(
        Name="/dev/test1",
        Description="Environment specific simple parameter",
        Value="string_value",
        Type="String",
    )

    client.put_parameter(
        Name="/app/dev/password",
        Description="Environment specific secret.",
        Value="my_secret_value",
        Type="SecureString",
        KeyId="alias/aws/ssm",
    )

    config.CONFIG = {"secrets": {"provider": "ssm", "region": region}}
    assert get_secret("foo") == "global_secret_value"
    assert get_secret("/dev/test1") == "string_value"
    assert get_secret("/app/dev/password") == "my_secret_value"

    with pytest.raises(AssertionError, match=r"Secret '/app/dev/password' did not have expected length of 3"):
        get_secret("/app/dev/password", 3)
    with pytest.raises(RuntimeError, match=r"Could not find secret: /Application/non_existent"):
        get_secret("/Application/non_existent")

    config.CONFIG = {"secrets": {"provider": "ssm", "region": region, "prefix": "/app/dev"}}
    assert get_secret("/password") == "my_secret_value"

    config.CONFIG = {"secrets": {"provider": "ssm", "region": "eu-central-1"}}
    with pytest.raises(RuntimeError, match=r"Could not find secret: foo"):
        get_secret("foo")


@mock_ssm
def test_ssm_default_region():
    region = "eu-central-1"
    client = boto3.client("ssm", region_name=region)

    client.put_parameter(
        Name="foo",
        Description="Global parameter",
        Value="global_secret_value",
        Type="SecureString",
        KeyId="alias/aws/ssm",
    )

    config.CONFIG = {"secrets": {"provider": "ssm"}}
    assert get_secret("foo") == "global_secret_value"

# vim: fenc=utf-8:ts=4:sw=4:expandtab
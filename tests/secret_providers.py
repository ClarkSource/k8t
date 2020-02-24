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
from k8t.secret_providers import random
from k8t.secret_providers import ssm


def test_random():
    length = 12

    assert random('/foobar', length) == random('/foobar', length) != random('/foobaz', length)

    result = random('/foobam', length)

    assert result == random('/foobam', length)


@mock_ssm
def test_ssm():
    region = "eu-central-1"
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

    response = ssm("foo", region)
    assert response == 'global_secret_value'
    response = ssm("/dev/test1", region)
    assert response == 'string_value'
    response = ssm("/app/dev/password", region)
    assert response == 'my_secret_value'

@mock_ssm
def test_ssm_nonexistent_parameter():
    region = "eu-central-1"

    with pytest.raises(RuntimeError, match=r"Could not find secret: /Application/non_existent"):
        ssm("/Application/non_existent", region)

# vim: fenc=utf-8:ts=4:sw=4:expandtab

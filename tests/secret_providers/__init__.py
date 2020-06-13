# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import pytest
from mock import patch
from k8t import config, secret_providers


def test_get_secret():
    config.CONFIG = {"secrets": {"provider": "random"}}
    with patch.object(secret_providers.random_provider, "get_secret") as mock:
        secret_providers.get_secret("any")
        mock.assert_called_with("any", None)
        secret_providers.get_secret("any", 99)
        mock.assert_called_with("any", 99)

    config.CONFIG = {"secrets": {"provider": "ssm"}}
    with patch.object(secret_providers.ssm_provider, "get_secret") as mock:
        secret_providers.get_secret("any")
        mock.assert_called_with("any", None)
        secret_providers.get_secret("any", 99)
        mock.assert_called_with("any", 99)

    config.CONFIG = {"secrets": {"provider": "stub"}}
    with patch.object(secret_providers.stub_provider, "get_secret") as mock:
        secret_providers.get_secret("any")
        mock.assert_called_with("any", None)
        secret_providers.get_secret("any", 99)
        mock.assert_called_with("any", 99)

    config.CONFIG = {"secrets": {"provider": "nothing"}}
    with pytest.raises(NotImplementedError, match=r"secret provider nothing does not exist."):
        secret_providers.get_secret("any")

    config.CONFIG = {}
    with pytest.raises(RuntimeError, match=r"Secrets provider not configured."):
        secret_providers.get_secret("any")

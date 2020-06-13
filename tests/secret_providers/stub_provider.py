# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from k8t import config, engine
from k8t.secret_providers.stub_provider import get_secret


def test_get_secret():
    assert str(get_secret("/foobar")) == '{{ SECRET("/foobar") }}'
    assert str(get_secret("/foobaz", 12)) == '{{ SECRET("/foobaz", 12) }}'


def test_filter_chaining():
    config.CONFIG = {"secrets": {"provider": "stub"}}
    values = {}
    eng = engine.build(".", None, None)

    template = eng.from_string('test: {{ get_secret("foo", 10) | default("bar") | hash }}')
    assert template.render(values) == 'test: {{ SECRET("foo", 10) | FILTER(do_default) | FILTER(hashf) }}'

# vim: fenc=utf-8:ts=4:sw=4:expandtab

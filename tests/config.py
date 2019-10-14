# -*- coding: utf-8 -*-
#
# Copyright © 2019 Clark Germany GmbH
# Author: Aljosha Friemann <aljosha.friemann@clark.de>

from kinja.config import validate


def test_validate():
    try:
        validate(dict(secrets=dict()))
    except AssertionError:
        return

    assert False, "validate should raise AssertionError when no secrets provider was defined"

# vim: fenc=utf-8:ts=4:sw=4:expandtab

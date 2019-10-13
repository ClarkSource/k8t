# -*- coding: utf-8 -*-
#
# Copyright © 2019 Clark Germany GmbH
# Author: Aljosha Friemann <aljosha.friemann@clark.de>

import boto3
from botocore.exceptions import UnknownParameterError
from kinja.logger import LOGGER


def SSM(key: str) -> str:
    LOGGER.debug('Requesting secret from %s', key)

    client = boto3.client('ssm')

    try:
        return client.get_parameter(Name=f"/{key}", WithDecryption=True)['Parameter']['Value']
    except client.exceptions.ParameterNotFound: 
        raise RuntimeError(f"Could not find secret: {key}")

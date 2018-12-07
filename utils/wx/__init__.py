#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 21/01/2018

"""
    微信相关服务实现
"""

import logging
import requests


logger = logging.getLogger(__name__)


class BaseWeChat(object):

    """

    `微信公众号开发`

    `微信商户开发`

    `微信开发平台`

    """

    API_BASE_URL = ""

    _http = requests.session()

    def __init__(self, app_id, timeout=None, session=None, auto_retry=True):
        self.app_id = app_id
        self.timeout = timeout
        self.session = session
        self.auto_retry = auto_retry

    def request(self, *args, **kwargs):
        raise NotImplementedError()

    def get(self, url, **kwargs):
        return self.request(
            method='get',
            url_or_endpoint=url,
            **kwargs
        )

    def post(self, url, **kwargs):
        return self.request(
            method='post',
            url_or_endpoint=url,
            **kwargs
        )

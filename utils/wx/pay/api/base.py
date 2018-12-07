#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/5/17


class BaseWeChatPayAPI(object):

    """

    微信支付API基类

    """

    def __init__(self, client=None):
        self._client = client

    def _get(self, url, **kwargs):
        if hasattr(self, "API_BASE_URL"):
            kwargs['api_base_url'] = getattr(self, "API_BASE_URL")
        return self._client.get(url, **kwargs)

    def _post(self, url, **kwargs):
        if hasattr(self, "API_BASE_URL"):
            kwargs['api_base_url'] = getattr(self, "API_BASE_URL")
        return self._client.post(url, **kwargs)

    @property
    def app_id(self):
        return self._client.app_id

    @property
    def mch_id(self):
        return self._client.mch_id

    @property
    def sub_mch_id(self):
        return self._client.sub_mch_id

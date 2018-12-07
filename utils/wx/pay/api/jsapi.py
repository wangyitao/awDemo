#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/6/27

import time

from django.utils.six import text_type
from django.utils.crypto import get_random_string

from utils.wx.pay.api.base import BaseWeChatPayAPI
from utils.wx.tools import calculate_signature


class WeChatJSAPI(BaseWeChatPayAPI):

    def get_jsapi_signature(self, prepay_id, timestamp=None, nonce_str=None):
        """获取 JSAPI 签名

        Parameters
        ----------
        prepay_id : string

            统一下单接口返回的 prepay_id 参数值

        timestamp: string

            时间戳，默认为当前时间戳

        nonce_str: string

            随机字符串，默认自动生成

        Returns
        -------
        string
        """
        data = {
            'appId': self.app_id,
            'timeStamp': timestamp or text_type(int(time.time())),
            'nonceStr': nonce_str or get_random_string(32),
            'signType': 'MD5',
            'package': 'prepay_id={0}'.format(prepay_id),
        }
        return calculate_signature(
            data,
            self._client.api_key if not self._client.debug else self._client.debug_api_key
        )

    def get_jsapi_params(self, prepay_id, timestamp=None, nonce_str=None, jssdk=False):
        """获取 JSAPI 参数

        Parameters
        ----------
        prepay_id : string

            统一下单接口返回的 prepay_id 参数值

        timestamp: string

            时间戳，默认为当前时间戳

        nonce_str: string

            随机字符串，默认自动生成

        jssdk: bool

            前端调用方式，默认使用 WeixinJSBridge

            使用 jssdk 调起支付的话，timestamp 的 s 为小写
            使用 WeixinJSBridge 调起支付的话，timeStamp 的 S 为大写

        Returns
        -------
        dict
        """

        data = {
            "appId": self.app_id,
            "timeStamp": timestamp or text_type(int(time.time())),
            "nonceStr": nonce_str or get_random_string(32),
            "signType": "MD5",
            "package": "prepay_id={0}".format(prepay_id)
        }
        sign = calculate_signature(
            data,
            self._client.api_key if not self._client.debug else self._client.debug_api_key
        )

        data['paySign'] = sign.upper()

        if jssdk:
            data['timestamp'] = data.pop('timeStamp')

        return data

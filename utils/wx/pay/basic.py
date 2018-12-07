#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/5/17

import inspect
import logging

from django.utils.crypto import get_random_string


from utils.wx import BaseWeChat
from utils.wx.pay import api
from utils.wx.pay.api.base import BaseWeChatPayAPI
from utils.wx.tools import calculate_signature
from utils.wx.tools import dict_to_xml
from utils.wx.tools import xml_to_dict

logger = logging.getLogger(__name__)


def _is_api_endpoint(instance):
    return issubclass(instance.__class__, BaseWeChatPayAPI)


class WeChatPay(BaseWeChat):

    API_BASE_URL = "https://api.mch.weixin.qq.com/"

    # 订单API
    order = api.WeChatOrder()
    # 工具API
    tools = api.WeChatTools()
    # 现金红包API
    red_pack = api.WeChatRedPack()
    # 公众号网页 JS 支付接口
    jsapi = api.WeChatJSAPI()
    # 微信退款API
    refund = api.WeChatRefund()

    def __new__(cls, *args, **kwargs):
        self = super(WeChatPay, cls).__new__(cls)
        api_endpoints = inspect.getmembers(self, _is_api_endpoint)
        for name, api_ins in api_endpoints:
            api_cls = type(api_ins)
            api_ins = api_cls(self)
            setattr(self, name, api_ins)
        return self

    def __init__(self, app_id, api_key_path, mch_id, session=None, sub_mch_id=None,
                 mch_cert=None, mch_key=None, timeout=None, debug=False):
        super(WeChatPay, self).__init__(
            app_id, timeout, session, False
        )
        self.api_key_path = api_key_path
        self.mch_id = mch_id
        self.sub_mch_id = sub_mch_id
        self.mch_cert = mch_cert
        self.mch_key = mch_key
        self.debug = debug
        self.debug_api_key = None

        with open(api_key_path, ) as f:
            self.api_key = f.read().strip("\n")

    def request(self, method, url_or_endpoint, **kwargs):
        if not url_or_endpoint.startswith(('http://', 'https://')):
            api_base_url = kwargs.pop('api_base_url', self.API_BASE_URL)
            if self.debug:
                api_base_url = '{url}sandboxnew/'.format(url=api_base_url)
            url = '{base}{endpoint}'.format(
                base=api_base_url,
                endpoint=url_or_endpoint
            )
        else:
            url = url_or_endpoint

        if isinstance(kwargs.get("data", ""), dict):
            data = kwargs["data"]
            if "mchid" not in data:
                # Fuck Tencent
                data.setdefault("mch_id", self.mch_id)

            if self.sub_mch_id:
                data.setdefault("sub_mch_id", self.sub_mch_id)

            if "nonce_str" not in data:
                data.setdefault("nonce_str", get_random_string(32))

            if self.debug:
                self.debug_api_key = self._fetch_sanbox_api_key()

            data.pop("sign", None)

            sign = calculate_signature(data, self.debug_api_key if self.debug else self.api_key)

            data["sign"] = sign.upper() if self.debug else sign

            body = dict_to_xml(data)

            body = body.encode('utf-8')
            kwargs["data"] = body

        res = self._http.request(
            method=method,
            url=url,
            **kwargs
        )

        res.raise_for_status()

        return self._handle_result(res)

    def get(self, url, **kwargs):
        return self.request(
            method="get",
            url_or_endpoint=url,
            **kwargs
        )

    def post(self, url, **kwargs):
        return self.request(
            method="post",
            url_or_endpoint=url,
            **kwargs
        )

    def _handle_result(self, res):
        data = xml_to_dict(res.content)

        return_code = data["return_code"]

        if return_code != "SUCCESS" and data.get("result_code") != "SUCCESS":
            if self.app_id != data.get("appid"):
                raise ValueError("{}: {}".format(data.get("return_code"), data.get("return_msg")))

        logger.info("WxApi pay res: return_code is {}".format(return_code))

        return data

    def _fetch_sanbox_api_key(self):
        nonce_str = get_random_string(32)
        sign = calculate_signature({'mch_id': self.mch_id, 'nonce_str': nonce_str}, self.api_key)
        payload = dict_to_xml({
            "mch_id": self.mch_id,
            "nonce_str": nonce_str,
            "sign": sign
        })
        headers = {'Content-Type': 'text/xml'}
        api_url = '{base}sandboxnew/pay/getsignkey'.format(base=self.API_BASE_URL)
        response = self._http.post(api_url, data=payload, headers=headers)
        return xml_to_dict(response.text).get("sandbox_signkey")

    def parse_payment_result(self, xml):
        """解析微信支付结果通知

        """
        data = xml_to_dict(xml)

        sign = data.pop('sign', None)

        real_sign = calculate_signature(data, self.api_key if not self.debug else self.debug_api_key)

        if sign != real_sign:
            # 校验签名失败
            data["state"] = False

        for key in ('total_fee', 'settlement_total_fee', 'cash_fee', 'coupon_fee', 'coupon_count'):
            if key in data:
                data[key] = int(data[key])
        data['sign'] = sign

        return data

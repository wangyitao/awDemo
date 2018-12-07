#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/6/27

"""
    微信api调用出口
"""

from django.conf import settings
from django.utils.functional import LazyObject

from utils.wx.client import WeChatClient
from utils.wx.pay import WeChatPay
from utils.wx.others.oauth import WeChatOAuth


class WxApi(object):

    """
    封装接口, 使用直接调用
    """

    # 注册微信配置
    WECHAT_CONFIG = settings.THIRD_PART_CONFIG["WX"]

    def __init__(self, ):
        # 注册消息类api
        self.client = WeChatClient(
            app_id=self.WECHAT_CONFIG["app_id"],
            secret=self.WECHAT_CONFIG["secret"],
        )
        # 注册支付类api
        self.pay = WeChatPay(
            app_id=self.WECHAT_CONFIG["app_id"],
            api_key_path=self.WECHAT_CONFIG["api_key_path"],
            mch_id=self.WECHAT_CONFIG["mch_id"],
            debug=self.WECHAT_CONFIG["debug"]
        )
        # 注册 oauth认证
        self.oauth = WeChatOAuth(
            app_id=self.WECHAT_CONFIG["app_id"],
            secret=self.WECHAT_CONFIG["secret"],
            redirect_uri=self.WECHAT_CONFIG["redirect_uri"]
        )


class DefaultApi(LazyObject):

    def _setup(self):
        self._wrapped = WxApi()


wx_api = DefaultApi()

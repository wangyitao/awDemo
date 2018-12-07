#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/5/14

import json
import time
import inspect
import logging
import requests
import threading

from django.conf import settings
from django.core.mail import send_mail

from utils.wx.client.api.base import BaseWeChatClientAPI
from utils.wx.errcodes import WeChatErrorCode
from utils.wx.client import api
from utils.wx import BaseWeChat

logger = logging.getLogger(__name__)


def _is_api_endpoint(instance):
    return issubclass(instance.__class__, BaseWeChatClientAPI)


class WeChatClient(BaseWeChat):

    API_BASE_URL = "https://api.weixin.qq.com/cgi-bin/"

    # 消息
    message = api.WeChatMessage()
    # 用户
    user = api.WeChatUser()
    # 混合工具
    misc = api.WeChatMisc()

    def __new__(cls, *args, **kwargs):
        self = super(WeChatClient, cls).__new__(cls)
        api_endpoints = inspect.getmembers(self, _is_api_endpoint)
        for name, api_ins in api_endpoints:
            api_cls = type(api_ins)
            api_ins = api_cls(self)
            setattr(self, name, api_ins)
        return self

    def __init__(self, app_id, secret, timeout=None, session=None, auto_retry=True):
        super(WeChatClient, self).__init__(
            app_id, timeout, session, auto_retry
        )
        self.secret = secret
        self.expires_at = 0
        self.__access_token = None

    def _handle_result(self, res, method=None, url=None,
                       result_processor=None, **kwargs):
        """结果解析

        Parameters
        ----------
        res : request instance

            响应对象 response

        method : string

            请求方法

        url : string

            请求的 `url`

        result_processor: func

            结果处理器

        kwargs: dict

            更多参数


        Returns
        -------
        dict
        """
        if not isinstance(res, dict):
            result = res.json()
        else:
            result = res

        if not isinstance(result, dict):
            return result

        if "base_resp" in result:
            # Different response in device APIs. Fuck Tencent!
            result.update(errcode=result.pop("base_resp"))

        if "errcode" in result:
            result["errcode"] = int(result["errcode"])

        if "errcode" in result and result["errcode"] != 0:
            errcode = result["errcode"]
            errmsg = result.get("errmsg", errcode)

            # 启动重试发送
            if self.auto_retry and errcode in (
                    WeChatErrorCode.INVALID_CREDENTIAL.value,
                    WeChatErrorCode.INVALID_ACCESS_TOKEN.value,
                    WeChatErrorCode.EXPIRED_ACCESS_TOKEN.value,):
                logger.info("Access token expired, fetch a new one and retry request")

                kwargs["params"]["access_token"] = self._fetch_access_token()

                return self.request(
                    method=method,
                    url_or_endpoint=url,
                    result_processor=result_processor,
                    **kwargs
                )

            elif errcode == WeChatErrorCode.OUT_OF_API_FREQ_LIMIT.value:
                # api 使用频率超过限制
                logger.error("Beyond API limits wx request:  {}".format(errmsg))

            else:
                # api 其它异常
                logger.error("Invalid wx request: {} {}".format(errcode, errmsg))

        logger.info("WxApi client res: {}".format(result))

        return result if not result_processor else result_processor(result)

    def request(self, method, url_or_endpoint, **kwargs):

        if not url_or_endpoint.startswith(("http://", "https://")):
            api_base_url = kwargs.pop("api_base_url", self.API_BASE_URL)
            url = "{base}{endpoint}".format(
                base=api_base_url,
                endpoint=url_or_endpoint
            )
        else:
            url = url_or_endpoint

        if "params" not in kwargs:
            kwargs["params"] = {}

        if isinstance(kwargs["params"], dict):
            kwargs["params"]["access_token"] = self.access_token

        if isinstance(kwargs.get("data", ""), dict):
            body = json.dumps(kwargs["data"], ensure_ascii=False)
            body = body.encode('utf-8')
            kwargs['data'] = body

        kwargs["timeout"] = kwargs.get("timeout", self.timeout)
        result_processor = kwargs.pop("result_processor", None)

        res = self._http.request(
            method=method,
            url=url,
            **kwargs
        )

        try:
            res.raise_for_status()
        except requests.RequestException as exc:
            logger.error(str(exc))
            # 发送错误消息至

        return self._handle_result(
            res, method, url, result_processor, **kwargs
        )

    def _fetch_access_token(self):

        logger.info("Fetching access token appid is {}, secret is {}".format(
            self.app_id, self.secret
        ))

        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.secret
        }

        res = self._http.get(url=url, params=params)

        res.raise_for_status()

        result = res.json()

        # 如果获取不到凭证进行通知
        if "errcode" in result and result["errcode"] != WeChatErrorCode.SUCCESS.value:
            task = threading.Thread(
                target=send_mail,
                args=(
                    "获取微信凭证失败通知", str(result),
                    settings.DEFAULT_FROM_EMAIL, settings.DEFAULT_TO_EMAILS
                )
            )
            task.start()

        self.expires_at = int(time.time()) + result.get("expires_in", 0)

        self.__access_token = result.get("access_token", )

        return result.get("access_token", )

    @property
    def access_token(self):
        """get access_token

            公众平台全局通用凭证

        Parameters
        ----------

        Returns
        -------
        access_token: string
        """

        if self.__access_token:
            if not self.expires_at:
                # user provided access_token, just return it
                return self.__access_token

            timestamp = time.time()
            if self.expires_at - timestamp > 300:
                return self.__access_token

        self._fetch_access_token()

        return self.__access_token

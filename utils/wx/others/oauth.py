#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/6/29

import json
import logging
import requests

from django.utils import six

logger = logging.getLogger(__name__)


class WeChatOAuth(object):
    """ 微信公众平台 OAuth 网页授权

    详情参考
    https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&t=resource/res_list&verify=1&id=open1419316505
    """

    _http = requests.session()

    API_BASE_URL = "https://api.weixin.qq.com/"
    OAUTH_BASE_URL = "https://open.weixin.qq.com/connect/"

    def __init__(self, app_id, secret, redirect_uri=""):
        """初始化参数

        Parameters
        ----------

        app_id: string
            微信公众号 app_id

        secret: string
            微信公众号 secret

        redirect_uri: string
            OAuth2 redirect URI

        Returns
        -------
        dict
        """

        # 传入参数
        self.app_id = app_id
        self.secret = secret
        self.redirect_uri = redirect_uri

        # 关键参数
        self.access_token = None
        self.openid = None
        self.expires_in = None
        self.refresh_token = None

    def _request(self, method, url_or_endpoint, **kwargs):
        if not url_or_endpoint.startswith(('http://', 'https://')):
            url = '{base}{endpoint}'.format(
                base=self.API_BASE_URL,
                endpoint=url_or_endpoint
            )
        else:
            url = url_or_endpoint

        if isinstance(kwargs.get('data', ''), dict):
            body = json.dumps(kwargs['data'], ensure_ascii=False)
            body = body.encode('utf-8')
            kwargs['data'] = body

        res = self._http.request(
            method=method,
            url=url,
            **kwargs
        )

        res.raise_for_status()

        result = json.loads(res.content.decode('utf-8', 'ignore'), strict=False)

        if 'errcode' in result and result['errcode'] != 0:
            errcode = result['errcode']
            errmsg = result['errmsg']
            logger.error("Invalid wx request: code: {}, msg: {}".format(errcode, errmsg))

        logger.info("WxApi oauth res: {}".format(result))

        return result

    def _get(self, url, **kwargs):
        return self._request(
            method='get',
            url_or_endpoint=url,
            **kwargs
        )

    def authorize_url(self, scope="snsapi_base", state="",):
        """获取授权跳转地址

        Parameters
        ----------

        scope: string
            应用授权作用域
            snsapi_base 不弹出授权页面，直接跳转，只能获取用户openid
            snsapi_userinfo （弹出授权页面，可通过openid拿到昵称、性别、所在地
            即使在未关注的情况下，只要用户授权，也能获取其信息

        state: string
            重定向后会带上state参数，开发者可以填写a-zA-Z0-9的参数值，最多128字节

        Returns
        -------
        string
        """
        redirect_uri = six.moves.urllib.parse.quote(self.redirect_uri, safe='')
        url_list = [
            self.OAUTH_BASE_URL,
            'oauth2/authorize?appid=',
            self.app_id,
            '&redirect_uri=',
            redirect_uri,
            '&response_type=code&scope=',
            scope
        ]
        if state:
            url_list.extend(['&state=', state])
        url_list.append('#wechat_redirect')
        return ''.join(url_list)

    def qrconnect_url(self, state=""):
        """生成扫码登录地址

        """
        redirect_uri = six.moves.urllib.parse.quote(self.redirect_uri, safe='')
        url_list = [
            self.OAUTH_BASE_URL,
            'qrconnect?appid=',
            self.app_id,
            '&redirect_uri=',
            redirect_uri,
            '&response_type=code&scope=',
            'snsapi_login'  # scope
        ]
        if state:
            url_list.extend(['&state=', state])
        url_list.append('#wechat_redirect')
        return ''.join(url_list)

    def fetch_access_token(self, code):
        """获取 access_token

        Parameters
        ----------

        code: string
            授权完成跳转回来后 URL 中的 code 参数

        Returns
        -------
        dict
        """
        res = self._get(
            'sns/oauth2/access_token',
            params={
                'appid': self.app_id,
                'secret': self.secret,
                'code': code,
                'grant_type': 'authorization_code'
            }
        )
        self.access_token = res.get("access_token")
        self.openid = res.get("openid")
        self.refresh_token = res.get("refresh_token")
        self.expires_in = res.get("expires_in")
        return res

    def refresh_access_token(self, refresh_token):
        """刷新 access token

        Parameters
        ----------

        refresh_token: string
            OAuth2 refresh token

        Returns
        -------
        dict
        """
        res = self._get(
            'sns/oauth2/refresh_token',
            params={
                'appid': self.app_id,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
        )
        self.access_token = res['access_token']
        self.openid = res['openid']
        self.refresh_token = res['refresh_token']
        self.expires_in = res['expires_in']
        return res

    def get_user_info(self, openid=None, access_token=None, lang="zh_CN"):
        """获取用户信息

        Parameters
        ----------

        openid: string
            可选，微信 openid，默认获取当前授权用户信息

        access_token: string
            可选，access_token，默认使用当前授权用户的 access_token

        lang: string
            可选，语言偏好, 默认为 `zh_CN`


        Returns
        -------
        dict
        """
        openid = openid or self.openid
        access_token = access_token or self.access_token
        return self._get(
            'sns/userinfo',
            params={
                'access_token': access_token,
                'openid': openid,
                'lang': lang
            }
        )

    def check_access_token(self, openid=None, access_token=None):
        """检查 access_token 有效性

        Parameters
        ----------

        openid: string
            可选, 微信 openid，默认获取当前授权用户信息

        access_token: string
            可选, access_token，默认使用当前授权用户的 access_token
                网页授权接口调用凭证, 注意：此access_token与基础支持的access_token不同

        Returns
        -------
        bool
        """
        openid = openid or self.openid
        access_token = access_token or self.access_token
        res = self._get(
            'sns/auth',
            params={
                'access_token': access_token,
                'openid': openid
            }
        )
        if res['errcode'] == 0:
            return True
        return False

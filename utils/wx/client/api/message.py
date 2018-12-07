#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/5/17

from django.utils import six
from django.utils.crypto import get_random_string

from utils.wx.client.api.base import BaseWeChatClientAPI


class WeChatMessage(BaseWeChatClientAPI):

    """
    微信发送消息 API, 持续扩展中
    """

    def _send_custom_message(self, data, account=None):
        data = data or {}
        if account:
            data['customservice'] = {'kf_account': account}
        return self._post(
            'message/custom/send',
            data=data
        )

    def send_text(self, openid, content, account=None):
        """发送文本消息

        详情请参考
        http://mp.weixin.qq.com/wiki/7/12a5a320ae96fecdf0e15cb06123de9f.html

        Parameters
        ----------
        openid : string

            用户唯一账号标识

        content : string

            消息正文

        account : string

            可选，客服账号


        Returns
        -------
        dict
        """
        data = {
            'touser': openid,
            'msgtype': 'text',
            'text': {'content': content}
        }
        return self._send_custom_message(data, account=account)

    def send_template(self, openid, template_id, data, url=None, mini_program=None):
        """发送模板消息

        详情请参考
        https://mp.weixin.qq.com/wiki?id=mp1445241432&lang=zh_CN

        Parameters
        ----------
        openid : string

            用户唯一账号标识

        template_id: string

            模板 ID, 在公众平台线上模板库中选用模板获得

        data: dict

            模板消息数据

        url: string

            链接地址

        mini_program: string

            跳小程序所需数据, 如：`{'appid': 'appid', 'pagepath': 'index?foo=bar'}`

        Returns
        -------
        dict
        """
        tpl_data = {
            "touser": openid,
            "template_id": template_id,
            "url": url,
            "miniprogram": mini_program,
            "data": data
        }
        return self._post(
            "message/template/send",
            data=tpl_data
        )

    def send_articles(self, openid, articles, account=None):
        """发送图文消息

            图文消息条数限制在8条以内，注意，如果图文数超过8，则将会无响应

        详情请参考
        http://mp.weixin.qq.com/wiki/7/12a5a320ae96fecdf0e15cb06123de9f.html

        Parameters
        ----------
        openid : string
            用户 ID 。 就是你收到的 `Message` 的 source

        articles : string

            一个包含至多10个图文的数组, 或者微信图文消息素材 media_id

        account : string

            可选，客服账号


        Returns
        -------
        True or False: bool
        """
        if isinstance(articles, (tuple, list)):
            articles_data = []
            for article in articles:
                articles_data.append({
                    'title': article['title'],
                    'description': article['description'],
                    'url': article['url'],
                    'picurl': article.get('image', article.get('picurl')),
                })
            data = {
                'touser': openid,
                'msgtype': 'news',
                'news': {
                    'articles': articles_data
                }
            }
        else:
            data = {
                'touser': openid,
                'msgtype': 'mpnews',
                'mpnews': {
                    'media_id': articles,
                }
            }
        return self._send_custom_message(data, account=account)

    def send_subscribe_template(self, openid, template_id, scene, title, data, url=None):
        """一次性订阅消息，通过API推送订阅模板消息给到授权微信用户

            当前对应公众号订阅消息模板ID:


        详情请参考
        https://mp.weixin.qq.com/wiki?id=mp1500374289_66bvB

        Parameters
        ----------
        openid : string
            用户唯一账号标识

        template_id : string
            订阅消息模板ID

        scene : int
            订阅场景值，开发者可以填0-10000的整形值，用来标识订阅场景值

        title: string
            消息标题，15字以内

        data: dict
            消息正文，value为消息内容，color为颜色，200字以内

        url: string
            点击消息跳转的链接，需要有ICP备案

        Returns
        -------
        True or False: bool
        """
        post_data = {
            'touser': openid,
            'template_id': template_id,
            'url': url,
            'scene': scene,
            'title': title,
            'data': data,
        }
        if url is not None:
            post_data['url'] = url
        return self._post(
            'message/template/subscribe',
            data=post_data,
        )

    def get_subscribe_authorize_url(self, scene, template_id, redirect_url, reserved=None):
        """构造请求用户授权的url

        详情请参考
        https://mp.weixin.qq.com/wiki?id=mp1500374289_66bvB

        Parameters
        ----------
        scene : int
            订阅场景值，开发者可以填0-10000的整形值，用来标识订阅场景值

        template_id : string
            订阅消息模板ID，登录公众平台后台，在接口权限列表处可查看订阅模板ID

        redirect_url : string
            授权后重定向的回调地址

        reserved:
            用于保持请求和回调的状态，授权请后原样带回给第三方。该参数可用于防止csrf攻击。若不指定则随机生成。

        Returns
        -------
        dict
        """
        if reserved is None:
            reserved = get_random_string(16)
        base_url = 'https://mp.weixin.qq.com/mp/subscribemsg'
        params = [
            ('action', 'get_confirm'),
            ('appid', self.app_id),
            ('scene', scene),
            ('template_id', template_id),
            ('redirect_url', redirect_url),
            ('reserved', reserved),
        ]
        encoded_params = six.moves.urllib.parse.urlencode(params)
        url = '{base}?{params}#wechat_redirect'.format(base=base_url, params=encoded_params)
        return url

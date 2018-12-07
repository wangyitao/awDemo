#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/6/29


from utils.wx.client.api.base import BaseWeChatClientAPI


class WeChatUser(BaseWeChatClientAPI):

    def get(self, openid, lang='zh_CN'):
        """获取用户基本信息（包括UnionID机制）

        详情参考: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421140839

        Parameters
        ----------

        openid: string
            普通用户的标识，对当前公众号唯一

        lang: string
            返回国家地区语言版本，zh_CN 简体，zh_TW 繁体，en 英语

        Returns
        -------
        dict
        """
        assert lang in ('zh_CN', 'zh_TW', 'en')
        return self._get(
            'user/info',
            params={
                'openid': openid,
                'lang': lang
            }
        )

    def get_followers(self, first_openid=None):
        """获取用户列表

        详情参考: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421140840

        Parameters
        ----------

        first_openid: string
            可选。第一个拉取的 openid，不填默认从头开始拉取

        Returns
        -------
        dict
        """
        params = {}
        if first_openid:
            params['next_openid'] = first_openid
        return self._get(
            'user/get',
            params=params
        )

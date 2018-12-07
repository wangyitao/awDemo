#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/6/29


from utils.wx.client.api.base import BaseWeChatClientAPI


class WeChatMisc(BaseWeChatClientAPI):

    def short_url(self, long_url):
        """将一条长链接转成短链接

        详情参考:
            http://mp.weixin.qq.com/wiki/10/165c9b15eddcfbd8699ac12b0bd89ae6.html

        Parameters
        ----------

        long_url: string
            长链接地址

        Returns
        -------
        string
        """
        return self._post(
            'shorturl',
            data={
                'action': 'long2short',
                'long_url': long_url
            }
        )

    def get_wechat_ips(self):
        """获取微信服务器 IP 地址列表

        Returns
        -------
        string
        """
        return self._get('getcallbackip', result_processor=lambda x: x['ip_list'])

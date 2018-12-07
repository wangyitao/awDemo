#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/5/18

"""
    微信支付提供的一些工具API
"""

from datetime import datetime, date

from utils.wx.pay.api.base import BaseWeChatPayAPI


class WeChatTools(BaseWeChatPayAPI):

    def short_url(self, long_url):
        """长连接转短链接

        该接口主要用于扫码原生支付模式一中的二维码链接转成短链接(weixin://wxpay/s/XXXXXX)，
            减小二维码数据量，提升扫描速度和精确度


        Parameters
        ----------

        long_url: string

            需要转换的URL，签名用原串，传输需URLencode


        Returns
        -------
        dict
        """
        data = {
            "appid": self.app_id,
            "long_url": long_url,
        }
        return self._post('tools/shorturl', data=data)

    def download_bill(self, bill_date, bill_type='ALL', device_info=None):
        """下载对账单


        Parameters
        ----------

        bill_date: string

            下载对账单的日期

        bill_type: string, default: ALL

            账单类型，ALL，返回当日所有订单信息，默认值
            SUCCESS，返回当日成功支付的订单,
            REFUND，返回当日退款订单,
            REVOKED，已撤销的订单

        device_info: string, default: None

            微信支付分配的终端设备号，填写此字段，只下载该设备号的对账单

        """
        if isinstance(bill_date, (datetime, date)):
            bill_date = bill_date.strftime('%Y%m%d')

        data = {
            "appid": self.app_id,
            "bill_date": bill_date,
            "bill_type": bill_type,
            "device_info": device_info,
        }
        return self._post('pay/downloadbill', data=data)

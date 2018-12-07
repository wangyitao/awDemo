#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/5/17

"""
    微信订单相关API
"""

import logging

from utils.wx.pay.api.base import BaseWeChatPayAPI


logger = logging.getLogger(__name__)


class WeChatOrder(BaseWeChatPayAPI):

    def create(
        self, body, out_trade_no, total_fee, spbill_create_ip, notify_url, trade_type="NATIVE", **kwargs
    ):
        """统一下单接口

        Parameters
        ----------
        body : string

            商品描述

        out_trade_no : string

            商户订单号

        total_fee : string

            标价金额(订单总金额，单位为分，详见支付金额)

        spbill_create_ip : string

            APP和网页支付提交用户端ip，Native支付填调用微信支付API的机器IP

        trade_type: string, default: NATIVE

            交易类型，取值如下：JSAPI，NATIVE，APP，WAP, MWEB

        notify_url: string

            异步接收微信支付结果通知的回调地址，通知url必须为外网可访问的url，不能携带参数

            example: http://www.weixin.qq.com/wxpay/pay.php

        kwargs: dict

            扩展业务参数, 可不传

            time_start: string

                订单生成时间，格式为yyyyMMddHHmmss(标准北京时间)

            time_expire: string

                订单失效时间，格式为yyyyMMddHHmmss(标准北京时间)

                订单失效时间是针对订单号而言的，
                由于在请求支付的时候有一个必传参数prepay_id只有两小时的有效期，
                所以在重入时间超过2小时的时候需要重新请求下单接口获取新的prepay_id

                建议：最短失效时间间隔大于1分钟

            goods_tag: string

                订单优惠标记，使用代金券或立减优惠功能时需要的参数

                参见: https://pay.weixin.qq.com/wiki/doc/api/tools/sp_coupon.php?chapter=12_1

            device_info: string

                自定义参数，可以为终端设备号(门店号或收银设备ID)，PC网页或公众号内支付可以传"WEB"

            detail: string

                商品详情

            attach: string

                附加数据，在查询API和支付通知中原样返回，可作为自定义参数使用

                例如, 购物车统一下单时使用

            fee_type: string

                符合ISO 4217标准的三位字母代码，默认人民币：CNY，
                详细参见: https://pay.weixin.qq.com/wiki/doc/api/native.php?chapter=4_2

            openid: string

                trade_type=JSAPI时（即公众号支付），此参数必传，此参数为微信用户在商户对应appid下的唯一标识

            更多移步 => https://pay.weixin.qq.com/wiki/doc/api/native.php?chapter=9_1


        Returns
        -------
        dict
        """
        data = {
            "appid": self.app_id,
            "body": body,
            "out_trade_no": out_trade_no,
            "total_fee": total_fee,
            "spbill_create_ip": spbill_create_ip,
            "notify_url": notify_url,
            "trade_type": trade_type,
        }
        data.update(**kwargs)
        logger.info("{}".format(data))
        return self._post('pay/unifiedorder', data=data)

    def query(self, transaction_id=None, out_trade_no=None):
        """查询订单

        Parameters
        ----------
        transaction_id : string

            微信的订单号，优先使用

        out_trade_no: string

            商户系统内部的订单号，当没提供transaction_id时需要传这个

        Returns
        -------
        dict
        """
        data = {
            "appid": self.app_id,
            "transaction_id": transaction_id,
            "out_trade_no": out_trade_no,
        }
        return self._post('pay/orderquery', data=data)

    def close(self, out_trade_no):
        """关闭订单

        Parameters
        ----------

        out_trade_no: string

            商户系统内部的订单号

        Returns
        -------
        dict
        """
        data = {
            "appid": self.app_id,
            "out_trade_no": out_trade_no,
        }
        return self._post('pay/closeorder', data=data)

    def reverse(self, transaction_id=None, out_trade_no=None):
        """撤销订单

        `transaction_id` `out_trade_no` 二选一

        如果同时存在优先级：transaction_id > out_trade_no

        Parameters
        ----------

        transaction_id: string

            可选，微信的订单号，优先使用

        out_trade_no: string

            商户系统内部的订单号

        Returns
        -------
        dict
        """
        data = {
            "appid": self.app_id,
            "transaction_id": transaction_id,
            "out_trade_no": out_trade_no,
        }
        return self._post('secapi/pay/reverse', data=data)

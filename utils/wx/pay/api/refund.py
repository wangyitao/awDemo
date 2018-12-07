#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/6/28

from utils.wx.pay.api.base import BaseWeChatPayAPI


class WeChatRefund(BaseWeChatPayAPI):

    def apply(self, total_fee, refund_fee, out_refund_no, transaction_id=None,
              out_trade_no=None, fee_type='CNY', op_user_id=None,
              device_info=None, refund_account='REFUND_SOURCE_UNSETTLED_FUNDS',
              notify_url=None):
        """申请退款

        Parameters
        ----------
        total_fee : string
            订单总金额，单位为分

        refund_fee: string
            退款总金额，单位为分

        out_refund_no: string
            商户系统内部的退款单号，商户系统内部唯一，同一退款单号多次请求只退一笔

        transaction_id: string
            可选, 微信订单号

        out_trade_no: string
            可选，商户系统内部的订单号，与 transaction_id 二选一

        fee_type: string
            可选，货币类型，符合ISO 4217标准的三位字母代码，默认人民币：CNY

        op_user_id: string
            可选，操作员帐号, 默认为商户号

        device_info: string
            可选，终端设备号

        refund_account: string
            可选，退款资金来源，仅针对老资金流商户使用，默认使用未结算资金退款

        notify_url: string
            可选，异步接收微信支付退款结果通知的回调地址

        Returns
        -------
        dict
        """
        data = {
            "appid": self.app_id,
            "device_info": device_info,
            "transaction_id": transaction_id,
            "out_trade_no": out_trade_no,
            "out_refund_no": out_refund_no,
            "total_fee": total_fee,
            "refund_fee": refund_fee,
            "refund_fee_type": fee_type,
            "op_user_id": op_user_id if op_user_id else self.mch_id,
            "refund_account": refund_account,
            "notify_url": notify_url,
        }
        return self._post("secapi/pay/refund", data=data)

    def query(self, refund_id=None, out_refund_no=None, transaction_id=None,
              out_trade_no=None, device_info=None):
        """查询退款

        Parameters
        ----------
        refund_id : string
            微信退款单号

        out_refund_no: string
            商户退款单号

        transaction_id: string
            微信订单号

        out_trade_no: string
            商户系统内部的订单号

        device_info: string
            可选，终端设备号

        Returns
        -------
        dict
        """
        data = {
            "appid": self.app_id,
            "device_info": device_info,
            "transaction_id": transaction_id,
            "out_trade_no": out_trade_no,
            "out_refund_no": out_refund_no,
            "refund_id": refund_id,
        }
        return self._post("pay/refundquery", data=data)

#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
    微信红包相关API
"""


from utils.wx.pay.api.base import BaseWeChatPayAPI


class WeChatRedPack(BaseWeChatPayAPI):

    def send(
        self, mch_billno, re_openid, total_amount, wishing, client_ip, act_name, remark, send_name,
        total_num=1, **kwargs
    ):
        """发送普通红包

        发放规则移步至 ==> https://pay.weixin.qq.com/wiki/doc/api/tools/cash_coupon.php?chapter=13_4&index=3


        Parameters
        ----------

        mch_billno: string

            商户订单号

        re_openid: string

            接受红包的用户, 用户在wxappid下的openid

        total_amount: string OR int

            付款金额，单位分

        wishing: string

            红包祝福语

        client_ip: string

            调用接口的机器Ip地址

        act_name: string

            活动名称

        remark: string

            备注信息

        send_name: string

            商户名称

        total_num: int, default: 1

            红包发放总人数, total_num=1

        kwargs: dict

            可选

            scene_id: string

                场景ID

                发放红包使用场景，红包金额大于200时必传

                PRODUCT_1:商品促销
                PRODUCT_2:抽奖
                PRODUCT_3:虚拟物品兑奖
                PRODUCT_4:企业内部福利
                PRODUCT_5:渠道分润
                PRODUCT_6:保险回馈
                PRODUCT_7:彩票派奖
                PRODUCT_8:税务刮奖

            risk_info: string

                活动信息

                posttime:用户操作的时间戳
                mobile:业务系统账号的手机号，国家代码-手机号。不需要+号
                deviceid :mac 地址或者设备唯一标识
                clientversion :用户操作的客户端版本

                把值为非空的信息用key=value进行拼接，再进行urlencode
                urlencode(posttime=xx& mobile =xx&deviceid=xx)

            consume_mch_id: string

                资金授权商户号, 服务商替特约商户发放时使用

        Returns
        -------
        dict
        """

        data = {
            "wxappid": self.app_id,
            "re_openid": re_openid,
            "total_amount": total_amount,
            "send_name": send_name,
            "act_name": act_name,
            "wishing": wishing,
            "remark": remark,
            "client_ip": client_ip,
            "total_num": total_num,
            "mch_billno": mch_billno,
        }

        data.update(**kwargs)

        return self._post("mmpaymkttransfers/sendredpack", data=data)

    def send_group(
        self, mch_billno, send_name, re_openid, total_amount, total_num, wishing, act_name, remark,
        amt_type="ALL_RAND", scene_id=None, risk_info=None, consume_mch_id=None
    ):
        """发送裂变红包

        Parameters
        ----------
        mch_billno: string

            商户订单号

        send_name: string

             商户名称

        re_openid: string

            接受红包的用户, 用户在wxappid下的openid

        total_amount: string

            付款金额，单位分

        total_num: string

            红包发放总人数, total_num=1

        wishing: string

            红包祝福语

        act_name: string

            活动名称

        remark: string

            备注信息

        amt_type: string

            红包金额设置方式
            ALL_RAND—全部随机,商户指定总金额和红包发放总人数，由微信支付随机计算出各红包金额

        scene_id: string

            场景id, 同普通红包API

        risk_info: string

            活动信息, 同普通红包API

        consume_mch_id: string

            资金授权商户号, 同普通红包API

        Returns
        -------
        dict
        """

        data = {
            "mch_billno": mch_billno,
            "send_name": send_name,
            "re_openid": re_openid,
            "total_amount": total_amount,
            "total_num": total_num,
            "wishing": wishing,
            "act_name": act_name,
            "remark": remark,
            "amt_type": amt_type,
            "scene_id": scene_id,
            "risk_info": risk_info,
            "consume_mch_id": consume_mch_id,
        }

        return self._post("mmpaymkttransfers/sendgroupredpack", data=data)

    def query(self, mch_billno, bill_type='MCHT'):
        """查询红包发放记录

        Parameters
        ----------
        mch_billno: string

            转换的数据

        bill_type: string

        Returns
        -------
        dict
        """
        data = {
            "mch_billno": mch_billno,
            "bill_type": bill_type,
            "appid": self.app_id,
        }
        return self._post("mmpaymkttransfers/gethbinfo", data=data)

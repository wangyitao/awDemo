#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/8/2

import time
import uuid

from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256

from base64 import encodebytes


def calculate_signature(params, api_key):
    """计算签名

    """
    signer = PKCS1_v1_5.new(api_key)
    signature = signer.sign(SHA256.new(params))
    # base64 编码，转换为unicode表示并移除回车
    sign = encodebytes(signature).decode("utf8").replace("\n", "")
    return sign


def get_uuid():
    """获取 `UUID`

    """
    return str(uuid.uuid4())


def get_iso_8061_date():
    """获取 `iso` 标准时间

    """
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

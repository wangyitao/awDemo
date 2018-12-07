#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/5/18

import hashlib
import logging

from xml.etree import ElementTree as EleTree


logger = logging.getLogger(__name__)


def format_params(params, api_key=None):
    data = ["{0}={1}".format(k, params[k]) for k in sorted(params) if params[k]]

    if api_key:
        data.append("key={0}".format(api_key))

    return "&".join(data)


def calculate_signature(params, api_key, sign_type="MD5"):

    if sign_type == "MD5":
        h = hashlib.md5()
    else:
        h = hashlib.md5()

    params_string = format_params(params, api_key)

    h.update(bytes(params_string, encoding="utf-8"))

    return h.hexdigest().upper()


def dict_to_xml(data):
    """将 `dict` 转化为 `xml`.


    Parameters
    ----------
    data: dict

        转换的数据

    Returns
    -------
    string
    """
    xml_list = ["<xml>"]
    for k, v in data.items():

        if not v:
            continue

        if str(v).isdigit():
            xml_list.append("<{0}>{1}</{0}>".format(k, v))
        else:
            xml_list.append("<{0}><![CDATA[{1}]]></{0}>".format(k, v))
    xml_list.append("</xml>")
    return "".join(xml_list)


def xml_to_dict(xml_string):
    """将 `xml` 转化为 `dict`.


    Parameters
    ----------
    xml_string: string

        转换的数据

    Returns
    -------
    dict
    """
    try:
        return dict((child.tag, child.text) for child in EleTree.fromstring(xml_string))
    except EleTree.ParseError:
        return {}

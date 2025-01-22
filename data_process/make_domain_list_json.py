#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/2 19:54
# @Author  : Yu.Jingkai
# @File    : make_domain_list_json.py
import json

# 读取域名
with open('../domain_list/use_this_blacklist.txt', 'r') as f:
    domains = [line.strip() for line in f]

# 创建包含 fqdn 和 value 的字典列表
domain_dicts = [{'fqdn': domain, 'value': 1} for domain in domains]

# 将字典列表写入到 JSON 文件中
with open('../domain_list/use_this_blacklist.json', 'w') as f:
    for domain_dict in domain_dicts:
        f.write(json.dumps(domain_dict) + '\n')

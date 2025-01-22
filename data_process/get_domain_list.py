#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/1/11 18:02
# @Author  : Yu.Jingkai
# @File    : get_domain_list.py

# 将给定的文件转化为exp_parrallel.py中的输入格式
import csv
import json
import os

input_file = '../domain_list/rank_result.csv'
output_file = '../domain_list/domain_list_0111.json'

domains = []

# Read the CSV file and extract the domain values
with open(input_file, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        domains.append({"fqdn": row['domain'], "value": 1})

# Write the domains to the JSON file
with open(output_file, 'w') as jsonfile:
    for domain in domains:
        json.dump(domain, jsonfile)
        jsonfile.write('\n')

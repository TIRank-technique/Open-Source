#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/3 16:05
# @Author  : Yu.Jingkai
# @File    : register_status.py

import argparse
import json
import csv
import os

# ---------- var define start ----------

# register_status_path = '../validity/register_status/whois_sld_based_fqdn_register_status.csv'
# output_parent_path = '../validity/register_status'

register_status_path = ''
output_parent_path = ''

# ---------- var define end ----------

# 读取domain_list中的每个文件，并将其中的fqdn或domain提取出来保存到一个集合domains中
def read_domain_list(domain_list):
    domains = set()
    for file in domain_list:
        file_path = os.path.join('../domain_list', file)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")
        with open(file_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                if 'fqdn' in data:
                    domains.add(data['fqdn'])
                elif 'domain' in data:
                    domains.add(data['domain'])
    return domains

# 从register_status_path中读取数据，并将domains中的每个元素与该文件中的fqdn进行匹配，如果匹配到了则保存到字典domain_register_status中
def read_register_status(domains):
    domain_register_status = {}
    with open(register_status_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['fqdn'] in domains:
                domain_register_status[row['fqdn']] = (row['hold'], row['pending'], row['deleted'])
    return domain_register_status

# 将domain_register_status输出到../validity/register_status/{$timestamp}_{register_status}.csv中
def write_register_status(domain_register_status, timestamp, prefix):
    with open(f'{output_parent_path}/{timestamp}_{prefix}register_status.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['domain', 'hold', 'pending', 'deleted'])
        for domain, status in domain_register_status.items():
            writer.writerow([domain] + list(status))

def main():
    global register_status_path
    global output_parent_path
    parser = argparse.ArgumentParser()
    parser.add_argument('--domain_list', nargs='+', required=True, help='List of domain list files')
    parser.add_argument('--timestamp', required=True, help='Timestamp string')
    parser.add_argument('--prefix', required=False, default='')

    args = parser.parse_args()
    # 读取前缀
    prefix = args.prefix
    if prefix == "null":
        prefix = ""
    # 读取domain_list
    domains = read_domain_list(args.domain_list)

    register_status_path = f'../validity/register_status/{prefix}whois_sld_based_fqdn_register_status.csv'
    output_parent_path = f'../validity/register_status'

    # 读取注册状态
    domain_register_status = read_register_status(domains)
    # 写入注册状态
    write_register_status(domain_register_status, args.timestamp, prefix)

if __name__ == '__main__':
    main()

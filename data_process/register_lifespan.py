#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/3 21:05
# @Author  : Yu.Jingkai
# @File    : register_lifespan.py


import argparse
import json
import csv
import os

# ---------- var define start ----------

# register_lifespan_path = '../activity/register_lifespan/whois_sld_register_lifespan.csv'
# output_parent_path = '../activity/register_lifespan'

register_lifespan_path = ''
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

# 从 register_lifespan_path 中读取数据，并将domains中的每个元素与该文件中的fqdn进行匹配，如果匹配到了则保存到字典domain_register_lifespan中
def read_register_lifespan(domains):
    domain_register_lifespan = {}
    with open(register_lifespan_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['domain'] in domains:
                domain_register_lifespan[row['domain']] = row['register_lifespan']
    return domain_register_lifespan

# 将domain_register_lifespan输出到../activity/register_lifespan/{$timestamp}_register_lifespan.csv中
def write_register_lifespan(domain_register_lifespan, timestamp, prefix):
    with open(f'{output_parent_path}/{timestamp}_{prefix}register_lifespan.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['domain', 'register_lifespan'])
        for domain, lifespan in domain_register_lifespan.items():
            writer.writerow([domain] + [lifespan])

def main():
    global register_lifespan_path
    global output_parent_path
    parser = argparse.ArgumentParser()
    parser.add_argument('--domain_list', nargs='+', required=True, help='List of domain list files')
    parser.add_argument('--timestamp', required=True, help='Timestamp string')
    parser.add_argument('--prefix', required=False, help='Prefix of the input and output file')
    args = parser.parse_args()

    prefix = args.prefix
    if prefix == "null":
        prefix = ""

    # 读取domain_list
    domains = read_domain_list(args.domain_list)

    register_lifespan_path = f'../activity/register_lifespan/{prefix}whois_sld_register_lifespan.csv'
    output_parent_path = f'../activity/register_lifespan'

    # 读取 register_lifespan
    domain_register_lifespan = read_register_lifespan(domains)
    # 写入 register_lifespan
    write_register_lifespan(domain_register_lifespan, args.timestamp, prefix)

if __name__ == '__main__':
    main()

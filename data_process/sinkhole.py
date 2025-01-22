#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/3 20:00
# @Author  : Yu.Jingkai
# @File    : sinkhole.py


import argparse
import json
import csv
import os

# ---------- var define start ----------

# sinkhole_path = '../validity/sinkhole/validity_sinkhole_analyze.csv'
# output_parent_path = '../validity/sinkhole'

sinkhole_path = ''
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

# 从 parking_path 中读取数据，并将domains中的每个元素与该文件中的fqdn进行匹配，如果匹配到了则保存到字典domain_parking中
def read_parking(domains):
    domain_parking = {}
    with open(sinkhole_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['FQDN'] in domains:
                domain_parking[row['FQDN']] = row['Sinkholed']
    return domain_parking

# 将domain_parking输出到../validity/sinkhole/{$timestamp}_sinkhole.csv中
def write_parking(domain_parking, timestamp, prefix):
    with open(f'{output_parent_path}/{timestamp}_{prefix}sinkhole.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['domain', 'sinkholed'])
        for domain, status in domain_parking.items():
            writer.writerow([domain] + [status])

def main():
    global sinkhole_path
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

    sinkhole_path = f'../validity/sinkhole/{prefix}validity_sinkhole_analyze.csv'
    output_parent_path = '../validity/sinkhole'

    # 读取parking
    domain_parking = read_parking(domains)
    # 写入parking
    write_parking(domain_parking, args.timestamp, prefix)

if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/3 20:17
# @Author  : Yu.Jingkai
# @File    : freq.py

import argparse
import json
import csv
import os

# ---------- var define start ----------

freq_path = '../validity/freq/all_maldomains_merged_with_blacklists.json'
output_parent_path = '../validity/freq'

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

# 从freq_path中读取数据，
def read_freq_data():
    all_domain_freq = {}
    with open(freq_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            all_domain_freq[data['domain']] = data['in_TI']

    return all_domain_freq

def calculate_freq(domains):
    all_domain_freq = read_freq_data()
    domain_freq = {}

    for domain in domains:
        if domain not in all_domain_freq or len(all_domain_freq[domain]) == 0:
            domain_freq[domain] = 1
        else:
            domain_freq[domain] = len(all_domain_freq[domain])

    return domain_freq


# 将domain_freq输出到../validity/freq/{$timestamp}_freq.csv中
def write_freq(domain_freq, timestamp):
    with open(f'{output_parent_path}/{timestamp}_freq.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['domain', 'freq'])
        for domain, freq in domain_freq.items():
            writer.writerow([domain] + [freq])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--domain_list', nargs='+', required=True, help='List of domain list files')
    parser.add_argument('--timestamp', required=True, help='Timestamp string')
    args = parser.parse_args()

    # 读取domain_list
    domains = read_domain_list(args.domain_list)
    # 计算freq
    domain_freq = calculate_freq(domains)
    # 写入freq
    write_freq(domain_freq, args.timestamp)

if __name__ == '__main__':
    main()

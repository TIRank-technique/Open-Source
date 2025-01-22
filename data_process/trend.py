#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/3 21:43
# @Author  : Yu.Jingkai
# @File    : trend.py

import argparse
import json
import csv
import os
import numpy as np
from sklearn.linear_model import LinearRegression
import glob
import pandas as pd

# ---------- var define start ----------

activation_parent_path = '../origin_data/activation'
output_parent_path = '../activity/trend'
# 原始 csv 文件名格式
activation_pattern = f'activation_*.csv'
# 新增黑名单&真实事件 csv 文件名格式
increase_black_pr_activation_pattern = f'increase_black_pr_activation_*.csv'


# activation_parent_path = '../origin_data/activation'
# output_parent_path = '../activity/trend'
# # 原始 csv 文件名格式
# activation_pattern = f'activation_*.csv'
# # 新增黑名单&真实事件 csv 文件名格式
# increase_black_pr_activation_pattern = f'increase_black_pr_activation_*.csv'



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



# 线性回归拟合
def linear_regression_fit(x, y):
    # print("开始进行线性回归拟合...")
    x = np.array(x).reshape((-1, 1))
    model = LinearRegression().fit(x, y)
    return model.coef_[0]

def read_activation_files(domains, sub_pattern, start_date, end_date):
    # activation_files = glob.glob(f'{activation_parent_path}/activation_*.csv')
    activation_files = glob.glob(f'{activation_parent_path}/{sub_pattern}')
    activation_data = {}
    for file in activation_files:
        date = int(file.split('_')[-1].split('.')[0])
        if start_date <= date <= end_date:
            df = pd.read_csv(file)
            for index, row in df.iterrows():
                domain = row['fqdn']
                activation = row['activation']
                # 如果domain不在domains中，不关注，跳过
                if domain not in domains:
                    continue
                if domain not in activation_data:
                    activation_data[domain] = [0]*(end_date-start_date+1)
                activation_data[domain][date-start_date] = activation
    return activation_data

def main():
    global activation_parent_path
    global output_parent_path
    global activation_parent_path
    global increase_black_pr_activation_pattern
    parser = argparse.ArgumentParser()
    parser.add_argument('--domain_list', nargs='+', required=True, help='List of domain list files')
    parser.add_argument('--timestamp', required=True, help='Timestamp string')
    parser.add_argument('--start_date', required=True, help='Start date')
    parser.add_argument('--end_date', required=True, help='End date')
    parser.add_argument('--prefix', required=False, help='Prefix of the input and output file')
    args = parser.parse_args()

    start_date = int(args.start_date)
    end_date = int(args.end_date)

    prefix = args.prefix
    if prefix == "null":
        prefix = ""

    activation_parent_path = '../origin_data/activation'
    output_parent_path = '../activity/trend'
    # 原始 csv 文件名格式
    activation_pattern = f'{prefix}activation_*.csv'
    # 新增黑名单&真实事件 csv 文件名格式
    increase_black_pr_activation_pattern = f'increase_black_pr_activation_*.csv'

    # 读取domain_list
    domains = read_domain_list(args.domain_list)
    # 读取 activation 数据
    activation_data = read_activation_files(domains, activation_pattern, start_date, end_date)
    # 读取新增黑名单&真实事件 activation 数据
    increase_black_pr_activation_data = read_activation_files(domains, increase_black_pr_activation_pattern, start_date, end_date)
    activation_data.update(increase_black_pr_activation_data)
    # 计算斜率并保存结果
    results = []
    for domain in domains:
        if domain in activation_data:
            k = linear_regression_fit(list(range(start_date, end_date+1)), activation_data[domain])
            results.append((domain, k))
        else :
            results.append((domain, 0))
    with open(f'{output_parent_path}/{args.timestamp}_{prefix}trend.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['domain', 'k'])
        writer.writerows(results)

if __name__ == '__main__':
    main()

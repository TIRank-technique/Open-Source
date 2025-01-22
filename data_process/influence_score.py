#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/7 20:31
# @Author  : Yu.Jingkai
# @File    : influence_score.py



import argparse
import json
import csv
import os
import numpy as np
from sklearn.linear_model import LinearRegression
import glob
import pandas as pd
from datetime import datetime, timedelta

# ---------- var define start ----------

activation_parent_path = '../origin_data/activation'
output_parent_path = '../activity/influence_score'
output_value_label = 'influence_score'
activation_pattern = 'activation_*.csv'
increase_black_pr_activation_pattern = 'increase_black_pr_activation_*.csv'

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
    print("开始进行线性回归拟合...")
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

def calculate_score(data_dict, G):
    influence_score_dict = {}
    for domain, y_data in data_dict.items():
        T = len(y_data)
        P = 0
        for activation in y_data:
            P += activation
        score = P / ((T + 2) ** G)
        influence_score_dict[domain] = score
    return influence_score_dict

def write_csv_files(data, parent_path, output_value_label, timestamp, prefix):
    with open(f'{parent_path}/{timestamp}_{prefix}{output_value_label}.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['fqdn', output_value_label])
        for domain, cv in data.items():
            writer.writerow([domain] + [cv])

def main():
    global activation_parent_path
    global output_parent_path
    global output_value_label
    global activation_pattern
    global increase_black_pr_activation_pattern

    parser = argparse.ArgumentParser()
    parser.add_argument('--domain_list', nargs='+', required=True, help='List of domain list files')
    parser.add_argument('--timestamp', required=True, help='Timestamp string')
    parser.add_argument('--start_date', required=True, help='Start date')
    parser.add_argument('--end_date', required=True, help='End date')
    parser.add_argument('--G', required=True, help='G')
    parser.add_argument('--prefix', required=False, help='Prefix of the input and output file')
    args = parser.parse_args()

    prefix = args.prefix
    if prefix == "null":
        prefix = ""

    activation_parent_path = '../origin_data/activation'
    output_parent_path = '../activity/influence_score'
    output_value_label = 'influence_score'
    activation_pattern = f'{prefix}activation_*.csv'
    increase_black_pr_activation_pattern = 'increase_black_pr_activation_*.csv'

    start_date = int(args.start_date)
    end_date = int(args.end_date)
    domain_list = args.domain_list
    G = float(args.G)
    timestamp = args.timestamp


    # 读取domain_list
    domains = read_domain_list(domain_list)
    # 读取 activation 数据
    activation_data = read_activation_files(domains, activation_pattern, start_date, end_date)
    # 新增黑名单和威胁情报
    increase_black_pr_activation_data = read_activation_files(domains, increase_black_pr_activation_pattern, start_date, end_date)
    # 将两者合并到一起
    activation_data.update(increase_black_pr_activation_data)
    # 计算影响力分数
    influence_score = calculate_score(activation_data, G)
    write_csv_files(influence_score, output_parent_path, output_value_label, timestamp, prefix)

if __name__ == '__main__':
    main()

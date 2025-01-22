#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/6 10:47
# @Author  : Yu.Jingkai
# @File    : cv.py

import argparse
import json
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.linear_model import LinearRegression
import os
import glob
import csv

# ---------- var define start ----------

# 原始 csv 文件父目录
activation_parent_path = '../origin_data/activation'
client_cnt_parent_path = '../origin_data/client_cnt'
request_cnt_sum_parent_path = '../origin_data/request_cnt_sum'
# 原始 csv 文件名格式
activation_pattern = f'activation_*.csv'
request_cnt_sum_pattern = f'request_cnt_sum_*.csv'
client_cnt_pattern = f'client_cnt_*.csv'
# 新增黑名单&真实事件 csv 文件名格式
increase_black_pr_client_cnt_pattern = f'increase_black_pr_client_cnt_*.csv'
increase_black_pr_request_cnt_sum_pattern = f'increase_black_pr_request_cnt_sum_*.csv'
increase_black_pr_activation_pattern = f'increase_black_pr_activation_*.csv'

# key
key = 'fqdn'
# values
client_cnt_value = 'client_cnt'
request_cnt_sum_value = 'request_cnt_sum'
activation_value = 'activation'
# output value label
client_cnt_label = 'client_cnt_coefficient_of_variation'
request_cnt_sum_label = 'request_cnt_sum_coefficient_of_variation'
activation_label = 'activation_coefficient_of_variation'

client_cnt_coefficient_of_variation_parent_path = '../activity/client_cnt_coefficient_of_variation'
request_cnt_sum_coefficient_of_variation_parent_path = '../activity/request_cnt_sum_coefficient_of_variation'
activation_coefficient_of_variation_parent_path = '../activity/activation_coefficient_of_variation'


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

# 读取 client_cnt, request_cnt_sum, activation 的 csv 文件
def read_csv_files(parent_path, sub_pattern, domains, csv_key, csv_value_name, start_date, end_date):
    full_pattern = f'{parent_path}/{sub_pattern}'
    # print(full_pattern)
    # files = glob.glob(f'{parent_path}/{sub_pattern}')
    files = glob.glob(full_pattern)
    data = {}
    for file in files:
        date = int(file.split('_')[-1].split('.')[0])
        if start_date <= date <= end_date:
            df = pd.read_csv(file)
            for index, row in df.iterrows():
                domain = row[csv_key]
                csv_value = row[csv_value_name]
                if domain not in domains:
                    continue
                if domain not in data:
                    data[domain] = [0]*(end_date-start_date+1)
                data[domain][date-start_date] = csv_value
    return data

# 变异系数
# def fluctuation_quantification(y_data):
#     std_dev = np.std(y_data)  # 标准差
#     coefficient_of_variation = np.std(y_data) / np.mean(y_data)  # 变异系数
#     return std_dev, coefficient_of_variation

def fluctuation_quantification(data_dict):
    cv_dict = {}
    for domain, y_data in data_dict.items():
        std_dev = np.std(y_data)  # 标准差
        coefficient_of_variation = np.std(y_data) / np.mean(y_data)  # 变异系数
        cv_dict[domain] = coefficient_of_variation
    return cv_dict

def write_csv_files(data, parent_path, output_value_label, timestamp, prefix):
    with open(f'{parent_path}/{timestamp}_{prefix}{output_value_label}.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['fqdn', output_value_label])
        for domain, cv in data.items():
            writer.writerow([domain] + [cv])

def main():
    global activation_parent_path, client_cnt_parent_path, request_cnt_sum_parent_path
    global activation_pattern, request_cnt_sum_pattern, client_cnt_pattern
    global increase_black_pr_activation_pattern, increase_black_pr_request_cnt_sum_pattern, increase_black_pr_client_cnt_pattern
    global key, client_cnt_value, request_cnt_sum_value, activation_value
    global client_cnt_label, request_cnt_sum_label, activation_label
    global client_cnt_coefficient_of_variation_parent_path, request_cnt_sum_coefficient_of_variation_parent_path, activation_coefficient_of_variation_parent_path
    parser = argparse.ArgumentParser()
    parser.add_argument('--domain_list', nargs='+', required=True, help='List of domain list files')
    parser.add_argument('--start_date', required=True)
    parser.add_argument('--end_date', required=True)
    parser.add_argument('--timestamp', required=True)
    parser.add_argument('--prefix', required=False, help='Prefix of the input and output file')

    args = parser.parse_args()

    prefix = args.prefix
    if prefix == "null":
        prefix = ""

    # 原始 csv 文件父目录
    activation_parent_path = '../origin_data/activation'
    client_cnt_parent_path = '../origin_data/client_cnt'
    request_cnt_sum_parent_path = '../origin_data/request_cnt_sum'
    # 原始 csv 文件名格式
    activation_pattern = f'{prefix}activation_*.csv'
    request_cnt_sum_pattern = f'{prefix}request_cnt_sum_*.csv'
    client_cnt_pattern = f'{prefix}client_cnt_*.csv'
    # 新增黑名单&真实事件 csv 文件名格式
    increase_black_pr_client_cnt_pattern = f'increase_black_pr_client_cnt_*.csv'
    increase_black_pr_request_cnt_sum_pattern = f'increase_black_pr_request_cnt_sum_*.csv'
    increase_black_pr_activation_pattern = f'increase_black_pr_activation_*.csv'

    # key
    key = 'fqdn'
    # values
    client_cnt_value = 'client_cnt'
    request_cnt_sum_value = 'request_cnt_sum'
    activation_value = 'activation'
    # output value label
    client_cnt_label = 'client_cnt_coefficient_of_variation'
    request_cnt_sum_label = 'request_cnt_sum_coefficient_of_variation'
    activation_label = 'activation_coefficient_of_variation'

    client_cnt_coefficient_of_variation_parent_path = '../activity/client_cnt_coefficient_of_variation'
    request_cnt_sum_coefficient_of_variation_parent_path = '../activity/request_cnt_sum_coefficient_of_variation'
    activation_coefficient_of_variation_parent_path = '../activity/activation_coefficient_of_variation'

    start_date = int(args.start_date)
    end_date = int(args.end_date)
    timestamp = args.timestamp
    domain_list = args.domain_list

    domains = read_domain_list(domain_list)
    # 890w 威胁情报
    client_cnt_data = read_csv_files(client_cnt_parent_path, client_cnt_pattern, domains, key, client_cnt_value, start_date, end_date)
    request_cnt_sum_data = read_csv_files(request_cnt_sum_parent_path, request_cnt_sum_pattern, domains, key, request_cnt_sum_value, start_date, end_date)
    activation_data = read_csv_files(activation_parent_path, activation_pattern, domains, key, activation_value, start_date, end_date)
    # 新增黑名单和威胁情报
    increase_black_pr_client_cnt_data = read_csv_files(client_cnt_parent_path, increase_black_pr_client_cnt_pattern, domains, key, client_cnt_value, start_date, end_date)
    increase_black_pr_request_cnt_sum_data = read_csv_files(request_cnt_sum_parent_path, increase_black_pr_request_cnt_sum_pattern, domains, key, request_cnt_sum_value, start_date, end_date)
    increase_black_pr_activation_data = read_csv_files(activation_parent_path, increase_black_pr_activation_pattern, domains, key, activation_value, start_date, end_date)

    # 将两者合并到一起
    client_cnt_data.update(increase_black_pr_client_cnt_data)
    request_cnt_sum_data.update(increase_black_pr_request_cnt_sum_data)
    activation_data.update(increase_black_pr_activation_data)

    # 计算变异系数
    client_cnt_cv = fluctuation_quantification(client_cnt_data)
    request_cnt_sum_cv = fluctuation_quantification(request_cnt_sum_data)
    activation_cv = fluctuation_quantification(activation_data)

    # 写入文件
    write_csv_files(client_cnt_cv, client_cnt_coefficient_of_variation_parent_path, client_cnt_label, timestamp, prefix)
    write_csv_files(request_cnt_sum_cv, request_cnt_sum_coefficient_of_variation_parent_path, request_cnt_sum_label, timestamp, prefix)
    write_csv_files(activation_cv, activation_coefficient_of_variation_parent_path, activation_label, timestamp, prefix)

    # print("Coefficient of Variation for client_cnt: ", client_cnt_cv)
    # print("Coefficient of Variation for request_cnt_sum: ", request_cnt_sum_cv)
    # print("Coefficient of Variation for activation: ", activation_cv)

if __name__ == "__main__":
    main()

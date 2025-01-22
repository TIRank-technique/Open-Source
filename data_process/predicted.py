#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/4 16:18
# @Author  : Yu.Jingkai
# @File    : predicted.py


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
client_cnt_parent_path = '../origin_data/client_cnt'
request_cnt_sum_parent_path = '../origin_data/request_cnt_sum'

predicted_client_cnt_parent_path = '../activity/predicted_client_cnt'
predicted_request_cnt_sum_parent_path = '../activity/predicted_request_cnt_sum'
predicted_activation_parent_path = '../activity/predicted_activation'

# 原始 csv 文件名格式
activation_pattern = f'activation_*.csv'
request_cnt_sum_pattern = f'request_cnt_sum_*.csv'
client_cnt_pattern = f'client_cnt_*.csv'
# 新增黑名单&真实事件 csv 文件名格式
increase_black_pr_client_cnt_pattern = f'increase_black_pr_client_cnt_*.csv'
increase_black_pr_request_cnt_sum_pattern = f'increase_black_pr_request_cnt_sum_*.csv'
increase_black_pr_activation_pattern = f'increase_black_pr_activation_*.csv'

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

def read_client_cnt_files(domains, sub_pattern, start_date, end_date):
    # client_cnt_files = glob.glob(f'{client_cnt_parent_path}/client_cnt_*.csv')
    client_cnt_files = glob.glob(f'{client_cnt_parent_path}/{sub_pattern}')
    client_cnt_data = {}
    for file in client_cnt_files:
        date = int(file.split('_')[-1].split('.')[0])
        if start_date <= date <= end_date:
            df = pd.read_csv(file)
            for index, row in df.iterrows():
                domain = row['fqdn']
                client_cnt = row['client_cnt']
                if domain not in domains:
                    continue
                if domain not in client_cnt_data:
                    client_cnt_data[domain] = [0]*(end_date-start_date+1)
                client_cnt_data[domain][date-start_date] = client_cnt
    return client_cnt_data

def read_request_cnt_sum_files(domains, sub_pattern, start_date, end_date):
    # request_cnt_sum_files = glob.glob(f'{request_cnt_sum_parent_path}/request_cnt_sum_*.csv')
    request_cnt_sum_files = glob.glob(f'{request_cnt_sum_parent_path}/{sub_pattern}')
    request_cnt_sum_data = {}
    for file in request_cnt_sum_files:
        date = int(file.split('_')[-1].split('.')[0])
        if start_date <= date <= end_date:
            df = pd.read_csv(file)
            for index, row in df.iterrows():
                domain = row['fqdn']
                cnt = row['request_cnt_sum']
                if domain not in domains:
                    continue
                if domain not in request_cnt_sum_data:
                    request_cnt_sum_data[domain] = [0]*(end_date-start_date+1)
                request_cnt_sum_data[domain][date-start_date] = cnt
    return request_cnt_sum_data

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
                if domain not in domains:
                    continue
                if domain not in activation_data:
                    activation_data[domain] = [0]*(end_date-start_date+1)
                activation_data[domain][date-start_date] = activation
    return activation_data

def predict_next_data(origin_data, alpha):
    predicted_data = {}
    for domain, datas in origin_data.items():
        s = pd.Series(datas)
        ema = s.ewm(alpha=alpha, adjust=False).mean()
        # 使用 shift 方法将 EMA 序列向后移动一位
        ema_shifted = ema.shift(1)
        # 使用 fillna 方法填充第一个 NaN 值
        ema_shifted = ema_shifted.fillna(datas[0])
        # 计算预测值
        predicted = (ema_shifted * (1 - alpha)) + (s * alpha)
        predicted_data[domain] = predicted.tolist()
        # print(predicted_data[domain])
    return predicted_data

def main():
    global activation_parent_path, client_cnt_parent_path, request_cnt_sum_parent_path
    global predicted_client_cnt_parent_path, predicted_request_cnt_sum_parent_path, predicted_activation_parent_path
    global activation_pattern, request_cnt_sum_pattern, client_cnt_pattern
    global increase_black_pr_client_cnt_pattern, increase_black_pr_request_cnt_sum_pattern, increase_black_pr_activation_pattern
    parser = argparse.ArgumentParser()
    parser.add_argument('--domain_list', nargs='+', required=True, help='List of domain list files')
    parser.add_argument('--start_date', required=True)
    parser.add_argument('--end_date', required=True)
    parser.add_argument('--timestamp', required=True)
    parser.add_argument('--alpha', required=True)
    parser.add_argument('--prefix', required=False, help='Prefix of the input and output file')

    args = parser.parse_args()

    prefix = args.prefix
    if prefix == "null":
        prefix = ""

    activation_parent_path = '../origin_data/activation'
    client_cnt_parent_path = '../origin_data/client_cnt'
    request_cnt_sum_parent_path = '../origin_data/request_cnt_sum'

    predicted_client_cnt_parent_path = '../activity/predicted_client_cnt'
    predicted_request_cnt_sum_parent_path = '../activity/predicted_request_cnt_sum'
    predicted_activation_parent_path = '../activity/predicted_activation'

    # 原始 csv 文件名格式
    activation_pattern = f'{prefix}activation_*.csv'
    request_cnt_sum_pattern = f'{prefix}request_cnt_sum_*.csv'
    client_cnt_pattern = f'{prefix}client_cnt_*.csv'
    # 新增黑名单&真实事件 csv 文件名格式
    increase_black_pr_client_cnt_pattern = f'increase_black_pr_client_cnt_*.csv'
    increase_black_pr_request_cnt_sum_pattern = f'increase_black_pr_request_cnt_sum_*.csv'
    increase_black_pr_activation_pattern = f'increase_black_pr_activation_*.csv'


    start_date = int(args.start_date)
    end_date = int(args.end_date)
    alpha = float(args.alpha)
    timestamp = args.timestamp
    domain_list = args.domain_list
    domains = read_domain_list(domain_list)

    print("start reading client_cnt files")
    client_cnt_data = read_client_cnt_files(domains, client_cnt_pattern, start_date, end_date)
    increase_black_pr_client_cnt_data = read_client_cnt_files(domains, increase_black_pr_client_cnt_pattern, start_date, end_date)
    client_cnt_data.update(increase_black_pr_client_cnt_data)
    print("start reading request_cnt_sum files")
    request_cnt_sum_data = read_request_cnt_sum_files(domains, request_cnt_sum_pattern, start_date, end_date)
    increase_black_pr_request_cnt_sum_data = read_request_cnt_sum_files(domains, increase_black_pr_request_cnt_sum_pattern, start_date, end_date)
    request_cnt_sum_data.update(increase_black_pr_request_cnt_sum_data)
    print("start reading activation files")
    activation_data = read_activation_files(domains, activation_pattern, start_date, end_date)
    increase_black_pr_activation_data = read_activation_files(domains, increase_black_pr_activation_pattern, start_date, end_date)
    activation_data.update(increase_black_pr_activation_data)

    print("start predicting client_cnt")
    predicted_client_cnt = predict_next_data(client_cnt_data, alpha)
    print("start predicting request_cnt_sum")
    predicted_request_cnt_sum = predict_next_data(request_cnt_sum_data, alpha)
    print("start predicting activation")
    predicted_activation = predict_next_data(activation_data, alpha)

    with open(f'{predicted_client_cnt_parent_path}/{timestamp}_{prefix}predicted_client_cnt.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['fqdn'] + list(range(start_date, end_date+1)))
        for domain, datas in predicted_client_cnt.items():
            writer.writerow([domain] + datas)

    with open(f'{predicted_request_cnt_sum_parent_path}/{timestamp}_{prefix}predicted_request_cnt_sum.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['fqdn'] + list(range(start_date, end_date+1)))
        for domain, datas in predicted_request_cnt_sum.items():
            writer.writerow([domain] + datas)

    with open(f'{predicted_activation_parent_path}/{timestamp}_{prefix}predicted_activation.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['fqdn'] + list(range(start_date, end_date+1)))
        for domain, datas in predicted_activation.items():
            writer.writerow([domain] + datas)

if __name__ == "__main__":
    main()

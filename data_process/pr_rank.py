#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/22 10:58
# @Author  : Yu.Jingkai
# @File    : pr_rank.py

import pandas as pd
import json
import matplotlib.pyplot as plt
import os
import numpy as np
from datetime import datetime
import pytz

# Set the file paths
domain_file = '../domain_list/all_PR_domains.txt'
matrix_results_path = '../matrix_results/0107-0331_new'
# matrix_results_path = '../matrix_results/0107-0331'
pr_rank_sub_path = 'pr_rank'

date_map_file = f'{matrix_results_path}/date_map.json'
# suffix = 'rank_25'
suffix = 'rank_result'

# Read the domain file
with open(domain_file, 'r') as f:
    domains = f.read().splitlines()

# Read the date map file
date_map = {}
with open(date_map_file, 'r') as f:
    for line in f:
        date_map.update(json.loads(line))

# Initialize the date range
start_date = min(date_map.keys())
end_date = max(date_map.keys())

# Define the output CSV file path
domain_rank_parent_path = f'{matrix_results_path}/{pr_rank_sub_path}'
output_csv_file_path = f'{domain_rank_parent_path}/{suffix}_{start_date}_{end_date}.csv'

# Initialize a dictionary to store ranks of all domains
all_ranks = {domain: {} for domain in domains}

# For each date
for date, timestamp in date_map.items():
    # Set the file path
    utc_now = datetime.now(pytz.timezone('UTC'))

    # Convert UTC time to Beijing time
    beijing_now = utc_now.astimezone(pytz.timezone('Asia/Shanghai'))

    file_path = f'{matrix_results_path}/{timestamp}_{suffix}.csv'
    print(f"[{beijing_now}]Processing file: {file_path}")

    # Check if the file exists
    if os.path.exists(file_path):
        # Read the file
        df = pd.read_csv(file_path)

        # For each domain
        for domain in domains:
            # Get the rank of the domain
            if domain in df['domain'].values:
                rank = df[df['domain'] == domain].index[0] + 1
            else:
                rank = np.nan

            # Append the rank to the dictionary
            all_ranks[domain][date] = rank
    else:
        print(f"File {file_path} not found.")
        for domain in domains:
            all_ranks[domain][date] = np.nan

# For each domain
for domain, ranks in all_ranks.items():
    print(f"Processing domain: {domain}")

    # Define the output file path
    output_img_file_path = f'{domain_rank_parent_path}/{domain}_{suffix}_{start_date}_{end_date}.png'

    print(f"Printing the ranks of {domain} over time...")

    # Plot the ranks
    plt.figure(figsize=(10, 6))
    plt.plot(list(ranks.keys()), list(ranks.values()))
    plt.xlabel('Date')
    plt.ylabel('Rank')
    plt.title(f'Rank of {domain} over time')
    plt.savefig(output_img_file_path)

    # Save the ranks to the CSV file
    df_ranks = pd.DataFrame(ranks, index=[domain])
    if os.path.exists(output_csv_file_path):
        df_ranks.to_csv(output_csv_file_path, mode='a', header=False)
    else:
        df_ranks.to_csv(output_csv_file_path)
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/6 21:56
# @Author  : Yu.Jingkai
# @File    : pr_rank_sel.py
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import os
import numpy as np
import matplotlib.ticker as ticker

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


# Set the file paths
# input_csv_file_path = '../matrix_results/0107-0331/pr_rank/rank_25_20240107_20240331.csv'
input_csv_file_path = '../matrix_results/0107-0331_new/pr_rank/rank_result_20240107_20240331.csv'
# output_folder_path = '../matrix_results/0107-0331/pr_rank/sel/'
output_folder_path = '../matrix_results/0107-0331_new/pr_rank/sel/'

# Ensure the output directory exists
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

# Read the CSV file
df = pd.read_csv(input_csv_file_path)

# Set the domains you are interested in
domains = ['1-31.qq-weixin.org', '6j312.rchan0.com', 'data-dev.helpkaspersky.top']  # Replace with actual domain names

# Convert column names to datetime objects for easier handling
df.columns = pd.to_datetime(df.columns, format='%Y%m%d', errors='ignore')

# For each domain, plot the rank over time
for domain in domains:
    if domain in df['domain'].values:
        # Filter the data for the current domain
        domain_data = df[df['domain'] == domain].iloc[0].drop('domain')

        # Ensure the index is datetime
        domain_data.index = pd.to_datetime(domain_data.index, format='%Y%m%d', errors='coerce')

        # Check for missing ranks and print the dates
        missing_dates = domain_data[domain_data.isna()].index
        if not missing_dates.empty:
            print(f"Missing ranks for domain {domain} on dates: {missing_dates.strftime('%Y-%m-%d').tolist()}")

        # Plot
        plt.figure(figsize=(10, 6))
        plt.plot(domain_data.index, domain_data.values, marker='')

        # Set the x-ticks to be evenly spaced across the date range
        xticks = np.linspace(domain_data.index.min().value, domain_data.index.max().value, 6)
        xticks = pd.to_datetime(xticks)  # Convert back to datetime

        plt.xticks(xticks, xticks.strftime('%m-%d'), fontsize=20)

        # Add vertical lines for x-ticks
        for xtick in xticks:
            plt.axvline(x=xtick, color='gray', linestyle='--', linewidth=0.5, dashes=(5, 10))

        # Add horizontal lines for y-ticks
        yticks = plt.yticks()[0]
        plt.yticks(yticks, fontsize=20)  # Adjust fontsize for y-axis ticks
        for ytick in yticks:
            plt.axhline(y=ytick, color='gray', linestyle='--', linewidth=0.5, dashes=(5, 10))

        # Set the y-axis to start from 0# Set y-axis formatter to use scientific notation
        plt.gca().yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
        plt.gca().yaxis.get_offset_text().set_fontsize(20)  # Adjust the offset text fontsize

        plt.ylim(bottom=0)  # Set the minimum value of y-axis to 0

        plt.xlabel('Date', fontsize=20)
        plt.ylabel('Rank', fontsize=20)
        # plt.title(f'Rank of {domain} over time')

        # Save the plot
        plt.savefig(f'{output_folder_path}{domain}_20240107_20240331.pdf')
        plt.close()

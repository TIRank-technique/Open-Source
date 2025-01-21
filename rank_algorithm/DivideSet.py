import time

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split



def split_dataset_randomly(filename, test_size=0.1):
    # 读取 Excel 文件
    df = pd.read_excel(filename)

    # 选择 ioc_value 列
    ioc_values = df['ioc_value']
    return train_test_split(ioc_values, test_size=test_size, random_state=int(time.time()))


def split_dataset_average(filename, test_size=0.1, random_state=int(time.time())):
    # 读取 Excel 文件
    df = pd.read_excel(filename)

    # 提取 ioc_value 和 category 列
    ioc_values = df['ioc_value']
    categories = df['category']

    # 获取所有唯一的 category 值
    unique_categories = categories.unique()

    # 用于存储最终的训练集和测试集的 ioc_value
    train_ioc_values = []
    test_ioc_values = []

    # 对每个 category 进行循环，分别进行训练集和测试集的划分
    for category in unique_categories:
        # 获取当前 category 下的索引
        category_indices = np.where(categories == category)[0]
        category_ioc_values = ioc_values[category_indices]

        train_ioc_values_cat, test_ioc_values_cat = train_test_split(category_ioc_values, test_size=test_size,
                                                                     random_state=random_state)

        train_ioc_values.extend(train_ioc_values_cat)
        test_ioc_values.extend(test_ioc_values_cat)

    return train_ioc_values, test_ioc_values


def custom_split_on_category(filename, category_values):
    # 读取 Excel 文件
    df = pd.read_excel(filename)

    # 将 category 等于 category_values 中任何一个的 ioc_value 作为训练集，其他作为测试集
    train_df = df[~df['category'].isin(category_values)]
    test_df = df[df['category'].isin(category_values)]

    return train_df['ioc_value'], test_df['ioc_value']

# 划分数据集
train_ioc_values, test_ioc_values = split_dataset_randomly('high_value_TI.xlsx')

# 写入训练集
with open('train_set.txt', 'w') as train_file:
    for value in train_ioc_values:
        train_file.write(str(value) + '\n')

# 写入测试集
with open('test_set.txt', 'w') as test_file:
    for value in test_ioc_values:
        test_file.write(str(value) + '\n')

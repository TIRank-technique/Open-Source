import math

import numpy as np
import pandas as pd
from scipy import stats
import argparse

parser = argparse.ArgumentParser(description="Process an input CSV file.")
parser.add_argument('input_file', type=str, help='Path to the input CSV file (feature matrix)')
args = parser.parse_args()

input_file = args.input_file

# 数据处理 -----------------------------------------------------------
# 读入表
df = pd.read_csv(input_file.split('/')[-1].split('.')[0] + "_MATRIX.csv")

# 定义 Good / Bad 集合
all_domains = set()
horrible_domains = set()
normal_domains = set()

# 定义参数
B = 20 / math.log(2)
A = 100 + B * math.log(1 / 1)


# 连续变量分箱（自动） -----------------------------------------------------------

def auto_bin(Y, X, q=10):
    """
    对连续变量进行自动分箱，并计算 WOE 和 IV 值
    Y: 响应变量，二值变量
    X: 自变量，连续变量
    q: 分箱数
    """
    badnum = Y.sum()
    goodnum = Y.count() - badnum
    
    # 等频分箱
    d1 = pd.DataFrame({"X": X, "Y": Y, "Bucket": pd.qcut(X, q, duplicates='drop')})
    d2 = d1.groupby('Bucket', as_index=True)
    d3 = pd.DataFrame(d2.X.min(), columns=['min'])
    d3['min'] = d2.min().X
    d3['max'] = d2.max().X
    d3['bad'] = d2.sum().Y
    d3['total'] = d2.count().Y
    d3['rate'] = d2.mean().Y

    # 平滑处理
    epsilon = 1e-6  # 微小值，避免除以0
    d3['woe'] = np.log(
        ((d3['bad'] + epsilon) / (badnum + epsilon)) / ((d3['total'] - d3['bad'] + epsilon) / (goodnum + epsilon)))
    d3['badattr'] = (d3['bad'] + epsilon) / (badnum + epsilon)
    d3['goodattr'] = ((d3['total'] - d3['bad']) + epsilon) / (goodnum + epsilon)
    iv = ((d3['badattr'] - d3['goodattr']) * d3['woe']).sum()
    woe = list(d3['woe'].round(3))
    
    # 获取分箱边界
    bins = [-np.inf] + sorted(d3['max'].tolist()) + [np.inf]
    
    return d3, iv, woe, bins


# 离散变量分箱（手动） -------------------------------------------------

import pandas as pd
import numpy as np


def self_bin(Y, X, cut):
    badnum = Y.sum()
    goodnum = Y.count() - badnum
    d1 = pd.DataFrame({"X": X, "Y": Y, "Bucket": pd.cut(X, cut)})
    d2 = d1.groupby('Bucket', as_index=True)
    d3 = pd.DataFrame(d2.X.min(), columns=['min'])
    d3['min'] = d2.min().X
    d3['max'] = d2.max().X
    d3['bad'] = d2.sum().Y
    d3['total'] = d2.count().Y
    d3['rate'] = d2.mean().Y

    # 平滑处理
    epsilon = 1e-6  # 微小值，避免除以0
    d3['woe'] = np.log(
        ((d3['bad'] + epsilon) / (badnum + epsilon)) / ((d3['total'] - d3['bad'] + epsilon) / (goodnum + epsilon)))

    d3['badattr'] = (d3['bad'] + epsilon) / (badnum + epsilon)
    d3['goodattr'] = ((d3['total'] - d3['bad']) + epsilon) / (goodnum + epsilon)
    iv = ((d3['badattr'] - d3['goodattr']) * d3['woe']).sum()
    woe = list(d3['woe'].round(3))
    return d3, iv, woe


# 示例用法
# d3, iv, woe = self_bin(Y, X, cut)


# 填写对应的变量在不同分箱中的 woe 值 ------------------------------
def trans_woe(var, var_name, woe, cut):
    woe_name = var_name + '_woe'
    for i in range(len(woe)):
        if i == 0:
            # 将 woe 的值按 cut 分箱的下节点，顺序赋值给 var 的 woe_name 列 ，分箱的第一段
            var.loc[(var[var_name] <= cut[i + 1]), woe_name] = woe[i]
        elif (i > 0) and (i < len(woe) - 1):
            var.loc[((var[var_name] > cut[i]) & (var[var_name] <= cut[i + 1])), woe_name] = woe[i]
        else:
            # 大于最后一个分箱区间的上限值，最后一个值是正无穷
            var.loc[(var[var_name] > cut[len(woe) - 1]), woe_name] = woe[len(woe) - 1]
    return var


# 生成评分卡 --------------------------------------------------
def generate_scorecard(model_coef, binning_df, features, B):
    lst = []
    cols = ['Variable', 'Binning', 'woe', 'coef', 'Score']
    coef = model_coef[0]  # 得分需要乘以的系数
    for i in range(len(features)):
        f = features[i]
        df = binning_df[binning_df['features'] == f]
        for index, row in df.iterrows():
            lst.append([f, row['Bucket'], row['woe'], coef[i], -coef[i] * row['woe'] * B])
    data = pd.DataFrame(lst, columns=cols)
    return data


# main -----------------------------------------------------------------

# 对各个指标进行离散/连续分箱，填写得到的 WOE 值 -->
ninf = float('-inf')
pinf = float('inf')

bool_cut = [ninf, 0.5, pinf]
hold_df, hold_iv, hold_woe = self_bin(df.IsHorrible, df.hold, bool_cut)
pending_df, pending_iv, pending_woe = self_bin(df.IsHorrible, df.pending, bool_cut)
deleted_df, deleted_iv, deleted_woe = self_bin(df.IsHorrible, df.deleted, bool_cut)
NXDOMAIN_df, NXDOMAIN_iv, NXDOMAIN_woe = self_bin(df.IsHorrible, df.NXDOMAIN, bool_cut)
parked_df, parked_iv, parked_woe = self_bin(df.IsHorrible, df.parked, bool_cut)
sinkholed_df, sinkholed_iv, sinkholed_woe = self_bin(df.IsHorrible, df.sinkholed, bool_cut)

freq_cut = [ninf, 1.5, 2.5, pinf]
freq_df, freq_iv, freq_woe = self_bin(df.IsHorrible, df.freq, freq_cut)


register_lifespan_df, register_lifespan_iv, register_lifespan_woe, register_lifespan_cut\
    = auto_bin(df.IsHorrible, df.register_lifespan, q=20)

activation_coefficient_of_variation_df, activation_coefficient_of_variation_iv, activation_coefficient_of_variation_woe, \
    activation_coefficient_of_variation_cut = auto_bin(df.IsHorrible, df.activation_coefficient_of_variation, q=20)
client_cnt_coefficient_of_variation_df, client_cnt_coefficient_of_variation_iv, client_cnt_coefficient_of_variation_woe, \
    client_cnt_coefficient_of_variation_cut = auto_bin(df.IsHorrible, df.client_cnt_coefficient_of_variation, q=20)
request_cnt_sum_coefficient_of_variation_df, request_cnt_sum_coefficient_of_variation_iv, request_cnt_sum_coefficient_of_variation_woe, \
   request_cnt_sum_coefficient_of_variation_cut = auto_bin(df.IsHorrible, df.request_cnt_sum_coefficient_of_variation, q=20)

activation_periodicity_index_df, activation_periodicity_index_iv, activation_periodicity_index_woe, \
    activation_periodicity_index_cut = auto_bin(df.IsHorrible, df.activation_periodicity_index, q=20)
client_cnt_periodicity_index_df, client_cnt_periodicity_index_iv, client_cnt_periodicity_index_woe, \
    client_cnt_periodicity_index_cut = auto_bin(df.IsHorrible, df.client_cnt_periodicity_index, q=20)
request_cnt_sum_periodicity_index_df, request_cnt_sum_periodicity_index_iv, request_cnt_sum_periodicity_index_woe, \
    request_cnt_sum_periodicity_index_cut = auto_bin(df.IsHorrible, df.request_cnt_sum_periodicity_index, q=20)

activation_abnormal_index_df, activation_abnormal_index_iv, activation_abnormal_index_woe, \
    activation_abnormal_index_cut = auto_bin(df.IsHorrible, df.activation_abnormal_index, q=20)
client_cnt_abnormal_index_df, client_cnt_abnormal_index_iv, client_cnt_abnormal_index_woe, \
    client_cnt_abnormal_index_cut = auto_bin(df.IsHorrible, df.client_cnt_abnormal_index, q=20)
request_cnt_sum_abnormal_index_df, request_cnt_sum_abnormal_index_iv, request_cnt_sum_abnormal_index_woe, \
    request_cnt_sum_abnormal_index_cut = auto_bin(df.IsHorrible, df.request_cnt_sum_abnormal_index, q=20)

influence_score_df, influence_score_iv, influence_score_woe, influence_score_cut \
    = auto_bin(df.IsHorrible, df.influence_score, q = 20)

predicted_activation_df, predicted_activation_iv, predicted_activation_woe, \
    predicted_activation_cut = auto_bin(df.IsHorrible, df.predicted_activation, q=20)

predicted_client_cnt_df, predicted_client_cnt_iv, predicted_client_cnt_woe, \
    predicted_client_cnt_cut = auto_bin(df.IsHorrible, df.predicted_client_cnt, q=20)

predicted_request_cnt_sum_df, predicted_request_cnt_sum_iv, predicted_request_cnt_sum_woe, \
    predicted_request_cnt_sum_cut = auto_bin(df.IsHorrible, df.predicted_request_cnt_sum, q=20)

predicted_company_score_rdata_df, predicted_company_score_rdata_iv, predicted_company_score_rdata_woe, \
    predicted_company_score_rdata_cut = auto_bin(df.IsHorrible, df.predicted_company_score_rdata, q=20)

print("hold_iv," + str(hold_iv))
print("pending_iv," + str(pending_iv))
print("deleted_iv," + str(deleted_iv))
print("NXDOMAIN_iv," + str(NXDOMAIN_iv))
print("parked_iv," + str(parked_iv))
print("sinkholed_iv," + str(sinkholed_iv))
print("freq_iv," + str(freq_iv))
print("register_lifespan_iv," + str(register_lifespan_iv))
print("activation_coefficient_of_variation_iv," + str(activation_coefficient_of_variation_iv))
print("client_cnt_coefficient_of_variation_iv," + str(client_cnt_coefficient_of_variation_iv))
print("request_cnt_sum_coefficient_of_variation_iv," + str(request_cnt_sum_coefficient_of_variation_iv))
print("activation_abnormal_index_iv," + str(activation_abnormal_index_iv))
print("client_cnt_abnormal_index_iv," + str(client_cnt_abnormal_index_iv))
print("request_cnt_sum_abnormal_index_iv," + str(request_cnt_sum_periodicity_index_iv))
print("activation_periodicity_index_iv," + str(activation_periodicity_index_iv))
print("client_cnt_periodicity_index_iv," + str(client_cnt_periodicity_index_iv))
print("request_cnt_sum_periodicity_index_iv," + str(request_cnt_sum_periodicity_index_iv))
print("influence_score_iv," + str(influence_score_iv))
print("predicted_activation_iv," + str(predicted_activation_iv))
print("predicted_client_cnt_iv," + str(predicted_client_cnt_iv))
print("predicted_request_cnt_sum_iv," + str(predicted_request_cnt_sum_iv))
print("predicted_company_score_rdata_iv," + str(predicted_company_score_rdata_iv))

# secrank_rank_cut = [ninf, 0, 100, 1000, 10000, 100000, 500000, pinf]
# secrank_rank_df, secrank_rank_iv, secrank_rank_woe \
#     = self_bin(df.IsHorrible, df.secrank_rank, secrank_rank_cut)
#
# tranco_rank_cut = [ninf, 0, 100, 1000, 10000, 25000, 100000, 500000, 1000000, 2500000, 5000000, pinf]
# tranco_rank_df, tranco_rank_iv, tranco_rank_woe \
#     = self_bin(df.IsHorrible, df.tranco_rank, tranco_rank_cut)

# todo 插入更多指标的分箱

df = trans_woe(df, "hold", hold_woe, bool_cut)
df = trans_woe(df, "pending", pending_woe, bool_cut)
df = trans_woe(df, "deleted", deleted_woe, bool_cut)
df = trans_woe(df, "NXDOMAIN", NXDOMAIN_woe, bool_cut)
df = trans_woe(df, "parked", parked_woe, bool_cut)
df = trans_woe(df, "sinkholed", sinkholed_woe, bool_cut)
df = trans_woe(df, "register_lifespan", register_lifespan_woe, register_lifespan_cut)
df = trans_woe(df, "freq", freq_woe, freq_cut)
df = trans_woe(df, "activation_coefficient_of_variation", activation_coefficient_of_variation_woe,
               activation_coefficient_of_variation_cut)
df = trans_woe(df, "client_cnt_coefficient_of_variation", client_cnt_coefficient_of_variation_woe,
               client_cnt_coefficient_of_variation_cut)
df = trans_woe(df, "request_cnt_sum_coefficient_of_variation", request_cnt_sum_coefficient_of_variation_woe,
               request_cnt_sum_coefficient_of_variation_cut)
df = trans_woe(df, "activation_periodicity_index", activation_periodicity_index_woe, activation_periodicity_index_cut)
df = trans_woe(df, "client_cnt_periodicity_index", client_cnt_periodicity_index_woe, client_cnt_periodicity_index_cut)
df = trans_woe(df, "request_cnt_sum_periodicity_index", request_cnt_sum_periodicity_index_woe, request_cnt_sum_periodicity_index_cut)
df = trans_woe(df, "activation_abnormal_index", activation_abnormal_index_woe, activation_abnormal_index_cut)
df = trans_woe(df, "client_cnt_abnormal_index", client_cnt_abnormal_index_woe, client_cnt_abnormal_index_cut)
df = trans_woe(df, "request_cnt_sum_abnormal_index", request_cnt_sum_abnormal_index_woe, request_cnt_sum_abnormal_index_cut)
df = trans_woe(df, "influence_score", influence_score_woe, influence_score_cut)
df = trans_woe(df, "predicted_activation", predicted_activation_woe, predicted_activation_cut)
df = trans_woe(df, "predicted_client_cnt", predicted_client_cnt_woe, predicted_client_cnt_cut)
df = trans_woe(df, "predicted_request_cnt_sum", predicted_request_cnt_sum_woe, predicted_request_cnt_sum_cut)
# df = trans_woe(df, "secrank_rank", secrank_rank_woe, secrank_rank_cut)
# df = trans_woe(df, "tranco_rank", tranco_rank_woe, tranco_rank_cut)
df = trans_woe(df, "predicted_company_score_rdata", predicted_company_score_rdata_woe, predicted_company_score_rdata_cut)

# 根据离散/连续分箱得到的各个指标对应的 IV 值筛选出预测能力强的 feature (?) -->
# IV 范围： | 无预测力  | 0.02  |  弱预测力  |  0.1   |  中预测力  |  0.2  |   强预测力
# todo

# feature_cols = IV 值条件筛选（或省略）
# feature_woe_cols = df 中 feature 对应的 woe 列
feature_cols = ['hold', 'pending', 'deleted', 'NXDOMAIN', 'parked', 'sinkholed',
                'register_lifespan', 'freq', 'activation_coefficient_of_variation',
                'client_cnt_coefficient_of_variation', 'request_cnt_sum_coefficient_of_variation',
                'activation_periodicity_index', 'client_cnt_periodicity_index',
                'request_cnt_sum_periodicity_index', 'activation_abnormal_index',
                'client_cnt_abnormal_index', 'request_cnt_sum_abnormal_index',
                'influence_score', 'predicted_activation', 'predicted_client_cnt', 
                'predicted_request_cnt_sum', 'predicted_company_score_rdata']  # todo
feature_woe_cols = [c for c in list(df.columns) if 'woe' in c]

# 将各个指标对应的分箱区间和 woe 值合成一张表 -->
# | Bucket | woe | features |
# todo 设置更多 feature
hold_df['features'] = 'hold'
pending_df['features'] = 'pending'
deleted_df['features'] = 'deleted'
NXDOMAIN_df['features'] = 'NXDOMAIN'
parked_df['features'] = 'parked'
sinkholed_df['features'] = 'sinkholed'
freq_df['features'] = 'freq'    # 1
register_lifespan_df['features'] = 'register_lifespan'
activation_coefficient_of_variation_df['features'] = 'activation_coefficient_of_variation'
client_cnt_coefficient_of_variation_df['features'] = 'client_cnt_coefficient_of_variation'
request_cnt_sum_coefficient_of_variation_df['features'] = 'request_cnt_sum_coefficient_of_variation'
activation_periodicity_index_df['features'] = 'activation_periodicity_index'
client_cnt_periodicity_index_df['features'] = 'client_cnt_periodicity_index'
request_cnt_sum_periodicity_index_df['features'] = 'request_cnt_sum_periodicity_index'
activation_abnormal_index_df['features'] = 'activation_abnormal_index'
client_cnt_abnormal_index_df['features'] = 'client_cnt_abnormal_index'
request_cnt_sum_abnormal_index_df['features'] = 'request_cnt_sum_abnormal_index'
influence_score_df['features'] = 'influence_score'
predicted_activation_df['features'] = 'predicted_activation'
predicted_client_cnt_df['features'] = 'predicted_client_cnt'
predicted_request_cnt_sum_df['features'] = 'predicted_request_cnt_sum'
# secrank_rank_df['features'] = 'secrank_rank'
# tranco_rank_df['features'] = 'tranco_rank'
predicted_company_score_rdata_df['features'] = 'predicted_company_score_rdata' # 1

# df_bin_to_woe = register_lifespan_df[['woe', 'features']]  # todo 拼接其他指标
df_bin_to_woe = pd.concat((register_lifespan_df.loc[:, ['woe', 'features']],
                           hold_df.loc[:, ['woe', 'features']],
                           pending_df.loc[:, ['woe', 'features']],
                           deleted_df.loc[:, ['woe', 'features']],
                           NXDOMAIN_df.loc[:, ['woe', 'features']],
                           parked_df.loc[:, ['woe', 'features']],
                           sinkholed_df.loc[:, ['woe', 'features']],
                           freq_df.loc[:, ['woe', 'features']],
                           activation_coefficient_of_variation_df.loc[:, ['woe', 'features']],
                           client_cnt_coefficient_of_variation_df.loc[:, ['woe', 'features']],
                           request_cnt_sum_coefficient_of_variation_df.loc[:, ['woe', 'features']],
                           activation_periodicity_index_df.loc[:, ['woe', 'features']],
                           client_cnt_periodicity_index_df.loc[:, ['woe', 'features']],
                           request_cnt_sum_periodicity_index_df.loc[:, ['woe', 'features']],
                           activation_abnormal_index_df.loc[:, ['woe', 'features']],
                           client_cnt_abnormal_index_df.loc[:, ['woe', 'features']],
                           request_cnt_sum_abnormal_index_df.loc[:, ['woe', 'features']],
                           influence_score_df.loc[:, ['woe', 'features']],
                           predicted_activation_df.loc[:, ['woe', 'features']],
                           predicted_client_cnt_df.loc[:, ['woe', 'features']],
                           predicted_request_cnt_sum_df.loc[:, ['woe', 'features']],
                           # secrank_rank_df.loc[:, ['woe', 'features']],
                           # tranco_rank_df.loc[:, ['woe', 'features']],
                           predicted_company_score_rdata_df.loc[:, ['woe', 'features']]
                           ))
df_bin_to_woe = df_bin_to_woe.reset_index()

# 模型训练和评估
# todo
from sklearn.model_selection import train_test_split

Y = df['IsHorrible']
X = df[['register_lifespan', 'register_lifespan_woe',
        'hold', 'hold_woe',
        'pending', 'pending_woe',
        'deleted', 'deleted_woe',
        'NXDOMAIN', 'NXDOMAIN_woe',
        'parked', 'parked_woe',
        'sinkholed', 'sinkholed_woe',
        'freq', 'freq_woe',
        'activation_coefficient_of_variation', 'activation_coefficient_of_variation_woe',
        'client_cnt_coefficient_of_variation', 'client_cnt_coefficient_of_variation_woe',
        'request_cnt_sum_coefficient_of_variation', 'request_cnt_sum_coefficient_of_variation_woe',
        'activation_periodicity_index', 'activation_periodicity_index_woe',
        'client_cnt_periodicity_index', 'client_cnt_periodicity_index_woe',
        'request_cnt_sum_periodicity_index', 'request_cnt_sum_periodicity_index_woe',
        'activation_abnormal_index', 'activation_abnormal_index_woe',
        'client_cnt_abnormal_index', 'client_cnt_abnormal_index_woe',
        'request_cnt_sum_abnormal_index', 'request_cnt_sum_abnormal_index_woe',
        'influence_score', 'influence_score_woe',
        'predicted_activation', 'predicted_activation_woe',
        'predicted_client_cnt', 'predicted_client_cnt_woe',
        'predicted_request_cnt_sum', 'predicted_request_cnt_sum_woe',
        # 'secrank_rank', 'secrank_rank_woe',
        # 'tranco_rank', 'tranco_rank_woe'
        'predicted_company_score_rdata', 'predicted_company_score_rdata_woe',
        ]]  # todo 选取更多属性列

# 测试和训练数据进行 3：7 的比例进行切分
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=123, stratify=Y)

train = pd.concat([Y_train, X_train], axis=1)
test = pd.concat([Y_test, X_test], axis=1)

from sklearn.linear_model import LogisticRegression

lrMod = LogisticRegression(penalty='l1', dual=False, tol=0.0001, C=1.0, fit_intercept=True,
                           intercept_scaling=1, class_weight=None, random_state=None, solver='liblinear', max_iter=100,
                           multi_class='ovr', verbose=2)

model = lrMod.fit(X_train[feature_woe_cols], Y_train)
# 查看在测试集上的性能
model.score(X_test[feature_woe_cols], Y_test)

# 生成评分卡 -->
score_card = generate_scorecard(model.coef_, df_bin_to_woe, feature_cols, B)
score_card.to_csv(input_file.split('/')[-1].split('.')[0] + '_score_card.csv', index=False)

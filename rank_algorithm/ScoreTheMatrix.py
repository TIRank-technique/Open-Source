import pandas as pd
import argparse

parser = argparse.ArgumentParser(description="Enter an input an output CSV file.")
parser.add_argument('input_file', type=str, help='Path to the input CSV file (feature matrix)')
parser.add_argument('output_file', type=str, help='Path to save the rank result(.csv)')
args = parser.parse_args()

input_file = args.input_file
output_file = args.output_file


def binary_search_largest_smaller(arr, target):
    arr[0] -= 99999999
    arr[-1] += 99999999
    if not arr:
        return -1
    left, right = 0, len(arr) - 1
    result = -1

    while left <= right:
        mid = (left + right) // 2
        if arr[mid] < target:
            result = mid  # 如果当前元素小于目标值，则更新结果为当前下标
            left = mid + 1
        else:
            right = mid - 1

    return result

# 读取评分卡数据
score_card = pd.read_csv(input_file.split('/')[-1].split('.')[0] + "_score_card.csv")

# 读取fqdn属性数据
fqdn_data = pd.read_csv(input_file.split('/')[-1].split('.')[0] + "_MATRIX.csv")

score_dict = {}
feature_is_visited = set()

for _, row in score_card.iterrows():
    variable = row["Variable"]
    binning = row["Binning"]
    score = row["Score"]
    binning_values = binning[1:-1].split(',')
    if variable not in feature_is_visited:
        feature_is_visited.add(variable)
        score_dict[variable] = [[float(binning_values[0]), float(binning_values[1])], [score]]
    else:
        score_dict[variable][0].append(float(binning_values[1]))
        score_dict[variable][1].append(score)


# 初始化评分结果
score_result_list = []

# 对每个fqdn计算评分
for index, row in fqdn_data.iterrows():
    fqdn_score = 0

    # 对于每个属性，查找其对应的分箱和分=数
    for col in fqdn_data.columns[1:]:  # 从第二列开始，第一列是fqdn
        if col not in score_dict:
            continue
        value = row[col]
        value_list = score_dict[col][0]
        score_list = score_dict[col][1]
        score_index = binary_search_largest_smaller(value_list, value)
        if score_index != -1:
            fqdn_score += score_list[score_index]

    # 将fqdn及其评分添加到结果中
    score_result_list.append({"domain": row["domain"], "Score": fqdn_score})

score_result = pd.DataFrame(score_result_list)
score_result = score_result.sort_values(by='Score')
score_result.to_csv(output_file, index=False)

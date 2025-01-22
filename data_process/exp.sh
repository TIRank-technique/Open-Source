#!/bin/bash

# Scrip Name: exp.sh
# Author: Yu Jingkai

# ---------- args define begin ----------
# 1. 选取的域名列表
# all_domains_temp_add_2_blacklist.json 890w域名
# high_value_TI.json 腾讯高质量威胁情报
# increase_black_pr.json 新增威胁情报&真实事件域名
domain_list=("use_this_blacklist.json")

# 2. 起始日期和结束日期
start_date="20240309"
end_date="20240315"

# 3. 选取的指标，0 表示假，1 表示真
register_status=1 # 注册状态 hold, pending, deleted
analyze_status=1 # 解析状态 NXDOMAIN
parking=1 # 是否parking
sinkhole=1 # 是否sinkhole
freq=1 # 存在于黑名单数量
register_lifespan=1 # 注册生命周期
trend=1 # 活跃度趋势k
predicted=1 # 趋势变化，客户端、解析量、活跃度，需要 alpha
cv=1 # 变异系数，客户端、解析量、活跃度
periodicity=1 # 周期性，客户端、解析量、活跃度
abnormal=1 # 突变概率，客户端、解析量、活跃度
influence_score=1 # 影响力
company_client_ip=0 # 伴随分数（客户端），需要 alpha
company_rdata=1 # 伴随分数（rdata），需要 alpha

# 4. 需要 emwa 压缩时间序列的指标使用的 alpha 值，包括趋势变化与伴随分数
alpha=0.2
# 5. 周期性计算threshold
threshold=0.1
# 6. 突变概率指数最小样本数
min_samples=5
# 7. 影响力重力因子常数G
G=1.8

# ---------- args define end ----------

# 1. 生成时间戳
echo "1. Generating timestamp..."
timestamp=$(date "+%Y%m%d%H%M%S")

# 2. 设置实验参数 json
echo "2. Printing experiment parameters..."
declare -A params
declare -A time_costs
params=(
    ["timestamp"]=$timestamp
    ["domain_list"]=$domain_list
    ["start_date"]=$start_date
    ["end_date"]=$end_date
    ["register_status"]=$register_status
    ["analyze_status"]=$analyze_status
    ["parking"]=$parking
    ["sinkhole"]=$sinkhole
    ["freq"]=$freq
    ["register_lifespan"]=$register_lifespan
    ["trend"]=$trend
    ["predicted"]=$predicted
    ["cv"]=$cv
    ["periodicity"]=$periodicity
    ["abnormal"]=$abnormal
    ["influence_score"]=$influence_score
    ["company_client_ip"]=$company_client_ip
    ["company_rdata"]=$company_rdata
)


# 3. 计算不需要选择时间窗口的指标
echo "3. Calculating indicators not need time window..."
# 3.1 计算注册状态 [Done]
if [ $register_status -eq 1 ]; then
    echo "3.1 Calculating register status..."
    start_time=$(date +%s)
    python3 register_status.py --domain_list ${domain_list[@]} --timestamp $timestamp
    end_time=$(date +%s)
    time_costs["register_status"]=$(echo "scale=2; ($end_time-$start_time)/60" | bc)
fi
# 3.2 计算解析状态 [Done]
if [ $analyze_status -eq 1 ]; then
    echo "3.2 Calculating analyze status..."
    start_time=$(date +%s)
    python3 analyze_status.py --domain_list ${domain_list[@]} --timestamp $timestamp
    end_time=$(date +%s)
    time_costs["analyze_status"]=$(echo "scale=2; ($end_time-$start_time)/60" | bc)
fi
# 3.3 计算parking [Done]
if [ $parking -eq 1 ]; then
    echo "3.3 Calculating parking..."
    start_time=$(date +%s)
    python3 parking.py --domain_list ${domain_list[@]} --timestamp $timestamp
    end_time=$(date +%s)
    time_costs["parking"]=$(echo "scale=2; ($end_time-$start_time)/60" | bc)
fi
# 3.4 计算sinkhole [Done]
if [ $sinkhole -eq 1 ]; then
    echo "3.4 Calculating sinkhole..."
    start_time=$(date +%s)
    python3 sinkhole.py --domain_list ${domain_list[@]} --timestamp $timestamp
    end_time=$(date +%s)
    time_costs["sinkhole"]=$(echo "scale=2; ($end_time-$start_time)/60" | bc)
fi
# 3.5 计算存在于黑名单数量 [Done]
if [ $freq -eq 1 ]; then
    echo "3.5 Calculating freq..."
    start_time=$(date +%s)
    python3 freq.py --domain_list ${domain_list[@]} --timestamp $timestamp
    end_time=$(date +%s)
    time_costs["freq"]=$(echo "scale=2; ($end_time-$start_time)/60" | bc)
fi
# 3.6 计算注册生命周期 [Done]
if [ $register_lifespan -eq 1 ]; then
    echo "3.6 Calculating register lifespan..."
    start_time=$(date +%s)
    python3 register_lifespan.py --domain_list ${domain_list[@]} --timestamp $timestamp
    end_time=$(date +%s)
    time_costs["register_lifespan"]=$(echo "scale=2; ($end_time-$start_time)/60" | bc)
fi


# 4. 计算需要选择时间窗口的指标
echo "4. Calculating indicators need time window..."
# 4.1 计算活跃度趋势 [Done]
if [ $trend -eq 1 ]; then
    echo "4.1 Calculating trend..."
    start_time=$(date +%s)
    python3 trend.py --domain_list ${domain_list[@]} --timestamp $timestamp --start_date $start_date --end_date $end_date
    end_time=$(date +%s)
    time_costs["trend"]=$(echo "scale=2; ($end_time-$start_time)/60" | bc)
fi
# 4.2 计算趋势变化 [Done]
if [ $predicted -eq 1 ]; then
    echo "4.2 Calculating predicted..."
    start_time=$(date +%s)
    python3 predicted.py --domain_list ${domain_list[@]} --timestamp $timestamp --start_date $start_date --end_date $end_date --alpha $alpha
    end_time=$(date +%s)
    time_costs["predicted"]=$(echo "scale=2; ($end_time-$start_time)/60" | bc)
fi
# 4.3 计算变异系数 [Done]
if [ $cv -eq 1 ]; then
    echo "4.3 Calculating cv..."
    start_time=$(date +%s)
    python3 cv.py --domain_list ${domain_list[@]} --timestamp $timestamp --start_date $start_date --end_date $end_date
    end_time=$(date +%s)
    time_costs["cv"]=$(echo "scale=2; ($end_time-$start_time)/60" | bc)
fi
# 4.4 计算周期性 [Done] TODO: 检查数据是否全为0
if [ $periodicity -eq 1 ]; then
    echo "4.4 Calculating periodicity..."
    start_time=$(date +%s)
    python3 periodicity.py --domain_list ${domain_list[@]} --timestamp $timestamp --start_date $start_date --end_date $end_date --threshold $threshold
    end_time=$(date +%s)
    time_costs["periodicity"]=$(echo "scale=2; ($end_time-$start_time)/60" | bc)
fi
# 4.5 计算突变概率 [Done] TODO: 检查数据是否全为0
if [ $abnormal -eq 1 ]; then
    echo "4.5 Calculating abnormal..."
    start_time=$(date +%s)
    python3 abnormal.py --domain_list ${domain_list[@]} --timestamp $timestamp --start_date $start_date --end_date $end_date --min_samples $min_samples
    end_time=$(date +%s)
    time_costs["abnormal"]=$(echo "scale=2; ($end_time-$start_time)/60" | bc)
fi
# 4.6 计算影响力 [Done]
if [ $influence_score -eq 1 ]; then
    echo "4.6 Calculating influence score..."
    start_time=$(date +%s)
    python3 influence_score.py --domain_list ${domain_list[@]} --timestamp $timestamp --start_date $start_date --end_date $end_date --G $G
    end_time=$(date +%s)
    time_costs["influence_score"]=$(echo "scale=2; ($end_time-$start_time)/60" | bc)
fi
# 4.7 计算伴随分数（客户端） [In Progress]
#if [ $company_client_ip -eq 1 ]; then
#    echo "4.7 Calculating company client ip..."
#    start_time=$(date +%s)
#    python3 company_client_ip.py --domain_list ${domain_list[@]} --timestamp $timestamp --start_date $start_date --end_date $end_date
#    end_time=$(date +%s)
#    time_costs["company_client_ip"]=$(echo "scale=2; ($end_time-$start_time)/60" | bc)
#fi
# 4.8 计算伴随分数（rdata） [Done]
if [ $company_rdata -eq 1 ]; then
    echo "4.8 Calculating company rdata..."
    start_time=$(date +%s)
    python3 company_rdata.py --domain_list ${domain_list[@]} --timestamp $timestamp --start_date $start_date --end_date $end_date --alpha $alpha
    end_time=$(date +%s)
    time_costs["company_rdata"]=$(echo "scale=2; ($end_time-$start_time)/60" | bc)
fi

# 5. 输出实验参数 json
echo "5. Outputting experiment parameters..."
# 添加time_costs的每个元素到params数组中
for key in "${!time_costs[@]}"; do
    params["time_costs_$key"]=${time_costs[$key]}
done

# 将params数组转换为JSON格式并输出
json_string=""
for key in "${!params[@]}"; do
    value=${params[$key]}
    if [[ $value =~ ^[0-9]+$ ]]; then
        json_string+=",\"$key\":$value"
    else
        json_string+=",\"$key\":\"$value\""
    fi
done
json_string=${json_string:1}
json_string="{$json_string}"
echo $json_string >> ../matrix_results/matrix_abs.json

# 6. 构建和输出指标矩阵
echo "6. Building and outputting matrix..."
python3 matrix.py --timestamp $timestamp

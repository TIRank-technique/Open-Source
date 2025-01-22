# codes

## abnormal.py

计算突变概率

| 参数            | 类型 | 描述                                                   |
| --------------- | ---- | ------------------------------------------------------ |
| `--domain_list` | 入参 | 域名列表，每个值对应`../domain_list`下的同名域名列表   |
| `--start_date`  | 入参 | 起始日期，形如`20240101`的字符串，用于选取PDNS范围     |
| `--end_date`    | 入参 | 结束日期，形如`20240101`的字符串，用于选取PDNS范围     |
| `--timestamp`   | 入参 | 时间戳，形如`20240610xxxxxx`的字符串，用于标记同组实验 |
| `--min_samples` | 入参 | 形如`5`的数字，用于突变概率的聚类点数量下限            |

| 输出目录                                                     | 表头                                |
| ------------------------------------------------------------ | ----------------------------------- |
| `../activity/client_cnt_abnormal_index/{timestamp}_client_cnt_abnormal_index.csv` | fqdn,client_cnt_abnormal_index      |
| `../activity/request_cnt_sum_abnormal_index/{timestamp}_request_cnt_sum_abnormal_index.csv` | fqdn,request_cnt_sum_abnormal_index |
| `../activity/activation_abnormal_index/{timestamp}_activation_abnormal_index.csv` | fqdn,activation_abnormal_index      |

## analyze_status.py

解析状态，关注 NXDOMAIN

| 参数            | 类型 | 描述                                                   |
| --------------- | ---- | ------------------------------------------------------ |
| `--domain_list` | 入参 | 域名列表，每个值对应`../domain_list`下的同名域名列表   |
| `--timestamp`   | 入参 | 时间戳，形如`20240610xxxxxx`的字符串，用于标记同组实验 |

| 输出目录                                                    | 表头            |
| ----------------------------------------------------------- | --------------- |
| `../validity/analyze_status/{timestamp}_analyze_status.csv` | domain,NXDOMAIN |

## company_rdata.py

伴生恶意域名分数rdata

| 参数            | 类型 | 描述                                                    |
| --------------- | ---- | ------------------------------------------------------- |
| `--domain_list` | 入参 | 域名列表，每个值对应`../domain_list`下的同名域名列表    |
| `--start_date`  | 入参 | 起始日期，形如`20240101`的字符串，用于选取PDNS范围      |
| `--end_date`    | 入参 | 结束日期，形如`20240101`的字符串，用于选取PDNS范围      |
| `--timestamp`   | 入参 | 时间戳，形如`20240610xxxxxx`的字符串，用于标记同组实验  |
| `--alpha`       | 入参 | 形如`0.2`的数字，emwa 压缩时间序列的指标使用的 alpha 值 |

| 输出目录                                                     | 表头            |
| ------------------------------------------------------------ | --------------- |
| `../aggregation/predicted_company_score_rdata/{timestamp}_predicted_company_score_rdata.csv` | fqdn,[时间序列] |

## cv.py

变异系数（客户端、解析量、活跃度）

| 参数            | 类型 | 描述                                                   |
| --------------- | ---- | ------------------------------------------------------ |
| `--domain_list` | 入参 | 域名列表，每个值对应`../domain_list`下的同名域名列表   |
| `--start_date`  | 入参 | 起始日期，形如`20240101`的字符串，用于选取PDNS范围     |
| `--end_date`    | 入参 | 结束日期，形如`20240101`的字符串，用于选取PDNS范围     |
| `--timestamp`   | 入参 | 时间戳，形如`20240610xxxxxx`的字符串，用于标记同组实验 |

| 输出目录                                                     | 表头                                          |
| ------------------------------------------------------------ | --------------------------------------------- |
| `../activity/client_cnt_coefficient_of_variation/{timestamp}_client_cnt_coefficient_of_variation.csv` | fqdn,client_cnt_coefficient_of_variation      |
| `../activity/request_cnt_sum_coefficient_of_variation/{timestamp}_request_cnt_sum_coefficient_of_variation.csv` | fqdn,request_cnt_sum_coefficient_of_variation |
| `../activity/activation_coefficient_of_variation/{timestamp}_activation_coefficient_of_variation.csv` | fqdn,activation_coefficient_of_variation      |

## exp.sh

计算指标矩阵（各指标的计算过程串行，可以获得每个程序的执行时间）

| 参数          | 类型       | 描述                                                         |
| ------------- | ---------- | ------------------------------------------------------------ |
| `domain_list` | 字符串数组 | 域名列表，每个值对应`../domain_list`下的同名域名列表         |
| `start_date`  | 字符串     | 起始日期，形如`20240101`的字符串，用于选取PDNS范围           |
| `end_date`    | 字符串     | 结束日期，形如`20240101`的字符串，用于选取PDNS范围           |
| 各指标        | 0或1       | 表示本组实验是否选取该指标                                   |
| `alpha`       | 小数       | 需要 emwa 压缩时间序列的指标使用的 alpha 值，包括趋势变化与伴随分数 |
| `threshold`   | 小数       | 周期性计算threshold                                          |
| `min_samples` | 整数       | 突变概率指数最小样本数                                       |
| `G`           | 小数       | 影响力重力因子常数G                                          |

## exp_parallel.sh

计算指标矩阵（各指标的计算过程并行，目前无法计算每个程序的执行时间）

| 参数          | 类型       | 描述                                                         |
| ------------- | ---------- | ------------------------------------------------------------ |
| `domain_list` | 字符串数组 | 域名列表，每个值对应`../domain_list`下的同名域名列表         |
| `start_date`  | 字符串     | 起始日期，形如`20240101`的字符串，用于选取PDNS范围           |
| `end_date`    | 字符串     | 结束日期，形如`20240101`的字符串，用于选取PDNS范围           |
| 各指标        | 0或1       | 表示本组实验是否选取该指标                                   |
| `alpha`       | 小数       | 需要 emwa 压缩时间序列的指标使用的 alpha 值，包括趋势变化与伴随分数 |
| `threshold`   | 小数       | 周期性计算threshold                                          |
| `min_samples` | 整数       | 突变概率指数最小样本数                                       |
| `G`           | 小数       | 影响力重力因子常数G                                          |

## freq.py

计算域名在不同黑名单中出现的次数

| 参数            | 类型 | 描述                                                   |
| --------------- | ---- | ------------------------------------------------------ |
| `--domain_list` | 入参 | 域名列表，每个值对应`../domain_list`下的同名域名列表   |
| `--timestamp`   | 入参 | 时间戳，形如`20240610xxxxxx`的字符串，用于标记同组实验 |

| 输出目录                                | 表头        |
| --------------------------------------- | ----------- |
| `../validity/freq/{timestamp}_freq.csv` | domain,freq |

## influence_score.py

计算域名的影响力分数

| 参数            | 类型 | 描述                                                   |
| --------------- | ---- | ------------------------------------------------------ |
| `--domain_list` | 入参 | 域名列表，每个值对应`../domain_list`下的同名域名列表   |
| `--start_date`  | 入参 | 起始日期，形如`20240101`的字符串，用于选取PDNS范围     |
| `--end_date`    | 入参 | 结束日期，形如`20240101`的字符串，用于选取PDNS范围     |
| `--timestamp`   | 入参 | 时间戳，形如`20240610xxxxxx`的字符串，用于标记同组实验 |
| `G`             | 入参 | 影响力重力因子常数G，形如1.8                           |

| 输出目录                                                     | 表头                 |
| ------------------------------------------------------------ | -------------------- |
| `../activity/influence_score/{timestamp}_influence_score.csv` | fqdn,influence_score |

## matrix.py

根据计算的各指标值整合为域名-指标矩阵

| 参数          | 类型 | 描述                                                   |
| ------------- | ---- | ------------------------------------------------------ |
| `--timestamp` | 入参 | 时间戳，形如`20240610xxxxxx`的字符串，用于标记同组实验 |

| 输出目录                                   | 表头             |
| ------------------------------------------ | ---------------- |
| `../matrix_results/{timestamp}_matrix.csv` | domain, 指标列表 |

## parking.py

域名是否 parking

| 参数            | 类型 | 描述                                                   |
| --------------- | ---- | ------------------------------------------------------ |
| `--domain_list` | 入参 | 域名列表，每个值对应`../domain_list`下的同名域名列表   |
| `--timestamp`   | 入参 | 时间戳，形如`20240610xxxxxx`的字符串，用于标记同组实验 |

| 输出目录              | 表头          |
| --------------------- | ------------- |
| `../validity/parking` | domain,parked |

## periodicity.py

周期性活跃指标（客户端、解析量、活跃度）

| 参数            | 类型 | 描述                                                   |
| --------------- | ---- | ------------------------------------------------------ |
| `--domain_list` | 入参 | 域名列表，每个值对应`../domain_list`下的同名域名列表   |
| `--start_date`  | 入参 | 起始日期，形如`20240101`的字符串，用于选取PDNS范围     |
| `--end_date`    | 入参 | 结束日期，形如`20240101`的字符串，用于选取PDNS范围     |
| `--timestamp`   | 入参 | 时间戳，形如`20240610xxxxxx`的字符串，用于标记同组实验 |
| `--threshold`   | 入参 | 周期性计算threshold                                    |

| 输出目录                                                     | 表头                                   |
| ------------------------------------------------------------ | -------------------------------------- |
| `../activity/client_cnt_periodicity_index/{timestamp}_client_cnt_periodicity_index` | fqdn,client_cnt_periodicity_index      |
| `../activity/request_cnt_sum_periodicity_index/{timestamp}_request_cnt_sum_periodicity_index` | fqdn,request_cnt_sum_periodicity_index |
| `../activity/activation_periodicity_index/{timestamp}_activation_periodicity_index` | fqdn,activation_periodicity_index      |

## predicted.py

活跃度趋势（客户端、解析量、活跃度）

| 参数            | 类型 | 描述                                                    |
| --------------- | ---- | ------------------------------------------------------- |
| `--domain_list` | 入参 | 域名列表，每个值对应`../domain_list`下的同名域名列表    |
| `--start_date`  | 入参 | 起始日期，形如`20240101`的字符串，用于选取PDNS范围      |
| `--end_date`    | 入参 | 结束日期，形如`20240101`的字符串，用于选取PDNS范围      |
| `--timestamp`   | 入参 | 时间戳，形如`20240610xxxxxx`的字符串，用于标记同组实验  |
| `--alpha`       | 入参 | 形如`0.2`的数字，emwa 压缩时间序列的指标使用的 alpha 值 |

| 输出目录                                                     | 表头            |
| ------------------------------------------------------------ | --------------- |
| `../activity/predicted_client_cnt/{timestamp}_predicted_client_cnt.csv` | fqdn,[时间序列] |
| `../activity/predicted_request_cnt_sum/{timestamp}_predicted_request_cnt_sum.csv` | fqdn,[时间序列] |
| `../activity/predicted_activation/{timestamp}_predicted_activation.csv` | fqdn,[时间序列] |

## register_lifespan.py

注册生命周期

| 参数            | 类型 | 描述                                                   |
| --------------- | ---- | ------------------------------------------------------ |
| `--domain_list` | 入参 | 域名列表，每个值对应`../domain_list`下的同名域名列表   |
| `--timestamp`   | 入参 | 时间戳，形如`20240610xxxxxx`的字符串，用于标记同组实验 |

| 输出目录                                                     | 表头                     |
| ------------------------------------------------------------ | ------------------------ |
| `../activity/register_lifespan/{timestamp}_register_lifespan.csv` | domain,register_lifespan |

## register_status.py

注册状态，主要关注 hold, pending deleted, deleted

| 参数            | 类型 | 描述                                                   |
| --------------- | ---- | ------------------------------------------------------ |
| `--domain_list` | 入参 | 域名列表，每个值对应`../domain_list`下的同名域名列表   |
| `--timestamp`   | 入参 | 时间戳，形如`20240610xxxxxx`的字符串，用于标记同组实验 |

| 输出目录                                                     | 表头                        |
| ------------------------------------------------------------ | --------------------------- |
| `../validity/register_status/{timestamp}_register_status.csv` | domain,hold,pending,deleted |

## sinkhole.py

域名取缔

| 参数            | 类型 | 描述                                                   |
| --------------- | ---- | ------------------------------------------------------ |
| `--domain_list` | 入参 | 域名列表，每个值对应`../domain_list`下的同名域名列表   |
| `--timestamp`   | 入参 | 时间戳，形如`20240610xxxxxx`的字符串，用于标记同组实验 |

| 输出目录                                        | 表头             |
| ----------------------------------------------- | ---------------- |
| `../validity/sinkhole/{timestamp}_sinkhole.csv` | domain,sinkholed |

## trend.py

活跃度趋势

| 参数            | 类型 | 描述                                                   |
| --------------- | ---- | ------------------------------------------------------ |
| `--domain_list` | 入参 | 域名列表，每个值对应`../domain_list`下的同名域名列表   |
| `--start_date`  | 入参 | 起始日期，形如`20240101`的字符串，用于选取PDNS范围     |
| `--end_date`    | 入参 | 结束日期，形如`20240101`的字符串，用于选取PDNS范围     |
| `--timestamp`   | 入参 | 时间戳，形如`20240610xxxxxx`的字符串，用于标记同组实验 |

| 输出目录                                  | 表头     |
| ----------------------------------------- | -------- |
| `../activity/trend/{timestamp}_trend.csv` | domain,k |

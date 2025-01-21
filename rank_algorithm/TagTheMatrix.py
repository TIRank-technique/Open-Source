import pandas as pd
import argparse
import tldextract

# 设置命令行参数解析
parser = argparse.ArgumentParser(description="Process an input CSV file.")
parser.add_argument('input_file', type=str, help='Path to the input CSV file (feature matrix)')
args = parser.parse_args()

input_file = args.input_file

horrible_domains = set()
with open('train_set.txt', 'r') as file:
    for line in file:
        horrible_domains.add(line.strip())

df = pd.read_csv(input_file)
# df.fillna(0, inplace=True)

df = df[df['domain'].str.contains('.', regex=False)]


with open('./filter_data/white_domains.txt', 'r') as file:
    white_domains = set(line.strip() for line in file)

df = df[~df['domain'].isin(white_domains)]

public_serve_domains = set()
with open('./filter_data/public_serve_domains.txt', 'r') as file:
    # public_serve_domains = set(line.strip() for line in file)
    for line in file:
        if 'blogspot.' not in line:
            public_serve_domains.add(line.strip())


public_serve_fqdn = set()

def is_public_service_domain(fqdn):
    # 提取 FQDN 的主域名（例如 example.com）
    ext = tldextract.extract(fqdn)
    domain = f"{ext.domain}.{ext.suffix}"
    
    # 检查该域名是否在公共服务域名集合中
    if domain not in horrible_domains and domain in public_serve_domains:
        public_serve_fqdn.add(fqdn)
        return True
    return False
    # return domain not in horrible_domains and domain in public_serve_domains


# 使用 is_public_service_domain 函数过滤 domain 列
df = df[~df['domain'].apply(is_public_service_domain)]


with open("public_serve_fqdns.txt", 'w') as out_file:
    public_serve_fqdn_list = list(public_serve_fqdn)
    public_serve_fqdn_list.sort()
    for item in public_serve_fqdn_list:
        out_file.write(item + "\n")
    print("public serve fqdn write out!")


# 对于 freq 和 predicted_company_score_rdata 列，填充 NaN 为 1 (符合基本事实)
df[['freq', 'predicted_company_score_rdata']] = df[['freq', 'predicted_company_score_rdata']].fillna(1)

# 对于连续性变量且正常计算值大于 0 的，填充 NaN 为 0 
df.fillna(0, inplace=True)

# 添加 IsHorrible 列并设置初始值为 0
df['IsHorrible'] = 0

# 先过滤出 domain 在 horrible_domains 中的行
horrible_mask = df['domain'].isin(horrible_domains)

# 再检查 hold, pending, deleted, NXDOMAIN, parked, sinkholed 字段是否都是 0
status_mask = (df[['hold', 'sinkholed']] == 0).all(axis=1)

# 将 IsHorrible 置为 1
df.loc[horrible_mask & status_mask, 'IsHorrible'] = 1


print(">>>>>>>>>")
print(df['IsHorrible'].sum())

# 保存结果到新的 CSV 文件
df.to_csv(input_file.split('/')[-1].split('.')[0] + '_MATRIX.csv', index=False)


import pandas as pd

# 1. 读取两个Excel文件
program_details_df = pd.read_excel("data\\UCL\\program_details_add_id.xlsx")
ucl_df = pd.read_excel("data\\UCL\\ucl_standard.xlsx")

# 1.1 为 "官网链接" 列添加不同的后缀
program_details_df = program_details_df.rename(columns={"官网链接": "官网链接_机器"})
ucl_df = ucl_df.rename(columns={"官网链接": "官网链接_人工"})

# 2. 使用“官网链接”列进行内部连接，得到匹配的数据
matched_df = pd.merge(program_details_df, ucl_df, left_on="官网链接_机器", right_on="官网链接_人工", how="inner", suffixes=('_机器', '_人工'))

# 3. 使用外部连接得到所有数据，然后从中删除匹配的数据，得到未匹配的数据
all_df = pd.merge(program_details_df, ucl_df, left_on="官网链接_机器", right_on="官网链接_人工", how="outer", suffixes=('_机器', '_人工'))
unmatched_df = all_df[~all_df["官网链接_机器"].isin(matched_df["官网链接_机器"]) & ~all_df["官网链接_人工"].isin(matched_df["官网链接_人工"])]

# 4. 将匹配的数据和未匹配的数据进行垂直拼接
final_df = pd.concat([matched_df, unmatched_df], axis=0)

# 5. 交叉放置两个表的列
columns_pro = [col for col in final_df.columns if col.endswith('_机器')]
columns_ucl = [col for col in final_df.columns if col.endswith('_人工')]
reordered_columns = []
for col_pro, col_ucl in zip(columns_pro, columns_ucl):
    reordered_columns.append(col_pro)
    reordered_columns.append(col_ucl)

final_df = final_df[reordered_columns]

# 6. 保存合并后的数据表
final_df.to_excel("evaluate.xlsx", index=False)

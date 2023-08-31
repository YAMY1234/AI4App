# from spiders import UCL

# def main():
#     # print("crawling program details...")
#     # ucl_program_crawler = UCL.UCLProgramURLCrawler()
#     # ucl_program_crawler.crawl()
#     print("crawling UCL details...")
#     ucl_detail_crawler = UCL.UCLProgramDetailsCrawler(test=True, verbose=True)
#     ucl_detail_crawler.get_program_useful_links()
#     ucl_detail_crawler.generate_program_details(translate=False)
#     # 具体实现...

# if __name__ == "__main__":
#     main()

import pandas as pd
# 1. 读取两个Excel文件
program_df = pd.read_excel("data\\UCL\\program_details.xlsx")
standard_df = pd.read_excel("data\\UCL\\ucl_standard.xlsx") 
def add_program_id(program_df, standard_df):
    # 2. 对“ucl项目含ID.xlsx”中的数据进行迭代
    for index, row in program_df.iterrows():
        link = row["官网链接"]
        matched_row = standard_df[standard_df["官网链接"] == link]
        
        # 3. 如果找到匹配的行，更新“专业ID”列
        if not matched_row.empty:
            program_id = str(matched_row["专业ID"].values[0]).zfill(7)
            program_df.at[index, "专业ID"] = program_id

    # 4. 保存更新后的“program_details.xlsx”
    output_path = "data\\UCL\\program_details_add_id.xlsx"
    program_df.to_excel(output_path, index=False)

add_program_id(program_df, standard_df)
import pandas as pd


def author_analysis(path: str):
    # 指定 Excel 文件的路径
    df = pd.read_excel(path)
        # 按 cex 和 nickname 分组，并计算 viewcount, like, forward, comment 的总计数
    df['发帖数'] = 1
    aggregated_counts = df.groupby(['nickname']).agg({
        'viewcount': 'sum',
        'like': 'sum',
        'forward': 'sum',
        'comment': 'sum',
        '发帖数':'sum'
    }).reset_index()
    aggregated_counts['互动数']=aggregated_counts['like']+aggregated_counts['forward']+aggregated_counts['comment']

    return aggregated_counts


def deal_xlsx_data(path: str):
    # 指定 Excel 文件的路径
    df = pd.read_excel(path)


    # 设置最大行数和列数
    pd.set_option('display.max_rows', None)  # None 表示显示所有行
    pd.set_option('display.max_columns', None)  # None 表示显示所有列

    # 设置每列最大显示宽度
    pd.set_option('display.max_colwidth', None)  # None 表示不限制每列的宽度

    # 设置显示的精度，例如小数位数
    pd.set_option('display.precision', 3)  # 设置浮点数显示的精度

    # 设置行列之间的分隔符，便于阅读
    pd.set_option('display.expand_frame_repr', False)  # False 防止 DataFrame 换行


    # 1. 计算每个 cex 的总行数
    cex_counts = df['cex'].value_counts().reset_index()
    cex_counts.columns = ['cex', 'total_rows']

    # 2. 按照 cex 进行聚合
    aggregated_df = df.groupby('cex').agg(
        total_viewcount=('viewcount', 'sum'),
        total_like=('like', 'sum'),
        total_forward=('forward', 'sum'),
        total_comment=('comment', 'sum')
    ).reset_index()

    # 3. 计算 interaction 列
    aggregated_df['total_interaction'] = aggregated_df['total_like'].astype(int) + aggregated_df[
        'total_forward'].astype(int) + aggregated_df['total_comment'].astype(int)

    # 4. 合并行数统计与聚合结果
    result_df = pd.merge(cex_counts, aggregated_df, on='cex')

    # 创建新行的数据
    total = pd.Series({
        'cex': '总计',  # 设置自定义总计标签
        'total_rows': result_df['total_rows'].sum(),
        'total_viewcount': result_df['total_viewcount'].sum(),
        'total_like': result_df['total_like'].sum(),  # 其他列也可以相应地总和
        'total_forward': result_df['total_forward'].sum(),
        'total_comment': result_df['total_comment'].sum(),
        'total_interaction': result_df['total_interaction'].sum()
    })
    result_df = result_df._append(total, ignore_index=True)
    result_df['total_forward'] = result_df['total_forward'].astype(int)

    return result_df


def main():
    old = r'D:\Users\bjc\DESK\pycharm\com.gateio.analysis\tmp\WeChat 0205-0211.xlsx'
    new = r'D:\Users\bjc\DESK\pycharm\com.gateio.analysis\tmp\WeChat 0212-0218.xlsx'

    now = deal_xlsx_data(new)
    oldTmp = deal_xlsx_data(old)
    old = oldTmp.rename(columns={
        'cex':'cex','total_rows': 'total_rows_old', 'total_viewcount':'total_viewcount_old','total_like': 'total_like_old','total_forward': 'total_forward_old', 'total_comment':'total_comment_old', 'total_interaction':'total_interaction_old'
    })
    result = pd.merge(now,old,on='cex',how='outer')
    result = result.loc[:,['cex','total_rows','total_rows_old' , 'total_viewcount' , 'total_viewcount_old','total_like','total_like_old',  'total_forward' ,'total_forward_old', 'total_comment', 'total_comment_old', 'total_interaction'  ,  'total_interaction_old']]
    result1 = result
    for now in ['total_rows','total_viewcount','total_like','total_forward','total_comment','total_interaction']:
        old = now +'_old'
        result[f'{now}_rate']=round((result[now]-result[old])/result[old]*100,2)
        result[f'{now}_rate'] = (result[f'{now}_rate'].astype(str)+'%')
    result = result.loc[:,['cex','total_rows','total_rows_rate','total_viewcount','total_viewcount_rate','total_like','total_like_rate','total_forward','total_forward_rate','total_comment','total_interaction','total_interaction_rate']]

    # result = result['cex','文章数','环比','观看数','环比','点赞数','环比','转发数','环比','评论数','互动数','环比']
    df1 = result
    df2 = author_analysis(new)
    # 使用 ExcelWriter 写入不同的工作表
    with pd.ExcelWriter('../tmp/微信.xlsx') as writer:
        result1.to_excel(writer, sheet_name='新旧占比对比', index=False)  # 写入第一个工作表
        df1.to_excel(writer, sheet_name='占比结果', index=False)  # 写入第一个工作表
        df2.to_excel(writer, sheet_name='作者', index=False)  # 写入第二个工作表
if __name__ == '__main__':
    """
    原始数据采集的列可看往期的微信数采  https://gtglobal.jp.larksuite.com/sheets/M1Z2sEX75hWdbKtjFTkjA99pp3b
    执行之前只需要将 old和new 参数的文件位置填入即可，old为上周期， new为本周期，单双周亦如此。
    最后的结果文件写入到 tmp文档下，有环比sheet页和作者互动页可贴入报告中
    """
    main()

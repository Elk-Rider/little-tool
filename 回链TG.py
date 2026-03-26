import csv
import time
from datetime import datetime

from DrissionPage import Chromium, ChromiumOptions

# 获取当前时间
now = datetime.now()
# 格式化时间
current_time = now.strftime("%m-%d")
print("当前时间:", current_time)


def convert_abbreviated_number(value):
    if isinstance(value, str):
        value = value.strip().upper()  # 去掉空格并转换为大写
        if value.endswith('K'):
            return float(value[:-1]) * 1_000
        elif value.endswith('M'):
            return float(value[:-1]) * 1_000_000
        elif value.endswith('B'):
            return float(value[:-1]) * 1_000_000_000
        else:
            try:
                return float(value)  # 不是K、M、B的情况，直接转为float
            except ValueError:
                return None  # 如果无法转换，返回None
    return None  # 如果输入不是字符串，返回None


def getdetails():
    co = ChromiumOptions()
    """
    True 就是没有页面显示
    False 就是显示页面
    """
    co.headless(False)
    # 以该配置创建页面对象
    chrom = Chromium(addr_or_opts=co)
    total = []
    # 打开小红书搜索页面，添加你想要搜索的关键词
    with open(rf'D:\Users\bjc\DESK\pycharm\com.gateio.analysis\tg.txt', 'r', encoding='utf-8') as file:
        for line in file:
            try:
                url = line.strip()
                # 使用分割的方法筛选出包含'bpaygroup'的部分
                filtered_part = url.split('/')  # 按'/'分割字符串
                author = filtered_part[3]
                page = chrom.new_tab(url)
                time.sleep(2)
                result = {}
                result['url'] = url
                result['author'] = author
                result['full_text'] = page.ele('.tgme_widget_message_text js-message_text').text
                result['view_count'] = convert_abbreviated_number(page.ele('.tgme_widget_message_views').text)
                total.append(result)

                chrom.close_tabs(chrom.get_tab(url=url))
            except Exception as e:
                print(url + "有问题")
    return total


def main():
    fields = ['url', 'author', 'full_text', 'view_count']

    with open(f"../tmp/TG回链数据_{current_time}.csv", mode="w", newline="", encoding='UTF-8') as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        # 写入表头
        writer.writeheader()
        # 写入数据
        writer.writerows(getdetails())


if __name__ == '__main__':
    """
    执行需要在tg.txt文件中列出所有回链地址
    首次失败的数据量比较多则将失败的地址重新抓取，但需要将之前的结果上传lark，否则会被覆盖
    实在不行的手动填充。
    """
    main()

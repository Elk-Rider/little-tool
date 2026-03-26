import csv
import re
import threading
import time
from datetime import datetime

from DrissionPage import Chromium, ChromiumOptions
from bs4 import BeautifulSoup

from util.csv文件合并 import csv_combine


# 日期转换
def timeformat(date_str: str):
    # 将字符串转换为日期对象
    date_obj = datetime.strptime(date_str, "%Y. %m. %d.")
    # 格式化为所需的字符串格式
    formatted_date = date_obj.strftime("%Y-%m-%d")
    return formatted_date  # 输出: 2025-01-02  from datetime import datetime


def getdetails(key_word: str, start: str, end: str, port: int):
    co = ChromiumOptions()
    co.headless(True)
    co.set_local_port(port)
    chrom = Chromium(addr_or_opts=co)
    # 创建 DrissionPage 实例，传入无头选项
    page = chrom.new_tab(
        rf'https://section.blog.naver.com/Search/Post.naver?pageNo=1&rangeType=PERIOD&orderBy=sim&startDate={start}&endDate={end}&keyword={key_word}')
    time.sleep(2)
    total_pages = int(page.ele('.search_number').text.replace('건', '').replace(',', ''))
    page_nums = int(total_pages / 7) + 1
    page.close()
    current = 0

    print(f'{key_word} 共有 {page_nums} 页')
    list = []
    while current <= page_nums:
        current += 1
        print(f'当前正在抓取 {key_word} 的 第{current}/{page_nums} 页数据')
        url = rf'https://section.blog.naver.com/Search/Post.naver?pageNo={current}&rangeType=PERIOD&orderBy=sim&startDate={start}&endDate={end}&keyword={key_word}'
        page = chrom.new_tab(url)
        html = page.ele('.area_list_search').html
        soup = BeautifulSoup(html, 'html.parser')

        dates = re.findall('<span class="date">(.*?)</span>', html)
        # texts = re.findall(r'<a class="text">(.*?)</a>', html)
        text_urls = re.findall('<a ng-href="(.*?)" class="desc_inner" ', html)
        blog_names = re.findall('<span class="name_blog">(.*?)</span>', html)
        author_names = re.findall('<em class="name_author">(.*?)</em>', html)

        # 查找所有 class="text" 的标签
        elements = soup.find_all(class_='author')
        author_urls = []
        for i, element in enumerate(elements):
            author_urls.append(re.search('href="(.*?)"', str(element)).group(1))

        texts = []
        elements = soup.find_all(class_='text')
        for i, element in enumerate(elements):
            texts.append(re.search('target="_blank">(.*?)</a>',
                                   str(element)
                                   .replace('<strong class="search_keyword">', '')
                                   .replace('</strong>', '')).group(1))

        titles = re.findall('<span class="title" ng-bind-html="post.title">(.*?)</span>', html)
        if len(titles) == len(texts):
            for i, title in enumerate(titles):
                title = str(titles[i].replace('<strong class="search_keyword">', '').replace('</strong>', ''))
                '''如果标题内包含关键词，则收录'''
                # or key_word.lower() in text.lower()
                result = {}
                if key_word.lower() in title.lower():
                    result['Keyword'] = key_word
                    result['title'] = title
                    result['url'] = text_urls[i]
                    result['text'] = texts[i]
                    result['Author1'] = author_names[i]
                    result['Name'] = blog_names[i]
                    result['author_url'] = author_urls[i]
                    if str(dates[i]).count('.') > 1:
                        result['createdAt'] = timeformat(dates[i])
                    list.append(result)
        else:
            print(f'抓取 {key_word} 的 第{current}页数据有问题')
            '''一般是抓取速度过快，抓点数据未加载完全导致，可适当调整睡眠时长'''

        time.sleep(3)
        chrom.close_tabs(chrom.get_tab(url=url))
    fields = ['Keyword', 'title', 'url', 'text', 'Author1', 'Name', 'author_url', 'createdAt']
    # 打开 CSV 文件（如果文件不存在会自动创建）
    with open(f"../tmp/naver_{key_word}_{start}_{end}采集.csv", mode="w", newline="", encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        # 写入表头
        writer.writeheader()
        # 写入数据
        writer.writerows(list)


def main():
    """
    执行前准备：
    起止时间 参数： start /end 格式：yyyy-MM-dd  闭区间 如2025-01-01 2025-01-07 则包括01 和 07 日期内的数据
    chrom（浏览器） 参数：co.headless(True) 若为True 则启动的浏览器后台执行，若为False 则浏览器正常运行可调试代码，定位bug时候使用
    port（端口）：不与其他程序冲突即可
    keyword（抓取关键词） ： 每个关键词为一个线程，所有关键词抓取完成后会写出每个关键词的csv文件和一个汇总（去重）的数据文件
    结果csv文件写在tmp文件夹里
    """

    start = '2025-02-12'
    end = '2025-02-18'

    threads = []
    port = 4482
    # 创建并启动线程
    for keyword in ['Binance', 'Bybit', 'Bitget', 'OKX', 'Gate.io', 'Mexc']:
        thread = threading.Thread(target=getdetails, args=(keyword, start, end, port))
        port += 1
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()
    csv_combine('naver_', f'../tmp/naver_{start}_{end}数据', ['title', 'Author1'])


if __name__ == '__main__':
    main()

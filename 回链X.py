import csv
import queue
import threading
import time
from datetime import datetime
from queue import Queue
from urllib.parse import urlparse, urlunparse

from DrissionPage import Chromium, ChromiumOptions

from util.datasplit import split_list

# 获取当前时间
now = datetime.now()
# 格式化时间
current_time = now.strftime("%m-%d")


# 解析数据函数
def parse_data(data_str):
    spt1 = "、" if "、" in data_str else ","
    # 分割字符串为各个部分
    parts = data_str.split(spt1)
    # 创建字典
    data_dict = {}
    for part in parts:
        spt = " "
        # 进一步分割每个部分，提取数字和对应的标签
        count, label = part.strip().split(spt, 1)
        # 将标签作为键，数字作为值并转换为整数
        data_dict[label[:4]] = int(count)
    return data_dict


def getdetails(urls: list, port: int, output: Queue):
    # 创建配置对象（默认从 ini 文件中读取配置）
    co = ChromiumOptions()
    co.headless(False)
    co.set_local_port(port)
    chrom = Chromium(addr_or_opts=co)
    result = []
    for line in urls:
        link = line.strip()

        try:
            parsed_url = urlparse(link)
            # 返回没有参数的 URL
            url = urlunparse(parsed_url._replace(query=''))
            # 以该配置创建页面对象
            page = chrom.new_tab()
            page.get(url)
            time.sleep(8)
            name = page.ele(
                'xpath://*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[2]').texts().__str__().split(
                "\\n")[0].replace('[\'', '')
            full_text = page.ele(
                'xpath://*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[1]/div').texts()
            t4 = ''
            try:
                t4 = page.ele(
                    '.css-175oi2r r-1kbdv8c r-18u37iz r-1oszu61 r-3qxfft r-n7gxbd r-2sztyj r-1efd50x r-5kkj8d r-h3s6tt r-1wtj0ep').attr(
                    'aria-label')
            except Exception as e:
                ''
            try:
                t4 = page.ele(
                    '.css-175oi2r r-1kbdv8c r-18u37iz r-1oszu61 r-3qxfft r-n7gxbd r-2sztyj r-1efd50x r-5kkj8d r-h3s6tt r-1wtj0ep r-1igl3o0 r-rull8r r-qklmqi').attr(
                    'aria-label')
            except Exception as e:
                ''
            dictData = parse_data(t4)
            view_count = dictData.get('views', dictData.get('次观看', dictData.get('view', '0')))
            reply_count = dictData.get('replies', dictData.get('回复', dictData.get('repl', '0')))
            retweet_count = dictData.get('reposts', dictData.get('次转帖', dictData.get('repo', '0')))
            favorite_count = dictData.get('likes', dictData.get('喜欢', dictData.get('like', '0')))
            print({'url': url, 'user/name': name, 'full_text': full_text, 'view_count': view_count,
                   'reply_count': reply_count, 'retweet_count': retweet_count, 'favorite_count': favorite_count})
            result.append({'url': url, 'user/name': name, 'full_text': full_text, 'view_count': view_count,
                           'reply_count': reply_count, 'retweet_count': retweet_count,
                           'favorite_count': favorite_count})
            page.close()
        except Exception as e:
            print(str(url) + '  失败')
            output.put([{'url': url, 'user/name': '有问题', 'full_text': '', 'view_count': '', 'reply_count': '',
                         'retweet_count': '', 'favorite_count': ''}])
    output.put(result)
    chrom.quit()


def main():
    '''
    回链链接放入 X.txt,执行可调整thread_num 参数，进行多线程抓取，抓取失败的可能是因为需要登陆，可设置睡眠时间登陆之后改回睡眠时长，重新启动程序。
    '''
    list = []
    # 逐行读取文件内容
    with open(r'D:\Users\bjc\DESK\pycharm\com.gateio.analysis\X.txt', 'r', encoding='utf-8') as file:
        for line in file:
            link = line.strip()
            list.append(link)
    print('读入全部X链接地址')

    port = 2500
    thread_num = 3
    # 数据切片（线程数量）
    sub_lists = split_list(list, thread_num)
    print('数据根据线程切片完成')

    # 创建线程列表
    output_queue = queue.Queue()
    threads = []
    for data in sub_lists:
        thread = threading.Thread(target=getdetails, args=(data, port, output_queue))
        port += 1
        threads.append(thread)
        thread.start()  # 启动线程

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    print('所有线程已完成，开始回收结果数据')
    # 收集所有返回值
    total_result = []
    while not output_queue.empty():
        total_result += output_queue.get()  # 从队列中获取结果

    # csv文件数据导出
    fields = ['url', 'user/name', 'full_text', 'view_count', 'reply_count', 'retweet_count', 'favorite_count']
    # 打开 CSV 文件（如果文件不存在会自动创建）
    with open(f"../tmp/X回链数据_{current_time}.csv", mode="w", newline="", encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        # 写入表头
        writer.writeheader()
        # 写入数据
        writer.writerows(total_result)


if __name__ == '__main__':
    main()

import csv
import queue
import threading
from datetime import datetime
from queue import Queue

from DrissionPage import Chromium, ChromiumOptions

from util.datasplit import split_list

# 获取当前时间
now = datetime.now()

# 格式化时间
current_time = now.strftime("%m-%d")

print("当前时间:", current_time)


def getdetails(urls: list, port: int, output: Queue):
    result = []
    co = ChromiumOptions()
    co.headless(True)
    co.set_local_port(port)
    # 以该配置创建页面对象
    chrom = Chromium(addr_or_opts=co)
    for i, url in enumerate(urls):
        url = url.strip()
        try:
            page = chrom.new_tab(url)
            name = page.ele(
                'xpath://*[@id="page-header"]/yt-page-header-renderer/yt-page-header-view-model/div/div[1]/div/yt-dynamic-text-view-model/h1/span').text
            result.append({'url': url, 'username': name})
            page.close()
        except Exception as e:
            output.put([{'url': url, 'username': '有问题'}])
    output.put(result)
    chrom.quit()


def main():
    port = 1204
    thread_num = 5
    # 逐行读取文件内容
    list = []
    with open(r'D:\Users\bjc\DESK\pycharm\com.gateio.analysis\youtube.txt', 'r', encoding='utf-8') as file:
        for line in file:
            url = line.strip()
            list.append(url)
    # 数据切片（线程数量）
    sub_lists = split_list(list, thread_num)

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
    print(total_result)
    # csv文件数据导出
    fields = ['url', 'username']
    # 打开 CSV 文件（如果文件不存在会自动创建）
    with open(f"../tmp/油管回链数据_{current_time}.csv", mode="w", newline="", encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        # 写入表头
        writer.writeheader()
        # 写入数据
        writer.writerows(total_result)


if __name__ == '__main__':
    main()

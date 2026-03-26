import json
import queue
import threading
import time
from datetime import datetime
from queue import Queue
from DrissionPage import Chromium,ChromiumOptions
from util.datasplit import split_list
from util.jdbc import jdbc

# 获取当前时间
now = datetime.now()
# 格式化时间
current_time = now.strftime("%m-%d")
print("当前时间:", current_time)

def getdetails(urls:list,port:int,output:Queue):
    co = ChromiumOptions()
    co.headless(False)
    co.set_local_port(port)
    chrom = Chromium(addr_or_opts=co)
    output_result = []
    for url in urls:
            try:
                page = chrom.new_tab()
                page.get(url)
                try:
                    page.ele(' 好的 ').click()
                except Exception as e:
                    ''
                time.sleep(8)
                jsontext = page.ele('xpath://*[@id="app"]').next().next().html.__str__().replace(
                    '<script>window.__INITIAL_STATE__=', '').replace('</script>', '').replace('undefined', '""')
                note = json.loads(jsontext)['note']
                note_id = note['firstNoteId']
                note_detail = note['noteDetailMap'][note_id]['note']
                interact = note_detail['interactInfo']
                ip_location = note_detail.get('ipLocation', 'Unknown')
                type = note_detail['type']
                text = note_detail['desc']
                user_detail = note_detail['user']
                update_time = str(note_detail['lastUpdateTime']).replace('\'', '')
                first = str(note_detail['time']).replace('\'', '')
                title = note_detail['title']
                tags = note_detail.get('tagList', 'Unknown')
                # 使用列表推导式提取所有 name 的值
                author_avatar = user_detail['avatar']
                author_userId = user_detail['userId']
                author_nickname = user_detail['nickname']
                likedCount = interact.get('likedCount', '0')
                collectedCount = interact.get('collectedCount', '0')
                commentCount = interact.get('commentCount', '0')
                shareCount = interact.get('shareCount', '0')

                result = {}
                tag_list = [item['name'] for item in tags]
                result['url'] = url
                result['note_id'] = note_id
                result['author_avatar'] = author_avatar
                result['author_userId'] = author_userId
                result['author_nickname'] = author_nickname
                result['type'] = type
                result['tag_list'] = str(tag_list)
                result['title'] = title
                result['text'] = text
                result['ip_location'] = ip_location
                result['first_time'] = first
                result['update_time'] = update_time
                result['likedCount'] = likedCount
                result['collectedCount'] = collectedCount
                result['commentCount'] = commentCount
                result['shareCount'] = shareCount
                print(result)
                output_result.append(result)
                chrom.close_tabs(chrom.get_tab(url=url))
            except Exception as e:
                print(f'有问题： {url}')
    output.put(output_result)
    chrom.quit()
def main():
    port = 9990
    thread_num=2
    list = []

    # 打开小红书搜索页面，添加你想要搜索的关键词
    with open(rf'D:\Users\bjc\DESK\pycharm\com.gateio.analysis\xhs.txt', 'r', encoding='utf-8') as file:
        for line in file:
            "若回链数据链接格式有问题在这里统一处理"
            # url = line.split('- 小红书 ')[1].strip()
            # # 解析URL
            # parsed_url = urlparse(url)
            # # 获取查询参数
            # query_params = parse_qs(parsed_url.query)
            # # 只保留xsec_token参数
            # filtered_params = {key: value for key, value in query_params.items() if key == 'xsec_token'}
            # # 重构URL
            # new_query_string = urlencode(filtered_params, doseq=True)
            # url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{new_query_string}"+"&xsec_source="
            list.append(line)

    #数据切片（线程数量）
    sub_lists = split_list(list,thread_num)

    # 创建线程列表
    output_queue = queue.Queue()
    threads = []
    for data in sub_lists:
        thread = threading.Thread(target=getdetails, args=(data, port,output_queue))
        port +=1
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

    db = jdbc()
    insert_query = '''
        INSERT INTO spider.xhs
        (url, note_id, author_avatar, author_userId, author_nickname, `type`, tag_list, title, `text`, ip_location, first_time, update_time, likedCount, collectedCount, commentCount, shareCount)
            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s);
            '''
    for i, data in enumerate(total_result):
        values = (f'{data['url']}', f'{data['note_id']}', f'{data['author_avatar']}', f'{data['author_userId']}', f'{data['author_nickname']}', f'{data['type']}',
                  f'{data['tag_list'].replace("'", "")}', f'{data['title']}', f'{data['text']}', f'{data['ip_location']}', int(data['first_time']),
                  int(data['update_time']), int(data['likedCount']), int(data['collectedCount']), int(data['commentCount']), int(data['shareCount']))
        db.insert(insert_query, values)
    db.close()


if __name__ == '__main__':
    main()
    # '输出结果是有哪些地址未抓取入库'
    # list1 = []
    # with open(rf'D:\Users\bjc\DESK\pycharm\com.gateio.analysis\xhs.txt', 'r', encoding='utf-8') as file:
    #     for line in file:
    #         url = line.strip()
    #         # 解析URL
    #         parsed_url = urlparse(url)
    #
    #         # 获取查询参数
    #         query_params = parse_qs(parsed_url.query)
    #
    #         # 只保留xsec_token参数
    #         filtered_params = {key: value for key, value in query_params.items() if key == 'xsec_token'}
    #
    #         # 重构URL
    #         new_query_string = urlencode(filtered_params, doseq=True)
    #         url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{new_query_string}" + "&xsec_source="
    #         list1.append(url)
    # print(list1)
    #
    # list2 = []
    # db = jdbc()
    # select_query = "SELECT url FROM spider.xhs"
    # users = db.read(select_query)
    # for user in users:
    #     list2.append(user[0])
    # print(list2)
    #
    # # 这是 list1 中有但 list2 中没有的字符串
    # difference = list(set(list1) - set(list2))
    #
    # for i, e in enumerate(difference):
    #     print(e)
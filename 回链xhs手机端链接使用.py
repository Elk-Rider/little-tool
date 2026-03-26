import json
import threading
import time
from datetime import datetime

from DrissionPage import Chromium, ChromiumOptions

from util.datasplit import split_list
from util.jdbc import jdbc

# 获取当前时间
now = datetime.now()
# 格式化时间
current_time = now.strftime("%m-%d")


def getdetails(urls: list, port: int):
    # 创建配置对象（默认从 ini 文件中读取配置）
    co = ChromiumOptions()
    co.headless(True)
    co.set_local_port(port)
    chrom = Chromium(addr_or_opts=co)
    result = []
    for link in urls:
        url = link.strip()
        try:
            page = chrom.new_tab()
            page.get(url)
            time.sleep(10)
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
            db = jdbc()
            insert_query = '''
            INSERT INTO spider.xhs
            (url, note_id, author_avatar, author_userId, author_nickname, `type`, tag_list, title, `text`, ip_location, first_time, update_time, likedCount, collectedCount, commentCount, shareCount)
                VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s);
                '''
            values = (
            f'{result['url']}', f'{result['note_id']}', f'{result['author_avatar']}', f'{result['author_userId']}',
            f'{result['author_nickname']}', f'{result['type']}',
            f'{result['tag_list'].replace("'", "")}', f'{result['title']}', f'{result['text']}',
            f'{result['ip_location']}', int(result['first_time']),
            int(result['update_time']), int(result['likedCount']), int(result['collectedCount']),
            int(result['commentCount']), int(result['shareCount']))
            db.insert(insert_query, values)
            db.close()
            page.close()
        except Exception as e:
            print(str(url) + '  失败')
    chrom.quit()


def main():
    "回链地址很少部分文章可能需要进行登陆抓取，正常情况下，有问题的地址多，程序抓两次，若少则手动处理"
    list = []
    port = 5000
    thread_num = 1
    # 打开小红书搜索页面，添加你想要搜索的关键词
    with open(rf'D:\Users\bjc\DESK\pycharm\com.gateio.analysis\xhs.txt', 'r', encoding='utf-8') as file:
        for line in file:
            list.append(line)

    # 数据切片（线程数量）
    sub_lists = split_list(list, thread_num)

    threads = []
    for data in sub_lists:
        thread = threading.Thread(target=getdetails, args=(data, port))
        port += 1
        threads.append(thread)
        thread.start()  # 启动线程

    # 等待所有线程完成
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()

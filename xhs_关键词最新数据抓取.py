import json
import re
import threading
import time

from DrissionPage import Chromium
from loguru import logger

from util.jdbc import jdbc


def getdetails(key: str, nums: int,port:int):
    # 初始化 Drission 对象，设置浏览器为 Chrome
    chrom = Chromium(port)
    # 打开小红书搜索页面，添加你想要搜索的关键词
    url = f'https://www.xiaohongshu.com/explore'
    page = chrom.new_tab(url)
    '搜索关键词，时间降序'
    page.ele(".search-input").input(f'{key}\n')
    #扫码登陆可从此延长睡眠时间 3改成3000，登陆之后会自动保存，改成3s后正常执行即可
    time.sleep(3)
    page.ele("综合").hover()
    time.sleep(2)
    page.ele("最新").click()
    logger.info(f'搜索关键词{key}，最新排序')

    '采集文章链接列表，用于后续使用'
    urls = []
    count = 0
    while count < nums:
        for i, html in enumerate(page.eles('.cover ld mask')):
            # 使用正则表达式提取href的值
            match = re.search(r'search_result//?([^\'" >]+)', str(html))
            if match:
                href_value = match.group(1)
                url = 'https://www.xiaohongshu.com/explore/' + href_value
                urls.append(url)
            else:
                print("没有找到href值" + str(html))
        current = len(list(set(urls)))
        if count == current: break
        count = current
        page.ele("加载中").click()
        page.ele("加载中").click()
        time.sleep(3)

    '遍历链接开始采集文章数据'
    real_urls = list(set(urls))
    total = len(real_urls)
    logger.info(f'共获得{total}条文章列表，后续进行细节数据抓取')
    for i, url in enumerate(real_urls):
        try:
            total -= 1
            page = chrom.new_tab(url)
            try:
                page.ele(' 好的 ').click()
            except Exception as e:
                ''
            time.sleep(3)

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
            db = jdbc()
            insert_query = ''' 
                INSERT INTO spider.xhs 
                (key_word ,url, note_id, author_avatar, author_userId, author_nickname, `type`, tag_list, title, `text`, ip_location, first_time, update_time, likedCount, collectedCount, commentCount, shareCount) 
                    VALUES ( %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s);  
                    '''
            values = (
                f'{key}', f'{url}', f'{note_id}', f'{author_avatar}', f'{author_userId}', f'{author_nickname}',
                f'{type}',
                f'{result['tag_list'].replace("'", "")}', f'{title}', f'{text}', f'{ip_location}', int(first),
                int(update_time), int(likedCount), int(collectedCount), int(commentCount), int(shareCount))
            db.insert(insert_query, values)
            logger.info(f' 已完成 {i + 1} 剩余 {total} \n {result} ')
            chrom.close_tabs(chrom.get_tab(url=url))
            db.close()
        except Exception as e:
            logger.error(f'该url无法抓取  {url}')


def main():
    """
    程序执行逻辑： 打开小红书web网站，等待扫码登陆，搜索关键词，综合改为最新排序，向下滑动获得每篇文章的链接，遍历链接抓取文章数据，数据入库

    每个关键词一个浏览器端口，执行之前需要进行调长睡眠时间扫码登陆，后续调回正常睡眠时长进行数据抓取。
     通过关键词进行搜索，每个关键词抓取的最新数据条数 110 ，可自行更改
     端口号不冲突即可，但如果已经登陆了则下次执行不需要改端口，否则需要重新登陆
    """
    port = 9990
    # 创建线程列表
    threads = []
    for i in ['bitget','mexc','okx']:
        thread = threading.Thread(target=getdetails, args=(i, 110, port))
        port += 1
        threads.append(thread)
        thread.start()  # 启动 线程

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    print("All threads have finished.")


if __name__ == '__main__':
    main()

import time

import pymysql as mysql
from telethon import TelegramClient, events

insert_sql = ''' INSERT INTO media_crawler.tg_groups_message(group_name,group_id,author, massage_time,store_time, massage) VALUES (%s,%s, %s,%s, %s,%s)'''


class jdbc:
    def __init__(self):
        # """初始化数据库连接."""
        self.connection = None
        self.cursor = None
        try:
            self.connection = mysql.connect(
                host='209.97.170.156',
                user='root',
                password='123456',
                database='media_crawler',
                port=3307,
                autocommit=True,
            )
            self.cursor = self.connection.cursor()
        except Exception as e:
            print(f"连接数据库时发生错误: {e}")

    def insert(self, query, data):
        """插入新记录."""
        try:
            self.cursor.execute(query, data)
            self.connection.commit()
        except mysql.MySQLError as e:
            print(f"MySQL 错误: {e.args[0]} - {e.args[1]}")
        except Exception as e:
            print(f"插入记录时发生错误: {e}")

    def close(self):
        """关闭连接."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


name_id = {
    '-1001136071376': '币安官方中文群',
    '-1001472527446': 'Bitget海外华语社区',
    '-1001872223162': 'Bitget English Official',
    '-1001488659293': 'MEXC English (Official)',
    '-1001890976631': 'Gate官方中文群',
    '-1001573618691': 'Gate.io Exchange',
    '-1001453035653': 'Bybit English',
    '-1001146170349': 'Binance English',
    '-1001450606717': 'OKX English',
    '-1001282851157': '火币HTX官方中文群',
    '-1001713223404': 'MEXC華語交流群'
}

GROUPS = [
    'gateio_en',
    'gate_zh',
    'MEXCEnglish',
    'MEXC_ZH',
    'BybitZH',
    'BybitEnglish',
    'BinanceChinese',
    'binanceexchange',
    'Bitget_CNOfficial',
    'BitgetENOfficial',
    'OKXOfficial_English',
    'HTX_Chineseofficial'
]

# Telegram API ID 和 API Hash
api_id = 25123790
api_hash = '9f42192d6604fed71704e271641533ac'
# 创建 Telegram 客户端
client = TelegramClient('./session_name', api_id, api_hash)


# 监听第二个群组的消息
@client.on(events.NewMessage(chats=GROUPS))
async def handler(event):
    # 如果消息来自目标群组
    chat_id = event.chat_id
    chat_name = name_id.get(str(chat_id), 'UnKnown')

    sender_id = event.sender_id  # 发送者 ID
    message_text = event.text  # 消息内容
    message_time = int(event.date.timestamp())  # 消息发送时间
    if message_text != '':
        print(f"{chat_name} {chat_id} (Sender: {sender_id}) at {message_time}:  {message_text}")
        # 将消息信息插入到 MySQL 数据库
        conn = jdbc()
        conn.insert(insert_sql, (
            f'{chat_name}', f'{chat_id}', f'{sender_id}', message_time * 1000, int(time.time()) * 1000,
            f'{message_text}'))
        conn.close()


# 主程序
def main():
    print('启动tg爬虫')
    # 启动客户端
    client.start('+852 94510480', '100200')
    print('正在启动客户端')
    client.run_until_disconnected()


if __name__ == '__main__':
    """
    目前程序稳定，部署的文件在服务器的/opt/module/tg_data下
    建议：
    写库方式可以改为连接池，效率更高，
    数据库的数据量最好不超过500W条，定期删除数据（手动也可）
    """
    main()

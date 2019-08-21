# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    :    
# @Author  : SongZhiBin


import requests
from mobile_app.settings import M_LIST_INFO, CYCLE_TIME
from pyquery import PyQuery as pq
import time


class Monitoring_jiandanwang():
    """
    动态获取煎蛋网新闻及其链接存储至MongoDB
    """

    def __init__(self):
        self.m_list_collection = M_LIST_INFO
        self.get_url = "http://jandan.net/"
        self.language_code = 'utf-8'

    def get_jiandan(self):
        """
        爬取煎蛋网首页返回html
        :return:
        """
        response = requests.get(self.get_url)
        response.encoding = self.language_code
        print("抓取完毕")
        return response.text

    def analyze_html(self, html):
        """
        分析html 进行数据打包 并调用self.save_mongodb进行数据保存
        :param html:
        :return:
        """
        doc = pq(html)
        div = doc(".post.f.list-post").items()
        print("开始解析数据")
        for item in div:
            try:
                data = {}
                data['path_url'] = item.find(".thumbs a").attr('href')
                image_url = item.find(".thumbs a img").attr("src") if item.find(".thumbs a img").attr(
                    "src") else item.find(
                    ".thumbs a img").attr("data-original")
                data['image_url'] = f'http:{image_url}'
                data["title"] = item.find(".indexs h2").text()
                data['author'] = item.find(".indexs .time_s a").text().split(' ')[0]
                data['album'] = item.find(".indexs .time_s strong a").text()
                data['content'] = item.find(".indexs").text().rsplit('\n', 1)[1]
                data['time'] = time.time()
                self.save_mongodb(data)
                print("已完成")

            except Exception as e:
                print(e)
                continue

    def save_mongodb(self, data):
        """
        存储至MongoDB中
        :param data:
        :return:
        """
        print("开始保存")
        self.m_list_collection.update_one({"title": data['title']}, {'$set': data}, True)

    def main(self):
        """
        流程函数
        先调用 self.get_jiandan() 获取煎蛋网 html
        在调用 self.analyze_html() 进行数据清洗 将数据打包并保存

        :return:
        """
        while 1:
            try:
                html = self.get_jiandan()
                self.analyze_html(html)
            except Exception as e:
                print(e)
                continue
            finally:
                time.sleep(CYCLE_TIME)


if __name__ == "__main__":
    Mj = Monitoring_jiandanwang()
    Mj.main()

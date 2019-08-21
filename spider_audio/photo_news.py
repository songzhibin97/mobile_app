# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    :    
# @Author  : SongZhiBin


import requests
from mobile_app.settings import PHOTO_INFO, CYCLE_TIME
from pyquery import PyQuery as pq
import time


class Monitoring_photo_news():
    """
    动态获取图片新闻及其链接存储至MongoDB
    """

    def __init__(self):
        self.photo_news_collection = PHOTO_INFO
        self.get_url = "http://picture.youth.cn/"
        self.language_code = 'utf-8'

    def get_news(self):
        """
        爬取图片新闻首页返回html
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
        li = doc(".banner.clearfix ul li").items()
        print("开始解析数据")
        for item in li:
            try:
                data = {}
                data['path_url'] = f"http:{item.find('a').attr('href')}"
                data["image_url"] = f"http:{item.find('a img').attr('src')}"
                data["message"] = item.find('a+div h3 a').text()
                data["time"] = time.time()
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
        self.photo_news_collection.update_one({"path_url": data["path_url"]}, {"$set": data}, True)

    def main(self):
        """
        流程函数
        先调用 self.get_news() 获取图片新闻 html
        在调用 self.analyze_html() 进行数据清洗 将数据打包并保存
        :return:
        """
        while 1:
            try:
                html = self.get_news()
                self.analyze_html(html)
            except Exception as e:
                print(e)
                continue
            finally:
                time.sleep(CYCLE_TIME)


if __name__ == '__main__':
    Mp = Monitoring_photo_news()
    Mp.main()

# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    :    
# @Author  : SongZhiBin


"""
喜马拉雅获取音频 url = https://m.ximalaya.com/tracks/音频id.json 获取对应信息
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import pymongo
import time


class Ximalaya():
    def __init__(self):
        self.driver = webdriver.Chrome()  # 初始化浏览器对象
        self.wait = WebDriverWait(self.driver, 10)  # 初始化浏览器等待时间
        self.store_list_url = []  # 存储故事专辑url
        self.nursery_rhyme_list_url = []  # 存储儿歌专辑url
        self.total_page = None  # 获取当前页最大页码数
        self.client = pymongo.MongoClient(host='localhost', port=27017)  # 初始化mangodb客户端
        self.db = self.client.ximalaya  # 连接mongodb ximalaya db
        self.stores_collection = self.db.stores  # 故事儿歌id表

    def get_store_free(self):
        """
        通过selenium自动化访问至 https://www.ximalaya.com/ertong/ 喜马拉雅儿童栏后
        进行自动化筛选 选中 故事栏以及免费
        :return:
        """
        self.driver.get("https://www.ximalaya.com/ertong/")
        try:
            # 筛选 免费以及故事频道
            story = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="root"]/main/section/div/div/div[2]/div/div/div[2]/div[1]/div[2]/a[1]')))
            story.click()
            self.wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="root"]/main/section/div/div/div[2]/div/div/div[3]/div[1]')))
            free = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="root"]/main/section/div/div/div[2]/div/div/div[2]/div[3]/div[2]/a[2]')))
            free.click()
        except Exception as e:
            print("点击筛选标签失败")

    def get_nursery_rhyme_free(self):
        """
        通过selenium自动化访问至 https://www.ximalaya.com/ertong/ 喜马拉雅儿童栏后
        进行自动化筛选 选中 儿歌栏以及免费
        :return:
        """
        self.driver.get("https://www.ximalaya.com/ertong/")
        try:
            # 筛选 免费以及故事频道
            nursery_rhyme = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="root"]/main/section/div/div/div[2]/div/div/div[2]/div[1]/div[2]/a[2]')))
            nursery_rhyme.click()
            self.wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="root"]/main/section/div/div/div[2]/div/div/div[3]/div[1]')))
            free = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="root"]/main/section/div/div/div[2]/div/div/div[2]/div[3]/div[2]/a[2]')))
            free.click()
        except Exception as e:
            print("点击筛选标签失败")

    def data_processing(self, append_list):
        """
        获取当前页面的html进行pyquery进行分析后 将专辑url存储至 self.store_list_url中 以便于爬取具体
        :return:
        """
        # 获得故事频道免费页面的html
        html = self.driver.page_source
        doc = pq(html)
        lis = doc.find(".content ul li").items()
        for li in lis:
            try:
                href = li.find('a').attr('href')
                audio_url = "https://www.ximalaya.com" + href
                append_list.append(audio_url)
            except Exception as e:
                print(e)

    def get_page(self):
        """
        获取总页码 并保存在self.total_page 中
        需要注意 默认self.total_page为None
        需要先调用此方法后才能执行 self.next_page()进行翻页操作
        :return:
        """
        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.pagination-page')))
            print('我还没报错')
            html = self.driver.page_source
            doc = pq(html)
            ret = doc.find(
                '#root > main > section > div > div > div.layout-main._80 > div.category-filter-result-wrap._80 > div > div.pagination-wrap > nav > ul > li:nth-child(7) > a > span').text()
            self.total_page = int(ret)
        except Exception as e:
            print(e)

    def next_page(self, append_list):
        """
        翻页 需要先调用self.get_page()获取页码后进行翻页操作
        :param append_list: # 用于区分保存 self.store_list_url or self.nursery_rhyme_list_url
        :return:
        """
        try:
            for i in range(2, self.total_page + 1):
                time.sleep(1)
                try:
                    input_page = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.control-input')))
                    input_page.clear()
                    input_page.send_keys(i)
                    sure_botton = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.btn')))
                    sure_botton.click()
                    self.data_processing(append_list)
                except Exception as e:
                    sure_botton = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.btn')))
                    sure_botton.click()
                    self.data_processing(append_list)
                    print(e)
        except Exception as e:
            self.next_page(append_list)
            print(e)

    def get_store_list(self):
        """
        类似一个main方法 用于调用全流程获取 故事 免费 所有专辑url并返回
        :return:
        """
        self.get_store_free()
        self.get_page()
        self.next_page(self.store_list_url)
        return self.store_list_url

    def get_nursery_rhyme_list(self):
        """
        类似一个main方法 用于调用全流程获取 儿歌 免费 所有专辑url并返回
        :return:
        """
        self.get_nursery_rhyme_free()
        self.get_page()
        self.next_page(self.nursery_rhyme_list_url)
        return self.nursery_rhyme_list_url

    def get_audio(self):
        """

        :return:
        """
        # TODO 需要实现分别从 self.store_list_url / self.nursery_rhyme_list_url 进行深一步挖掘
        #  获取具体音频id 进行拼接后 存入mangodb中保存url 以及分类
        #  在利用requests模块进行分布式爬取 获取音频信息以及其他信息进行存储

        pass

    # https://www.ximalaya.com/ertong/23800597/
    def save_audio_id(self, url_list, label):
        """
        循环 self.store_list_url 或 self.nursery_rhyme_list_url 来获取保存audio id 至 mangodb中
        :return:
        """
        try:
            for url in url_list:
                p = 1
                self.driver.get(url)
                self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="anchor_sound_list"]/div[2]')))
                html = self.driver.page_source
                doc = pq(html)
                current_page_url = doc.find("#anchor_sound_list .sound-list li").items()
                try:
                    for audio in current_page_url:
                        audio_info = audio.find('a').attr("href")
                        audio_id = audio_info.split('/')[3]
                        if not len(audio_id) < 8:
                            data = {
                                "audio_id": audio_id,
                                "label": label
                            }
                            self.stores_collection.update_many({"audio_id": audio_id}, {'$set': data}, True)
                except Exception as e:
                    print(e)
                    pass
                while doc.find('.page-next'):
                    p += 1
                    self.driver.get(url + 'p%s/' % p)
                    try:
                        self.wait.until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="anchor_sound_list"]/div[2]')))

                        html = self.driver.page_source
                        doc = pq(html)
                        current_page_url = doc.find("#anchor_sound_list .sound-list li").items()
                    except Exception as e:
                        print(e)
                    try:
                        for audio in current_page_url:
                            audio_info = audio.find('a').attr("href")
                            audio_id = audio_info.split('/')[3]
                            if not len(audio_id) < 8:
                                data = {
                                    "audio_id": audio_id,
                                    "label": label
                                }
                                self.stores_collection.update_many({"audio_id": audio_id}, {'$set': data}, True)
                    except Exception as e:
                        print(e)
                        pass

        except Exception as e:
            print(e)
            pass


if __name__ == "__main__":
    pass

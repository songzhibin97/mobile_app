# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    :
# @Author  : SongZhiBin


import pymongo
import uuid
import requests
import os
import asyncio
from aiohttp import ClientSession
from aiohttp import TCPConnector
import json

"""
喜马拉雅获取音频 url = https://m.ximalaya.com/tracks/音频id.json 获取对应信息
"""


class Get_audio():

    def __init__(self):
        """
        初始化
        """
        self.client = pymongo.MongoClient(host='203.195.171.208', port=27017)  # 初始化mangodb客户端
        self.db = self.client.ximalaya  # 连接mongodb ximalaya db
        self.stores_collection = self.db.stores  # 故事儿歌id表
        self.stores_info_collection = self.db.stores_info  # 故事详细表
        self.nursery_rhymes_info_collection = self.db.nursery_rhymes_info  # 儿歌详细表
        self.path_name = None

    def get_audio_name(self):
        """
        随机获得audio_name以便于保存文件
        :return:
        """
        return str(uuid.uuid4())

    def find_mongodb(self, label):
        """
        通过label获取在mongodb中已存 audio_id 并返回
        :param label: mongodb存储audio分类
        :return:
        """
        ret = self.stores_collection.find({'label': label}, {"_id": 0, "label": 0})
        return ret

    def get_json_audio_info_path(self, audio_id):
        """
        进行url拼接
        喜马拉雅获取音频 url = https://m.ximalaya.com/tracks/音频id.json 获取对应信息
        :param audio_id:
        :return:
        """
        get_json_url = "https://m.ximalaya.com/tracks/%s.json" % audio_id
        return get_json_url

    async def requests_url(self, url):
        """
        进行请求访问获取json数据提取有用信息进行打包返回
        title 音频name
        nickname 专辑
        play_path 音频下载地址
        intro 故事简介
        :param url:
        :return:
        """
        async with ClientSession(connector=TCPConnector(verify_ssl=False)) as session:
            async with session.get(url) as response:
                response = await response.read()
                new_response = json.loads(response.decode('utf-8'))

                data = {
                    "title": new_response.get("title"),
                    "nickname": new_response.get("nickname"),
                    "play_path": new_response.get('play_path'),
                    'intro': new_response.get('intro'),
                    "cover_url": new_response.get("cover_url")
                }
                return data

    async def download_audio(self, path, url):
        """
        异步下载音频文件
        :param path:
        :param url:
        :return:
        """
        async with ClientSession(connector=TCPConnector(verify_ssl=False)) as session:
            async with session.get(url) as response:
                response = await response.read()
                print("正在下载音频", url)
                with open(path, 'wb') as f:
                    f.write(response)
                print("下载成功成功")

    async def download_image(self, path, url):
        """
        异步下载图片文件
        :param path:
        :param url:
        :return:
        """
        async with ClientSession(connector=TCPConnector(verify_ssl=False)) as session:
            async with session.get(url) as response:
                response = await response.read()
                print("正在下载图片", url)
                with open(path, 'wb') as f:
                    f.write(response)
                print("图片下载成功")

    def save_mongodb(self, data, label):
        if label == "故事":
            self.stores_info_collection.update_many({"title": data.get('title')}, {'$set': data}, True)
            print("故事插入成功或更新成功")
        elif label == "儿歌":
            self.nursery_rhymes_info_collection.update_many({"title": data.get('title')}, {'$set': data}, True)
            print("儿歌插入成功或更新成功")

    def main(self, label):
        """
        主文件 用于调用self中其他函数完成一系列操作
        :param label:
        :return:
        """
        if label == '故事':
            self.path_name = 'story'
        if label == '儿歌':
            self.path_name = 'nursery_rhyme'

        # 通过label获取已存储mongodb中的相关数据们
        audio_ids = self.find_mongodb(label)
        # 遍历 .get("audio_id") 获取audio_id

        for audio_id in audio_ids:
            try:
                # 进行拼接后拿到url
                audio_url = self.get_json_audio_info_path(audio_id.get('audio_id'))
                # 获取保存audio文件name
                audio_name = self.get_audio_name()
                # 利用requests获取data字典
                data = loop.run_until_complete(self.requests_url(audio_url))
                data['audio_name'] = audio_name
                # local_path = os.path.join('mobile_app','spider_audio',"audios",f'{self.path_name,audio_name}.mp3')
                # local_image_path = os.path.join('mobile_app','spider_audio',"audios",f'{self.path_name,audio_name}_image.jpg')
                # download_path = os.path.join(os.getcwd(),"audios",self.path_name,f'{audio_name}.mp3')
                # download_image_path = os.path.join(os.getcwd(),"audios","images",f'{audio_name}_image.jpg')
                # data['local_path'] = local_path
                # data['local_image_path'] = local_image_path
                self.save_mongodb(data, label)
                # # # 异步下载
                # loop.run_until_complete(self.download_audio(download_path, data.get("play_path")))
                # loop.run_until_complete(self.download_image(download_image_path, data.get("cover_url")))
            except Exception as e:
                print(e)
                continue


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    audio = Get_audio()
    audio.main("故事")

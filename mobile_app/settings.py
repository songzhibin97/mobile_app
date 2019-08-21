# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    :    
# @Author  : SongZhiBin

import pymongo
import os

# ================ MongoDB相关 ==============
CILENT = pymongo.MongoClient(host='203.195.171.208', port=27017)
LOGIN_DB = CILENT.Mobile_APP
XIMALAYA_DB = CILENT.ximalaya
OR_DB = CILENT.OR

LOGIN_COLLENTION = LOGIN_DB.User_Info  # 存放用户信息DB
M_LIST_INFO = LOGIN_DB.M_list_info  # 存放爬取煎蛋网数据DB
PHOTO_INFO = LOGIN_DB.Photo_news  # 存放图片新闻数据DB

CHATS_COLLENTION = LOGIN_DB.chats  # 存放聊天标识id
TOY_INFO = LOGIN_DB.toy_info  # 存放每个app详细情况

XIMALAYA_STORES_INFO = XIMALAYA_DB.stores_info  # 存放故事info
XIMALAYA_NURSERY_RHYMES_INFO = XIMALAYA_DB.nursery_rhymes_info  # 存放儿歌info

OR_COLLENTION = OR_DB.Or  # 存放玩具二维码


UNREAD_MESSAGE_COLLENTION = LOGIN_DB.Unread_message  # 存放未读消息

REQUEST_FRIEND_COLLENTION = LOGIN_DB.Request_friend  # 存放好友申请

MOBILE_APP_PATH = os.path.dirname(__file__)  # /Users/songzhibin/pycharm_program/mobile_app/mobile_app

# ================ 循环周期相关 ==================
CYCLE_TIME = 3600  # 单位s

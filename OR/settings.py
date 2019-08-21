# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    :    
# @Author  : SongZhiBin


import pymongo
import os


# ================= SETTING ===================
GET_OR_URL = "http://qr.liantu.com/api.php?text="
LOGO_URL = "https://gss0.baidu.com/94o3dSag_xI4khGko9WTAnF6hhy/zhidao/pic/item/8b13632762d0f70349c9e70e06fa513d2797c5ed.jpg"

# =============== MongoDB ===============
CILENT = pymongo.MongoClient(host='203.195.171.208', port=27017)
OR_DB = CILENT.OR
OR_COLLENTION = OR_DB.Or

OR_PATH = os.path.dirname(__file__)

# ================ PATH ===============
LOCAL_PATH = os.getcwd()
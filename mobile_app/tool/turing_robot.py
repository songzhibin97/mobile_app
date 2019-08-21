# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    :    
# @Author  : SongZhiBin


import requests
import json


class TuringRobot():
    def __init__(self):
        self.apiKey = 'f52690ee3f2c4b559b6de7ea6c0f79c7'
        self.get_url = 'http://openapi.tuling123.com/openapi/api/v2'
        self.error_code = [5000, 6000, 4000, 4001, 4002, 4003, 4005, 4007, 4100, 4200, 4300, 4400, 4500, 4600, 4602,
                           7002, 8008, 0]

    def post(self, message):
        """
        图灵接口
        :param message:
        :return:
        """
        req_dic = {
            "reqType": 0,
            "perception": {
                "inputText": {
                    "text": message
                },
            },
            "userInfo": {
                "apiKey": self.apiKey,
                "userId": "bin"
            }
        }
        ret = requests.post(url=self.get_url, json=req_dic)
        try:
            data = json.loads(ret.content.decode('utf-8'))
            if data.get('intent').get('code') not in self.error_code:
                response_mes = data.get("results")[0].get('values').get('text')
                return response_mes
            return None
        except Exception as e:
            print(e)
            return None

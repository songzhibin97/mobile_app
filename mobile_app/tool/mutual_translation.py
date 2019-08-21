# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    :    
# @Author  : SongZhiBin


from aip import AipSpeech
import uuid
import os
import json
from hashlib import md5
import time


class MutualTranslation:
    """
    借助百度AI开放平台实现音频转化文字以及文字转化音频功能
    """

    def __init__(self):
        self.APP_ID = '16726431'
        self.API_KEY = 'ZKUYeHypMb21m0ksREhSQL3K'
        self.SECRET_KEY = '2ifgwfZQ83rzht5SogSIwevOiTvF9OqH'
        self.client = AipSpeech(self.APP_ID, self.API_KEY, self.SECRET_KEY)

    def get_file_content(self, filePath):
        """
        读目标文件
        :param filePath:
        :return:
        """
        with open(filePath, 'rb') as fp:
            return fp.read()

    def transcoding(self, filename):
        """
        进行录制音频m4a转化为pcm格式
        :param filename:
        :return:
        """
        os.system("ffmpeg -y -i {0} -acodec pcm_s16le -f s16le -ac 1 -ar 16000 {0}.pcm".format(filename))
        return filename + '.pcm'

    def audio_text(self, filePath):
        """
        音频转化为文字
        :param filePath:  音频文件
        :return:
        """
        # 识别本地文件
        ret = self.client.asr(self.get_file_content(filePath), 'pcm', 16000, {
            'dev_pid': 1536,
        })
        if ret.get('err_no') == 0:
            result = ret.get('result')
            return result
        else:
            error_mess = ret.get('data empty')
            print(error_mess)
            return error_mess

    def text_audio(self, save_path, text, vol=5, per=4, pit=8, spd=4):
        """
        文字转化为音频文件

        :param text: 合成文字
        :param vol: 音量
        :param per: 度丫丫发音
        :param pit: 语调
        :param spd: 语速
        :return:
        """
        result = self.client.synthesis(text, 'zh', 1, {
            'vol': vol, 'per': per, "pit": pit, 'spd': spd
        })

        # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
        if not isinstance(result, dict):
            id = md5(f"{uuid.uuid4()}{time.time()}{uuid.uuid4()}".encode("utf-8")).hexdigest()
            with open(f'{save_path}/{id}.mp3', 'wb') as f:
                f.write(result)
            # os.system(f'open {save_path}/{id}.mp3')
            return json.dumps(id+'.mp3')
        return None

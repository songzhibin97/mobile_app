# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    :    
# @Author  : SongZhiBin


import requests
import uuid
from hashlib import md5
import time
import os
from settings import OR_COLLENTION, GET_OR_URL, LOGO_URL, LOCAL_PATH


def create_or(num):
    """
    批量生成玩具二维码
    :param num:
    :return:
    """
    insert_list = []
    try:
        for n in range(num):
            try:
                secret_key = md5(f"{uuid.uuid4()}{time.time()}{uuid.uuid4()}".encode("utf-8")).hexdigest()
                new_get_or_url = f"{GET_OR_URL}{secret_key}&logo={LOGO_URL}"
                new_path = os.path.join(LOCAL_PATH, "OR_image", f"{secret_key}.jpg")
                response = requests.get(new_get_or_url)
                with open(new_path, 'wb') as f:
                    f.write(response.content)
                    print("二维码保存成功")
                data = {"secret_key": secret_key, "code": 0}  # 0表示未激活
                insert_list.append(data)
            except Exception as e:
                print(e)

        OR_COLLENTION.insert_many(insert_list)
        print("数据已保存成功")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    create_or(20)

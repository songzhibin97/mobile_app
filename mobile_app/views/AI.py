# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    :    
# @Author  : SongZhiBin


from flask import Blueprint, jsonify, request, send_file
from mobile_app.tool.mutual_translation import MutualTranslation
from mobile_app.tool.turing_robot import TuringRobot
from mobile_app.settings import MOBILE_APP_PATH
from mobile_app.settings import XIMALAYA_STORES_INFO, XIMALAYA_NURSERY_RHYMES_INFO
import os
import json

assistant = Blueprint('assistant', __name__)

mt = MutualTranslation()
tl = TuringRobot()
save_path = os.path.join(MOBILE_APP_PATH, "hint_audio")


@assistant.route("/message_prompt/<nickname>")
def message_prompt(nickname):
    """
    用于返回消息提示音
    :param from_user:
    :return:
    """

    id = mt.text_audio(save_path, f"你有一条来自{nickname}的消息,请注意查收")
    id = json.loads(id)
    audio_path = os.path.join(save_path, f"{id}")
    return send_file(audio_path)


@assistant.route("/message_prompt_audio/<nickname>")
def message_prompt_audio(nickname):
    """
    用于返回点播语言消息提示
    :param from_user:
    :return:
    """

    id = mt.text_audio(save_path, f"你有一首来自{nickname}点播的音频,接下来开始播放~")
    id = json.loads(id)
    audio_path = os.path.join(save_path, f"{id}.mp3")
    return send_file(audio_path)


@assistant.route("/ai", methods=['POST'])
def ai():
    """
    用于接受用户上传音频信息 解析音频信息 将其转化为文本 根据不同关键字进行节点区分
    :return:
    """
    send_data = {"code": 0}
    file_name = request.form.get("file_name")
    from_id = request.form.get("from_id")
    # {file_name: "3b69663c16f03bc087f3ae049b763f46.mp3", from_id: "3ea429f5d90585642031a1b88505b821",voice_message: true}
    try:
        if file_name and from_id:
            if file_name and from_id:
                # 拼接对应音频路径
                get_audio_path = os.path.join(MOBILE_APP_PATH, "upload_audio", file_name)
                # 将其音频转码
                new_file_name = mt.transcoding(get_audio_path)
                # 在拿到转码后音频的路径
                new_get_audio_path = os.path.join(MOBILE_APP_PATH, "upload_audio", new_file_name)
                # 将其转化为 文本
                text = mt.audio_text(new_get_audio_path)[0]
                # 接入图灵
                ret = tl.post(text)
                print("tuling", ret)
                if ret:
                    # 如果接入图灵成功返回text
                    path = os.path.join(MOBILE_APP_PATH, 'upload_audio')
                    print("path", path)
                    audio_id = mt.text_audio(path, ret)
                    print("id", audio_id,type(audio_id))
                    send_data["code"] = 200
                    send_data["file_name"] = audio_id
                    send_data['from'] = "小彬彬智能玩具助手"
                    print(send_data)
                    return jsonify(send_data)
                send_data['code'] = 300
                send_data["error"] = "图灵接口错误"
                return jsonify(send_data)
        send_data["code"] = 400
        send_data["error"] = "提交数据有误"
        return jsonify(send_data)
    except Exception as e:
        print(e)
        send_data["code"] = 500
        send_data["error"] = "内部错误"
        return jsonify(send_data)

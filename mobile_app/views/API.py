# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    :    
# @Author  : SongZhiBin


from flask import Blueprint, jsonify, request, send_file
from mobile_app.settings import M_LIST_INFO  # 获取Mobile_app中M_list中的db
from mobile_app.settings import PHOTO_INFO  # 获取Mobile_app中Photo_news db
from mobile_app.settings import XIMALAYA_STORES_INFO  # 获取ximalaya中storys_info db
from mobile_app.settings import XIMALAYA_NURSERY_RHYMES_INFO  # 获取ximalaya中nursery_rhymes_info db
from mobile_app.settings import OR_COLLENTION
from mobile_app.settings import CHATS_COLLENTION
from mobile_app.settings import TOY_INFO
from mobile_app.settings import LOGIN_COLLENTION
from mobile_app.settings import UNREAD_MESSAGE_COLLENTION
from mobile_app.settings import REQUEST_FRIEND_COLLENTION
from mobile_app.settings import MOBILE_APP_PATH
from OR.settings import OR_PATH
from bson import ObjectId
import os
from hashlib import md5
import uuid
import time
import json

api = Blueprint('api', __name__)


@api.route("/m_list/<page>", methods=["POST"])
def m_list(page):
    """
    从MongoDB中获取数据并返回
    :return:
    """
    try:
        count_data = M_LIST_INFO.find({}).count()  # 计算数据库的数据量
        return_data = M_LIST_INFO.find({}, {"_id": 0}).limit(10).skip(int(page) * 10).sort([("time", -1)])
        if count_data > int(page) * 10:  # 判断数据量
            data_code = 200
            return_list = []
            for data in return_data:
                return_list.append(data)
            new_data = json.dumps({"data_code": data_code, "data_conent": return_list})
            return new_data
        return jsonify({"data_code": 400, "error_message": "无更多数据"})
    except Exception as e:
        return jsonify({"data_code": 500, "error_message": "服务器错误"})


@api.route("/photo_new", methods=["POST"])
def photo_new():
    """
    从MongoDB中获取数据并返回
    """
    data_code = 200
    return_list = []
    return_data = PHOTO_INFO.find({}, {"_id": 0}).limit(4).sort([("time", -1)])
    for data in return_data:
        return_list.append(data)
    new_data = json.dumps({"data_code": data_code, "data_conent": return_list})
    return new_data


@api.route('/audios/<subject>/<page>', methods=["POST"])
def audios(subject, page):
    """
    从MongoDB中获取对应数据返回
    subject 区分专题
    page 页码
    :param page:
    :return:
    """
    db = None
    if subject == 'story':
        db = XIMALAYA_STORES_INFO
    if subject == "nursery_rhyme":
        db = XIMALAYA_NURSERY_RHYMES_INFO
    if db:
        try:
            data_code = 200
            count_data = db.find({}).count()  # 计算数据库的数据量
            if count_data > int(page) * 10:
                return_data = db.find({}, {"_id": 0, "audio_name": 0}).limit(10).skip(int(page) * 10).sort(
                    [("nickname", -1)])
                return_list = [data for data in return_data]
                new_data = json.dumps({"data_code": data_code, "data_conent": return_list})
                return new_data
            return jsonify({"data_code": 400, "error_message": "无更多数据"})
        except Exception as e:
            return jsonify({"data_code": 500, "error_message": "服务器错误"})
    return jsonify({"data_code": 402, "error_message": "subject无对应数据"})


@api.route('/check_key', methods=["POST"])
def check_key():
    """
    扫描二维码激活玩具api
    :return:
    """
    data = {"code": 0}
    try:
        or_key = request.form.get("or_key")  # 获取后台提交玩具id数据
        if or_key:  # 如果提交数据不为空进行下一步判断
            activation_id = OR_COLLENTION.find_one({"secret_key": or_key})  # 从数据库中寻找toy_id玩具
            if activation_id and activation_id.get("code") == 0:  # 如果找到玩具id 且状态为0 未激活
                # OR_COLLENTION.update_one(activation_id, {"$set": {"code": 1}})  # 将玩具code置1 废除 在绑定成功后写1
                data["code"] = 200
                data["message"] = "开始执行绑定"
                data["toy_id"] = or_key
                return jsonify(data)
            if activation_id.get("code") == 1:
                # 如果玩具已被绑定 将玩具id返回 用于添加好友
                data["code"] = 202
                data["message"] = "玩具已被绑定,开始执行好友添加"
                data['error'] = "玩具已被绑定"
                data["toy_id"] = or_key
                return jsonify(data)
            # 如果找不到玩具
            data["code"] = 500
            data["error"] = "非法秘钥"
            return jsonify(data)
        # 如果后台数据为空则
        data["code"] = 400
        data["error"] = "无效数据"
        return jsonify(data)
    except Exception as e:
        data["code"] = 300
        data["error"] = "服务器内部错误"
        return jsonify(data)


@api.route("/create_toy", methods=["POST"])
def create_toy():
    """
    用于处理用户扫码成功后注册玩具信息
    :return:
    """
    data = {"code": 0}
    try:
        # 获取用户信息以及扫码出现的or_key
        if request.form.to_dict().get("app_id") and request.form.to_dict().get("or_key"):
            user_id = request.form.to_dict().pop("app_id")
            or_key = request.form.to_dict().pop("or_key")

            user_info = LOGIN_COLLENTION.find_one({"_id": ObjectId(user_id)})
            if user_info:
                # 创建聊天框
                chats = CHATS_COLLENTION.insert_one({"user_list": [], "historical": []})
                chats_id = chats.inserted_id

                # 构建玩具信息
                toy_info = request.form.to_dict()
                toy_info["bind_user"] = user_id
                toy_info["avatar"] = "toy.jpg"
                toy_info["or_key"] = or_key
                toy_info["friends"] = [
                    {"friend_id": user_id,
                     "friend_name": user_info.get("nickname"),
                     "friend_nickname": toy_info.pop("nickname"),
                     "friend_avatar": "app.jpg",
                     "friend_type": "app",
                     "friend_chat": str(chats_id)
                     }
                ]
                # 将玩具信息插入至数据库
                TOY_INFO.insert_one(toy_info)

                # 构建用户信息
                user_info["bind_toy"].append(or_key)
                user_info["friends"].append(
                    {"friend_id": or_key,
                     "friend_name": toy_info.get("toy_name"),
                     "friend_nickname": toy_info.get("baby_name"),
                     "friend_avatar": "toy.jpg",
                     "friend_type": "toy",
                     "friend_chat": str(chats_id)
                     }
                )
                # 将用户信息更新
                LOGIN_COLLENTION.update_one({"_id": ObjectId(user_id)}, {"$set": user_info})

                CHATS_COLLENTION.update_one({"_id": chats_id}, {"$set": {"user_list": [user_id, or_key]}})
                OR_COLLENTION.update_one({"secret_key": or_key}, {"$set": {"code": 1}})
                data["code"] = 200
                data["message"] = "玩具已激活成功"
                return jsonify(data)
            else:
                data['code'] = 402
                data['error'] = '只能使用app进行绑定'
                return jsonify(data)
        else:
            data["code"] = 400
            data["error"] = "提交数据残缺"
            return jsonify(data)
    except Exception as e:
        data['code'] = 500
        data["error"] = "出错啦"
        return jsonify(data)


@api.route("/get_equipment", methods=["POST"])
def get_equipment():
    """
    获取当前id的绑定设备信息
    :return:
    """
    data = {"coee": 0}
    id = request.form.get("id")
    if id:
        user = LOGIN_COLLENTION.find_one({"_id": ObjectId(id)})
        if user:
            data["code"] = 200
            toy_keys = [key for key in user.get("bind_toy")]
            equipments = TOY_INFO.find({"or_key": {"$in": toy_keys}}, {"_id": 0, "friends": 0})
            data['equipments'] = list(equipments)
            return jsonify(data)
        data["code"] = 300
        data['error'] = "用户不存在"
        return jsonify(data)
    data["code"] = 400
    data['error'] = "提交数据为空"
    return jsonify(data)


@api.route("/get_friends", methods=["POST"])
def get_friends():
    """
    获取当前id的好友信息
    :return:
    """
    data = {"code": 0}
    id = request.form.get("id")
    type = request.form.get("type")
    if id != "null" and id and type:
        if type == "app":
            user = LOGIN_COLLENTION.find_one({"_id": ObjectId(id)})
            if user:
                data["code"] = 200
                data["friend_dict"] = user.get("friends")
                return jsonify(data)
            data['code'] = 300
            data['error'] = '用户不存在'
            return jsonify(data)
        if type == "toy":
            toy = TOY_INFO.find_one({"or_key": id})
            if toy:
                data["code"] = 200
                data["friend_dict"] = toy.get("friends")
                return jsonify(data)
            else:
                data["code"] = 300
                data["error"] = "玩具不存在"
        data["code"] = 304
        data["error"] = "用户类型不存在"

    data["code"] = 400
    data["error"] = "请先登录"
    return jsonify(data)


@api.route("/upload_file", methods=["POST"])
def upload_file():
    """
    用于获取保存app上传的音频文件
    :return:
    """
    data = {"code": 0}
    f = request.files.get("audio_file")
    if f:
        print(f)
        try:
            # 如果句柄存在则进行路径分配并且保存文件
            f.filename = md5(f"{uuid.uuid4()}{time.time()}{uuid.uuid4()}".encode("utf-8")).hexdigest()
            new_path = os.path.join(os.getcwd(), "upload_audio", f.filename)
            print(new_path)
            f.save(new_path)
            # 利用ffmpeg 将原文件进行转码至MP3格式
            os.system(f"ffmpeg -i {new_path} {new_path}.mp3")
            data["code"] = 200
            data["file_name"] = f"{f.filename}.mp3"
            data["file_path"] = f"{new_path}.mp3"
            print(data)
            return jsonify(data)
        except Exception as e:
            print(e)
            data["code"] = 500
            data["error"] = '服务器内部错误'
            return jsonify(data)
    data["code"] = 400
    data["error"] = "没有找到上传的音频文件"
    return jsonify(data)


@api.route("/get_local_audio/<audio_id>")
def get_local_audio(audio_id):
    """
    用户获取flask语音消息资源接口
    :param audio_id:
    :return:
    """
    if audio_id:
        new_path = os.path.join(os.getcwd(), "upload_audio", audio_id)
        return send_file(new_path)


@api.route("/get_boot_prompt/<code>")
def get_boot_prompt(code):
    """
    获取开机音乐
    :param :
    :return:
    """
    try:
        if code:
            new_path = os.path.join(os.getcwd(), "boot_prompt", f"code{code}.mp3")
            return send_file(new_path)
    except Exception as e:
        return jsonify({"code": 500})


@api.route("/get_chat_historical/<chat_id>")
def get_chat_historical(chat_id):
    """
    通过chat_id获取聊天历史
    :param chat_id:
    :return:
    """
    data = {"code": 0}
    if chat_id:
        new_data = CHATS_COLLENTION.find_one({"_id": ObjectId(chat_id)})
        if new_data:
            data['code'] = 200
            # 仅显示十条历史记录
            data['friend_list'] = new_data["historical"][-10:]
            return jsonify(data)
    data["code"] = 500
    data["error"] = "无效id"
    return jsonify(data)


@api.route("/get_unread_message/<to_id>/<from_id>/")
def get_unread_message(to_id, from_id):
    """
    获取未读消息数量,再从消息历史中获取消息
    :return:
    """
    data = {"code": 200}
    unread_message_list = []
    try:

        # 判断提交数据
        if to_id and from_id:
            # 如果 toy1 与 toy2 同时满足 则是玩具与玩具通讯
            toy1 = TOY_INFO.find_one({"or_key": to_id})
            toy2 = TOY_INFO.find_one({"or_key": from_id})
            if toy1 and toy2:
                chats_dict = CHATS_COLLENTION.find_one({"user_list": {"$all": [to_id, from_id]}})
                if chats_dict:
                    for messages in chats_dict.get("historical"):
                        if messages.get("from_id") != to_id:
                            unread_message_list.append(messages)
                        continue
                        # 在进行未读消息查询
                    get_number = UNREAD_MESSAGE_COLLENTION.find_one({"from": from_id, "to": to_id})
                    if get_number:
                        # 如果找到对应数据行进行检索找到未读消息数据 进行unread_message_list切分打包至data中
                        num = int(get_number.get("message"))
                        if num == 0:
                            data["unread_message_list"] = None
                            data["code"] = 200
                            return jsonify(data)
                        UNREAD_MESSAGE_COLLENTION.update_one({"from": from_id, "to": to_id}, {"$set": {"message": 0}})
                        data["unread_message_list"] = unread_message_list[-num:]
                        data["code"] = 200
                        print(data)
                        return jsonify(data)
            to_type = 'app'
            # 如果toy1不为空则为app发送给toy的信息
            if toy1:
                # 在TOY_INFO中查找to_id是否存在 如果存在则为app发送给玩具消息
                to_type = "toy"
            # 找到对应toy_id以及from_id的聊天框
            chats_dict = CHATS_COLLENTION.find_one({"user_list": {"$all": [to_id, from_id]}})
            if chats_dict:
                # 如果聊天框存在则根据 to_type类型进行区分选取 app情况根据是否有is_send来判断消息是否为app发送
                # 将不是自己发送的消息放入 unread_message_list
                if to_type == "app":
                    for messages in chats_dict.get("historical"):
                        if not messages.get("is_send"):
                            unread_message_list.append(messages)
                        continue
                if to_type == 'toy':
                    for messages in chats_dict.get("historical"):
                        if messages.get("is_send"):
                            unread_message_list.append(messages)
                        continue

                # 在进行未读消息查询
                get_number = UNREAD_MESSAGE_COLLENTION.find_one({"from": from_id, "to": to_id})
                if get_number:
                    # 如果找到对应数据行进行检索找到未读消息数据 进行unread_message_list切分打包至data中
                    num = int(get_number.get("message"))
                    if num == 0:
                        data["unread_message_list"] = None
                        data["code"] = 200
                        return jsonify(data)
                    UNREAD_MESSAGE_COLLENTION.update_one({"from": from_id, "to": to_id}, {"$set": {"message": 0}})
                    data["unread_message_list"] = unread_message_list[-num:]
                    data["code"] = 200
                    return jsonify(data)
        data["code"] = 400
        data['error'] = "参数无效"
        return jsonify(data)
    except Exception as e:
        data["code"] = 500
        data['error'] = "内部错误"
        return jsonify(data)


@api.route("/get_unread_message_num/<to_id>")
def get_unread_message_num(to_id):
    """
    用于app端显示未读消息数
    :param to_id:
    :return:
    """
    send_data = {"code": 0}
    try:
        if to_id:
            message_list = UNREAD_MESSAGE_COLLENTION.find({"to": to_id}, {"_id": 0})
            if not message_list:
                send_data["count"] = 0
                send_data["unread_message_list"] = []
            unread_message_list = []
            count = 0
            for message in message_list:
                unread_message_list.append(message)
                count += message.get("message")
            send_data['code'] = 200
            send_data["count"] = count
            send_data['unread_message_list'] = unread_message_list
            print("send_data", send_data)
            return jsonify(send_data)
        send_data["code"] = 400
        send_data['error'] = "上传参数错误"
        return jsonify(send_data)
    except Exception as e:
        send_data['code'] = 500
        send_data["error"] = '内部错误'
        return jsonify(send_data)


@api.route("/empty_unread/<from_id>/<to_id>")
def empty_unread(from_id, to_id):
    """
    用于清空未读消息计数
    :param from_id:
    :param to_id:
    :return:
    """
    send_data = {"code": 0}
    try:
        if from_id and to_id:
            UNREAD_MESSAGE_COLLENTION.update_one({"from": from_id, 'to': to_id}, {"$set": {"message": float(0)}})
            send_data["code"] = 200
            send_data['data'] = '清空成功'
            send_data["from_id"] = from_id
            return jsonify(send_data)
        send_data["code"] = 400
        send_data['error'] = "上传参数有误"
        return jsonify(send_data)
    except Exception as e:
        send_data['code'] = 500
        send_data['error'] = "内部错误"
        return jsonify(send_data)


@api.route("/get_toy_info", methods=["POST"])
def get_toy_info():
    """
    用于获取玩具详情
    :return:
    """
    send_data = {"code": 0}
    try:
        toy_id = request.form.get("toy_id")
        if toy_id:
            toy_info = TOY_INFO.find_one({"or_key": toy_id}, {"_id": 0})
            if toy_info:
                send_data['code'] = 200
                send_data['info'] = toy_info
                return jsonify(send_data)
            send_data['code'] = 405
            send_data['error'] = "数据校验失败"
            return jsonify(send_data)
        send_data['code'] = 400
        send_data['error'] = "上传数据为空"
        return jsonify(send_data)
    except Exception as e:
        send_data['code'] = 500
        send_data["error"] = "内部错误"
        return jsonify(send_data)


@api.route("/get_or/<or_key>")
def get_or(or_key):
    """
    获取二维码图片
    :param or_key:
    :return:
    """
    try:
        or_image_path = os.path.join(OR_PATH, "OR_image", f"{or_key}.jpg")
        return send_file(or_image_path)
    except Exception as e:
        return None


@api.route("/send_friend_request", methods=["POST"])
def send_friend_request():
    """
    发送好友申请
    :return:
    """
    send_data = {"code": 0}
    try:
        toy_id = request.form.get("toy_id")
        to_toy = request.form.get("to_toy")
        request_info = request.form.get("request_info")
        friend_nickname = request.form.get("friend_nickname")
        if toy_id and to_toy and request_info and friend_nickname:
            ret = REQUEST_FRIEND_COLLENTION.find_one({"from": toy_id, "to": to_toy})
            if not ret:
                request_friend_dict = {
                    "from": toy_id,
                    "to": to_toy,
                    "request_info": request_info,
                    "friend_nickname": friend_nickname,
                    "code": 0
                }
                REQUEST_FRIEND_COLLENTION.insert_one(request_friend_dict)
                send_data['code'] = 200
                send_data["message"] = "请求发送成功"
                return jsonify(send_data)
            send_data['code'] = 300
            send_data["error"] = "您已经发送过请求或你们已经是好友了"
            return jsonify(send_data)
        send_data['code'] = 400
        send_data['error'] = "参数不完整或为空"
        return jsonify(send_data)
    except Exception as e:
        print(e)
        send_data['code'] = 500
        send_data['error'] = '内部错误'
        return jsonify(send_data)


@api.route("/get_friend_request", methods=["POST"])
def get_friend_request():
    """
    获取请求被加为好友信息
    :return:
    """
    send_data = {"code": 200}
    try:
        toy_id = request.form.get("toy_id")
        if toy_id:
            get_request_list = REQUEST_FRIEND_COLLENTION.find({"to": toy_id, "code": 0}, {"_id": 0})
            request_list = []
            for request_info in get_request_list:
                dic = {
                    "from_info": TOY_INFO.find_one({"or_key": request_info.get("from")}, {"_id": 0, "friends": 0}),
                    "request_info": request_info.get("request_info"),
                    "friend_nickname": request_info.get("friend_nickname")
                }
                request_list.append(dic)
            send_data['code'] = 200
            send_data["request_list"] = request_list if request_list else None
            return jsonify(send_data)
        send_data['code'] = 400
        send_data["error"] = "上传数据为空"
    except Exception as e:
        send_data["code"] = 500
        send_data["error"] = "内部错误"
        return jsonify(send_data)


@api.route('/dispose_request', methods=["POST"])
def dispose_request():
    """
    处理好友请求 建立好友关系
    :return:
    """
    send_data = {"code": 0}
    try:
        toy_nickname = request.form.get("toy_nickname")  # 申请用户设置添加好友成功备注
        from_nickname = request.form.get("from_nickname")  # 当前处理人设置添加人的备注
        toy_id = request.form.get("toy_id")
        from_id = request.form.get("from_id")

        if REQUEST_FRIEND_COLLENTION.find_one({"from":from_id,"to":toy_id,"code":3}):
            send_data['code'] = 305
            send_data['error'] = "不能重复提交数据"
            return jsonify(send_data)

        if toy_nickname and from_nickname and toy_id and from_id:
            to_user = TOY_INFO.find_one({"or_key": toy_id}, {"_id": 0})
            from_user = TOY_INFO.find_one({"or_key": from_id}, {"_id": 0})

            # 构建聊天框
            chats = CHATS_COLLENTION.insert_one({"user_list": [], "historical": []})
            chats_id = chats.inserted_id
            # 构建相互的字典

            # to_add_friend 是往to_user中添加from_user信息栏
            to_add_friend = {
                "friend_id": from_id,
                "friend_name": from_user.get("toy_name"),
                "friend_nickname": from_nickname,
                "friend_avatar": "toy.jpg",
                "friend_type": "toy",
                "friend_chat": str(chats_id)
            }

            from_add_friend = {
                "friend_id": toy_id,
                "friend_name": to_user.get("toy_name"),
                "friend_nickname": toy_nickname,
                "friend_avatar": "toy.jpg",
                "friend_type": "toy",
                "friend_chat": str(chats_id)
            }
            # 更新至mongodb
            to_user.get("friends").append(to_add_friend)
            from_user.get("friends").append(from_add_friend)

            TOY_INFO.update_one({"or_key": toy_id}, {"$set": to_user})
            TOY_INFO.update_one({"or_key": from_id}, {"$set": from_user})
            # 将chat更新至mongodb
            CHATS_COLLENTION.update_one({"_id": chats_id}, {"$set": {"user_list": [toy_id, from_id]}})
            # 更新请求状态
            REQUEST_FRIEND_COLLENTION.update_one({"from": from_id, "to": toy_id}, {"$set": {"code": 3}})
            send_data["code"] = 200
            send_data['message'] = '处理成功'
            return jsonify(send_data)
        send_data['code'] = 400
        send_data['error'] = "上传参数不完整或为空"
        return jsonify(send_data)


    except Exception as e:
        print(e)
        send_data['code'] = 500
        send_data['error'] = "内部错误"
        return jsonify(send_data)


@api.route("/get_app")
def get_app():
    app_path = os.path.join(MOBILE_APP_PATH,"app_file","H51E99050_0820235419.apk")
    return send_file(app_path)
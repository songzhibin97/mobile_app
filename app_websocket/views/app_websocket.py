# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    :    
# @Author  : SongZhiBin


from flask import Blueprint, request, render_template, jsonify
import json
from mobile_app.settings import OR_COLLENTION, CHATS_COLLENTION, UNREAD_MESSAGE_COLLENTION
from bson import ObjectId

web_socket_api = Blueprint("web_socket_api", __name__)
socket_dict = {}


@web_socket_api.route('/app/<app_id>')
def user_socket(app_id):
    # 获取当前用户的socket句柄
    user_socket = request.environ.get("wsgi.websocket")
    # 如果当前有socket句柄 则将对应user添加至 user_socket_dict
    if user_socket:
        socket_dict[app_id] = user_socket
        while True:
            try:
                message = user_socket.receive()  # 接受消息
                send_message = json.loads(message)
                toy_socket = socket_dict.get(send_message.get("toy_id"))
                # 并将消息保存至对应chat中
                chat = send_message.get("chat")
                if chat:
                    # 添加到消息历史 chat中的 historical
                    new_data = CHATS_COLLENTION.find_one({"_id": ObjectId(chat)})
                    new_data["historical"].append(send_message.get("data"))
                    # CHATS_COLLENTION.update_one({"_id": ObjectId(chat)}, {"$set": new_data}
                    CHATS_COLLENTION.update_one({"_id": ObjectId(chat)},
                                                {"$push": {"historical": send_message.get("data")}})
                    # # 添加到未读消息
                    UNREAD_MESSAGE_COLLENTION.update_one({"to": send_message.get("toy_id"), "from": app_id},
                                                         {"$inc": {"message": float(1)}},
                                                         True)
                toy_socket.send(json.dumps(send_message.get("data")))
            except:
                return jsonify("websocket 已断开连接")


@web_socket_api.route("/toy/<toy_id>")
def toy_socket(toy_id):
    # 获取当前用户的socket句柄
    toy_socket = request.environ.get("wsgi.websocket")
    # 如果当前有socket句柄 则将对应user添加至 user_socket_dict
    if toy_socket:
        socket_dict[toy_id] = toy_socket
        print(socket_dict)
        while True:
            try:
                message = toy_socket.receive()  # 接受消息
                send_message = json.loads(message)
                # user_socket.send(send_message)
                app_socket = socket_dict.get(send_message.get("app_id"))
                # 并将消息保存至对应chat中
                chat = send_message.get("chat")
                if chat:
                    new_data = CHATS_COLLENTION.find_one({"_id": ObjectId(chat)})
                    new_data["historical"].append(send_message.get("data"))
                    # CHATS_COLLENTION.update_one({"_id": ObjectId(chat)}, {"$set": new_data})
                    CHATS_COLLENTION.update_one({"_id": ObjectId(chat)},
                                                {"$push": {"historical": send_message.get("data")}})

                    # # 添加到未读消息
                    UNREAD_MESSAGE_COLLENTION.update_one({"to": send_message.get("app_id"), "from": toy_id},
                                                         {"$inc": {"message": float(1)}},
                                                         True)

                app_socket.send(json.dumps(send_message.get("data")))
            except:
                return jsonify("websocket 已断开连接")


@web_socket_api.route("/toys")
def toys():
    return render_template("toy_audio.html")


@web_socket_api.route("/toy_login", methods=["POST"])
def toy_login():
    """
    处理玩具登录
    :return:
    """
    data = {"code": 0}
    toy_id = request.form.get("toy_id")
    if toy_id:
        toy = OR_COLLENTION.find_one({"secret_key": toy_id})
        if toy:
            toy_code = str(toy.get("code"))
            if toy_code == "1":
                data["code"] = 200
                data["message"] = "欢迎使用小彬彬开发的智能玩具,祝您玩的开心"
                return jsonify(data)
            data['code'] = 210
            data['error'] = "请先执行玩具激活流程,再来使用只能玩具哟"
            return jsonify(data)
        else:
            data["code"] = 302
            data["error"] = "请查证玩具id是否正确,如有疑问请联系售后"
            return jsonify(data)
    data["code"] = 400
    data["error"] = "提交玩具id为空"
    return jsonify(data)

# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    :    
# @Author  : SongZhiBin


from flask import Blueprint, request, jsonify
from mobile_app.settings import LOGIN_COLLENTION  # MongoDB User用户
from mobile_app.settings import OR_COLLENTION
from bson import ObjectId

log_in = Blueprint("log_in", __name__)

@log_in.route("/login", methods=["POST"])
def login():
    """
    处理用户登录
    :return:
    """
    data = {
        "code": None
    }
    get_data = request.form.to_dict()
    if get_data:
        user = LOGIN_COLLENTION.find_one(get_data, {"password": 0})
        if user:
            data['code'] = 200
            data["id"] = str(user.get("_id"))
            data['nickname'] = user.get("nickname")
            return jsonify(data)
    data["code"] = 400
    return jsonify(data)


@log_in.route("/register", methods=['POST'])
def register():
    """
    处理用户注册
    :return:
    """
    data = {
        "code": None
    }
    get_data = request.form.to_dict()
    # 判断是否有提交数据
    if get_data:
        username = get_data.get("username")
        if LOGIN_COLLENTION.find_one({"username": username}):
            data["code"] = 302
            data["message"] = "用户已被注册"
            return jsonify(data)
        get_data['bind_toy'] = []
        get_data["friends"] = []
        LOGIN_COLLENTION.insert_one(get_data)
        data["code"] = 200
        return jsonify(data)


@log_in.route('/check_user', methods=["POST"])
def check_user():
    """
    处理用户自动登录校验
    :return:
    """
    data = {
        "code": None
    }
    user_id = request.form.to_dict().get("id")
    # 判断是否有提交数据
    if user_id:
        obj_id = ObjectId(user_id)
        user_info = LOGIN_COLLENTION.find_one({"_id": obj_id})
        if user_info:
            data['code'] = 200
            data["id"] = user_id
            data['nickname'] = user_info.get('nickname')
            return jsonify(data)
        data['code'] = 404
        data["error"] = "用户信息无效"
        return jsonify(data)
    data['code'] = 500
    data['error'] = "用户数据为空"

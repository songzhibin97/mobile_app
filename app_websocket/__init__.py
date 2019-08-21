# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    :    
# @Author  : SongZhiBin


from flask import Flask
from app_websocket.views.app_websocket import web_socket_api


def web_socket_app_flask():
    app = Flask(__name__)  # type:Flask
    app.register_blueprint(web_socket_api)
    return app

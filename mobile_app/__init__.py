# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    :    
# @Author  : SongZhiBin


from flask import Flask
from mobile_app.views.login import log_in
from mobile_app.views.API import api
from mobile_app.views.AI import assistant

def app_flask():
    app = Flask(__name__)  # type:Flask
    app.register_blueprint(log_in)
    app.register_blueprint(api)
    app.register_blueprint(assistant)

    return app

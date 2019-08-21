# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    :    
# @Author  : SongZhiBin

from flask import Flask, request, render_template, jsonify

web_toy = Flask(__name__)


@web_toy.route("/toys")
def toys():
    return render_template("toy_audio.html")


if __name__ == "__main__":
    web_toy.run("0.0.0.0", 80)

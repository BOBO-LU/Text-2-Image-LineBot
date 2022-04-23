
from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from clip_py import clip_class

import configparser

app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

clip_model = clip_class()


@app.route("/", methods=['GET'])
def get():
    return 'OK'


# 接收 LINE 的資訊
@app.route("/clip", methods=['POST'])
def callback():

    body = request.json
    txt = body['text']
    max_img_cnt = body['max_img_cnt']
    print(txt)
    img_list = clip_model.search_unslash(txt, max_img_cnt)
    print(img_list)

    return {"img_list": img_list}


if __name__ == "__main__":
    app.run(host=config['ENV']['CLIP_HOST'], port=config['ENV']['CLIP_PORT'])
    # from waitress import serve
    # serve(app, host=config['ENV']['HOST'], port=config['ENV']['PORT'])

from __future__ import unicode_literals
from operator import ge
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction
from routing import route_to_clip, get_unsplash_redirect
import json
import configparser
import random
from utils import dictConfig

app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config['LINE']['channel_access_token'])
handler = WebhookHandler(config['LINE']['channel_secret'])
clip_address = f"http://{config['ENV']['CLIP_HOST']}:{config['ENV']['CLIP_PORT']}/clip"


@app.route("/", methods=['GET'])
def get():
    clip_response = route_to_clip("I am bobo", clip_address)
    return clip_response


# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        handler.handle(body, signature)
        app.logger.info('callback success!')
    except InvalidSignatureError:
        abort(400)
        app.logger.info('callback failed!')
    
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def msg_handler(event):

    if event.message.text[0] == '!':
        res = "https://images.unsplash.com/photo-1524389054500-26845af32b1e?crop=entropy&cs=tinysrgb&fit=crop&fm=jpg&h=160&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY1MDY4NzczOQ&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=160"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=res)
        )

    elif event.message.text[0] == '@':
        res = "https://images.unsplash.com/photo-1524389054500-26845af32b1e?crop=entropy&cs=tinysrgb&fit=crop&fm=jpg&h=160&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY1MDY4NzczOQ&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=160"
        image_message = ImageSendMessage(
                original_content_url=res+"/640x640",
                preview_image_url=res+"/160x160"
            )
        line_bot_api.reply_message(
            event.reply_token,
            image_message
        )
    
    
    else:

        text = str.lower(event.message.text)

        if text == "hi":
            example_input_list = ['I feel so happy because I have a great dinner.','Feeling anxious due to the unfinished homework.', 'The feeling when I get the offer.', 'The feeling when you are writing thesis.' ]
            random_example_input = random.choice(example_input_list)
            message = TextSendMessage(
                        text=" i am bobo",
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyButton(
                                    image_url="https://i.ibb.co/dJPnTr9/pika-icon.png",
                                    action={
                                    "type": "message",
                                    "label": "About Me",
                                    "text": "About Me"
                                    }
                                ),
                                QuickReplyButton(
                                    action=MessageAction(label='Github', text='Github')
                                ),
                                QuickReplyButton(
                                    action=MessageAction(label='LinkedIn', text='LinkedIn')
                                ),
                                QuickReplyButton(
                                    action=MessageAction(label='Help', text='Help')
                                ),
                                QuickReplyButton(
                                    action=MessageAction(label='Example', text=random_example_input)
                                ),
                                
                            ]
                        )
                    )
            
        elif text == "about me" or text == "jonathan" or text=="bobo":
            message = TextSendMessage(text="I am Jonathan Lu, you can call me BOBO. I am seeking for data related internship.\n\n My resume: https://reurl.cc/e38lMR")

        elif text == "github":
            message = TextSendMessage(text='https://github.com/BOBO-LU')

        elif text == "linkedin":
            message = TextSendMessage(text='https://www.linkedin.com/in/luwenkai/')
        
        elif text == "help":
            help_text = "This bot aims to find the best image which can express your words, just type your feeling in English and let the bot finish the rest of the work.\n\nType 'Hi' to show quick reply prompts."
            message = TextSendMessage(text=help_text)


        else:

            # 將訊息轉成照片網址
            max_img_cnt = 1
            clip_response_str = route_to_clip(event.message.text, max_img_cnt, clip_address)
            clip_response = json.loads(clip_response_str)

            for img_url in clip_response['img_list']:
                original = get_unsplash_redirect(img_url+"/640x640")
                preview = get_unsplash_redirect(img_url+"/160x160")

                message = ImageSendMessage(
                    original_content_url=original,
                    preview_image_url=preview
                )

        # replay message 
        line_bot_api.reply_message(
            event.reply_token,
            message
        )
if __name__ == "__main__":
    app.run(host=config['ENV']['HOST'], port=config['ENV']['PORT'])
    # from waitress import serve
    # serve(app, host=config['ENV']['HOST'], port=config['ENV']['PORT'])
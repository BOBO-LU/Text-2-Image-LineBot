
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction
import configparser
import random
from clip_py import clip_class

app = Flask(__name__)

# 讀取設定
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config['LINE']['channel_access_token'])
handler = WebhookHandler(config['LINE']['channel_secret'])

# 實體化模型
clip_model = clip_class()


# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        handler.handle(body, signature)
        app.logger.info('Callback success!')
    except InvalidSignatureError:
        abort(400)
        app.logger.info('Callback failed, InvalidSignatureError!')
    
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

        # 特定情況
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
            message = TextSendMessage(text="I am Jonathan Lu, you can call me BOBO. I am seeking for data related internship.\n\n My resume:\nhttps://reurl.cc/e38lMR")

        elif text == "github":
            message = TextSendMessage(text='https://github.com/BOBO-LU')

        elif text == "linkedin":
            message = TextSendMessage(text='https://www.linkedin.com/in/luwenkai/')
        
        elif text == "help":
            help_text = "This bot aims to find the best image which can express your words, just type your feeling in English and let the bot finish the rest of the work.\n\nType 'Hi' to show quick reply prompts."
            message = TextSendMessage(text=help_text)

        # 將訊息轉成照片網址
        else:
            max_img_cnt = 1
            img_list = clip_model.search_unslash(event.message.text, max_img_cnt)

            for img_url in img_list:
                original = get_unsplash_redirect(img_url+"/640x640")
                preview = get_unsplash_redirect(img_url+"/160x160")

                message = ImageSendMessage(
                    original_content_url=original,
                    preview_image_url=preview
                )

        # 回傳訊息
        line_bot_api.reply_message(
            event.reply_token,
            message
        )

        
if __name__ == "__main__":
    app.run(host=config['ENV']['HOST'], port=config['ENV']['PORT'])

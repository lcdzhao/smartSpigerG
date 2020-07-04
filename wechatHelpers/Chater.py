# coding:utf-8
import time

import itchat
import requests

from spiderG import ActionController


class Chater:
    """
    该类是用来关心自己想关心的人的类。
    """

    def __init__(self, wechat_name, name_uuid):
        '''
        初始化
        '''
        self.wechat_name = wechat_name
        self.name_uuid = name_uuid

    def get_zhao_words(self, babyWords):

        '''
        获取图灵机器人的回复。
		return 图灵机器人的回复
        '''
        info = babyWords.encode('utf8')
        api_url = 'http://www.tuling123.com/openapi/api'  # 图灵机器人网址
        data = {
            'key': 'cefc853e3aa4404faf56b649fcff4763',
            'info': info,  # 这是我们从好友接收到的消息 然后转发给图灵机器人
            'userid': 'wechat-robot',  # 这里你想改什么都可以
        }
        r = requests.post(api_url, data=data).json()  # 把data数据发
        return r.get('text')

    def reply(self, babyWords):
        '''
        回复消息
        '''

        ActionController.act(babyWords)
        reply_words = self.get_zhao_words(babyWords)

        # 延时1s后发送
        time.sleep(1)
        itchat.send_msg(reply_words, toUserName=self.name_uuid)



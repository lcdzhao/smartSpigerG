# coding:utf-8
import io
import os
import random
import sys
import time
import wave

import itchat
from aip import AipSpeech
from pydub import AudioSegment

from wechatHelpers.Chater import Chater

sys.path.append('./wechatHelpers')
from apscheduler.schedulers.blocking import BlockingScheduler
import _thread



class ChatManager:
    chaters = {}
    automaticRepliers = {}

    def __init__(self):
        self.GFWeather = None

    def keepAliveJob(self):
        scheduler = BlockingScheduler()
        scheduler.add_job(self.keepAlive, 'interval', seconds=60 * 30)
        scheduler.start()

    def keepAlive(self):
        # 不准时发送，防止被微信查封
        sleepSeconds = random.randint(1, 5)
        time.sleep(sleepSeconds)
        ChatManager.set_system_notice('keepAlive')

    @staticmethod
    def addChater(wechat_name):
        friends = itchat.search_friends(name=wechat_name)
        if not friends:
            return '昵称有误,添加失败！'
        name_uuid = friends[0].get('UserName')
        chater = Chater(wechat_name, name_uuid)
        ChatManager.chaters[name_uuid] = chater
        return wechat_name + '已添加到聊天者中，他已可以获得隐藏功能！'

    @staticmethod
    def delChater(wechat_name):
        friends = itchat.search_friends(name=wechat_name)
        name_uuid = friends[0].get('UserName')
        if not ChatManager.chaters[name_uuid]:
            return '昵称有误,删除失败！'
        del ChatManager.chaters[name_uuid]
        return wechat_name + '已从关心者中删除！'

    def is_online(self, auto_login=True):
        """
        判断是否还在线,
        :param auto_login: bool,如果掉线了则自动登录(默认为 False)。
        :return: bool,当返回为 True 时，在线；False 已断开连接。
        """

        def online():
            '''
            通过获取好友信息，判断用户是否还在线
            :return: bool,当返回为 True 时，在线；False 已断开连接。
            '''
            try:
                if itchat.search_friends():
                    return True
            except:
                return False
            return True

        if online():
            return True
        # 仅仅判断是否在线
        if not auto_login:
            return online()

        # 登陆，尝试 5 次
        for _ in range(5):
            # 命令行显示登录二维码
            # itchat.auto_login(enableCmdQR=True)
            print('正在打印登陆二维码')
            if os.environ.get('MODE') == 'server':
                itchat.auto_login(enableCmdQR=2, hotReload=True)
                _thread.start_new_thread(itchat.run, ())
            else:
                itchat.auto_login(hotReload=True)
                _thread.start_new_thread(itchat.run, ())
            if online():
                print('登录成功')
                return True
        else:
            print('登录成功')
            return False

    @staticmethod
    def getOrders():
        """
        获取命令都有哪些
        """
        return (
            '命令错误，请按照下面提示来输入命令:\n'
            '    增加聊天者+空格+要加的人\n'
            '    删除聊天者+空格+要删除的人\n'
            '    查看聊天者\n'
        )

    @staticmethod
    def executiveOrder(orderWords):
        """
        处理各种命令
        """
        order = orderWords.split(' ', 1)
        if order[0] == '增加聊天者':
            return ChatManager.addChater(order[1])
        elif order[0] == '删除聊天者':
            return ChatManager.delChater(order[1])
        elif order[0] == '查看聊天者':
            if not ChatManager.chaters:
                return '列表为空'
            allchaters = '聊天者有:'
            for Chater in ChatManager.chaters.values():
                allchaters += '\n       ' + Chater.wechat_name
            return allchaters
        else:
            return ChatManager.getOrders()

    @staticmethod
    def asr(msg):
        # 将语音消息存入文件，想通过百度翻译，再通过获得图灵机器人的回复
        APP_ID = '16516161'
        API_KEY = 'eycPzd5xfCMsd0jn4aWrjwDz'
        SECRET_KEY = 'PLWIGyEIYcsYQoHuw6lPzxmBrrmSgsoc'
        client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
        msg['Text'](msg['FileName'])
        # 先从本地获取mp3的bytestring作为数据样本
        fp = open(msg['FileName'], 'rb')
        data = fp.read()
        fp.close()
        # 主要部分
        aud = io.BytesIO(data)
        sound = AudioSegment.from_file(aud, format='mp3')
        raw_data = sound._data
        # 写入到文件，验证结果是否正确。
        l = len(raw_data)
        f = wave.open("tmp.wav", 'wb')
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        f.setnframes(l)
        f.writeframes(raw_data)
        f.close()
        fp = open("tmp.wav", 'rb')
        result = client.asr(fp.read(), 'wav', 16000, {'dev_pid': 1536, })
        fp.close()
        os.remove('tmp.wav')
        os.remove(msg['FileName'])
        return result['result'][0]

    @staticmethod
    def set_system_notice(text):
        """
        给文件传输助手发送系统日志。
        :param text:日志内容
        :return:None
        """
        if text:
            text = '*' * 30 + '\n\n' + text + '\n\n' + '*' * 30
            itchat.send(text, toUserName='filehelper')

    @itchat.msg_register(itchat.content.TEXT)
    def replyText(msg):
        """
        接受文本消息，并进行回复！
        """
        fromUserName = msg['FromUserName']
        toUserName = msg['ToUserName']
        # 如果是发给filehelper的微信消息，则处理该命令
        if toUserName == 'filehelper':
            ChatManager.set_system_notice(ChatManager.executiveOrder(msg['Text']))
            return
        automaticReplier = ChatManager.automaticRepliers.get(fromUserName)
        if automaticReplier:
            automaticReplier.reply(msg['Text'])
        else:
            chater = ChatManager.chaters.get(fromUserName)
            if chater:
                chater.reply(msg['Text'])

    #        print(msg)

    @itchat.msg_register(itchat.content.RECORDING)
    def replyRECORDING(msg):
        """
        绑定语音消息，并进行回复！
        """
        fromUserName = msg['FromUserName']
        automaticReplier = ChatManager.automaticRepliers.get(fromUserName)
        if automaticReplier:
            asrMessage = ChatManager.asr(msg)
            automaticReplier.reply(asrMessage)
        else:
            Chater = ChatManager.chaters.get(fromUserName)
            if Chater:
                asrMessage = ChatManager.asr(msg)
                Chater.reply(asrMessage)

    def run(self):
        """
        主运行入口
        :return:None
        """
        # 自动登录
        print('正在登陆')
        if not self.is_online(auto_login=True):
            return
        _thread.start_new_thread(self.keepAliveJob, ())

#!/usr/bin/env/python
# File name   : ActionController.py
# Production  : GWR
# Website     : www.gewbot.com
# E-mail      : gewubot@163.com
# Author      : William
# Date        : 2019/07/24

import socket
import threading
import time

from spiderG import SpiderG

SpiderG.move_init()
import os
from spiderG import FPV
from spiderG import info
from spiderG import LED
from spiderG import switch

functionMode = 0
inited = False


def info_send_client():
    SERVER_IP = addr[0]
    SERVER_PORT = 2256  # Define port serial
    SERVER_ADDR = (SERVER_IP, SERVER_PORT)
    Info_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Set connection value for socket
    Info_Socket.connect(SERVER_ADDR)
    print(SERVER_ADDR)
    while 1:
        try:
            Info_Socket.send((
                                     info.get_cpu_tempfunc() + ' ' + info.get_cpu_use() + ' ' + info.get_ram_info() + ' ' + str(
                                 SpiderG.get_direction())).encode())
            time.sleep(1)
        except:
            time.sleep(10)
            pass


def FPV_thread():
    global fpv
    fpv = FPV.FPV()
    fpv.capture_thread(addr[0])


def ap_thread():
    os.system("sudo create_ap wlan0 eth0 Groovy 12345678")


def init():
    if not inited:
        switch.switchSetup()
        switch.set_all_switch_off()


def act(commond):
    init()
    global speed_set, functionMode, direction_command, turn_command

    speed_set = 100
    direction_command = 'no'
    turn_command = 'no'

    info_threading = threading.Thread(target=info_send_client)  # Define a thread for FPV and OpenCV
    info_threading.setDaemon(True)  # 'True' means it is a front thread,it would close when the mainloop() closes
    info_threading.start()  # Thread starts

    if not commond:
        return 

    elif '往前走' == commond:
        SpiderG.walk('forward')

    elif '往后走' == commond:
        SpiderG.walk('backward')

    elif 'DS' in commond:
        if turn_command == 'no':
            SpiderG.servoStop()

    elif '往左走' == commond:
        SpiderG.walk('turnleft')

    elif '往右走' == commond:
        SpiderG.walk('turnright')

    elif 'TS' in commond:
        if direction_command == 'no':
            SpiderG.servoStop()


    elif 'Switch_1_on' in commond:
        switch.switch(1, 1)
        tcpCliSock.send(('Switch_1_on').encode())

    elif 'Switch_1_off' in commond:
        switch.switch(1, 0)
        tcpCliSock.send(('Switch_1_off').encode())

    elif 'Switch_2_on' in commond:
        switch.switch(2, 1)
        tcpCliSock.send(('Switch_2_on').encode())

    elif 'Switch_2_off' in commond:
        switch.switch(2, 0)
        tcpCliSock.send(('Switch_2_off').encode())

    elif 'Switch_3_on' in commond:
        switch.switch(3, 1)
        tcpCliSock.send(('Switch_3_on').encode())

    elif 'Switch_3_off' in commond:
        switch.switch(3, 0)
        tcpCliSock.send(('Switch_3_off').encode())


    elif 'function_1_on' in commond:  # Steady
        functionMode = 1
        SpiderG.steadyModeOn()
        tcpCliSock.send(('function_1_on').encode())

    elif 'function_2_on' in commond:  # Color Find
        functionMode = 2
        fpv.FindColor(1)
        tcpCliSock.send(('function_2_on').encode())

    elif 'function_3_on' in commond:  # Watch Dog
        functionMode = 3
        fpv.WatchDog(1)
        tcpCliSock.send(('function_3_on').encode())

    elif 'function_4_on' in commond:  # T/D
        functionMode = 4
        SpiderG.gait_set = 0
        tcpCliSock.send(('function_4_on').encode())

    elif 'function_5_on' in commond:  # None (Action 1)
        functionMode = 5
        tcpCliSock.send(('function_5_on').encode())
        SpiderG.action_1()
        functionMode = 0
        tcpCliSock.send(('function_5_off').encode())

    elif 'function_6_on' in commond:  # None (Action 2)
        functionMode = 6
        tcpCliSock.send(('function_6_on').encode())
        SpiderG.action_2()
        functionMode = 0
        tcpCliSock.send(('function_6_off').encode())


    elif 'function_1_off' in commond:
        functionMode = 1
        SpiderG.steadyModeOff()
        tcpCliSock.send(('function_1_off').encode())

    elif 'function_2_off' in commond:
        functionMode = 0
        fpv.FindColor(0)
        switch.switch(1, 0)
        switch.switch(2, 0)
        switch.switch(3, 0)
        tcpCliSock.send(('function_2_off').encode())

    elif 'function_3_off' in commond:
        functionMode = 0
        fpv.WatchDog(0)
        tcpCliSock.send(('function_3_off').encode())

    elif 'function_4_off' in commond:
        functionMode = 0
        SpiderG.gait_set = 1
        tcpCliSock.send(('function_4_off').encode())

    elif 'function_5_off' in commond:
        functionMode = 0
        tcpCliSock.send(('function_5_off').encode())

    elif 'function_6_off' in commond:
        functionMode = 0
        tcpCliSock.send(('function_6_off').encode())


    elif '向左看' == commond:
        servo_command = 'lookleft'
        SpiderG.headLeft()

    elif '向右看' == commond:
        servo_command = 'lookright'
        SpiderG.headRight()

    elif '向上看' == commond:
        servo_command = 'up'
        SpiderG.headUp()

    elif '向下看' == commond:
        servo_command = 'down'
        SpiderG.headDown()

    elif '停止转头' == commond:
        if not functionMode:
            SpiderG.headStop()
        servo_command = 'no'
        pass

    elif '恢复' == commond:
        SpiderG.move_init()

    elif 'wsB' in commond:
        try:
            set_B = commond.split()
            speed_set = int(set_B[1])
        except:
            pass

    elif '站起来' == commond:
        SpiderG.walk('StandUp')

    elif '坐下去' == commond:
        SpiderG.walk('StayLow')

    elif '左摇' == commond:
        SpiderG.walk('Lean-R')

    elif '右摇' == commond:
        SpiderG.walk('Lean-L')

    else:
        pass

    print(commond)


def wifi_check():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("1.1.1.1", 80))
        ipaddr_check = s.getsockname()[0]
        s.close()
        print(ipaddr_check)

    except:
        ap_threading = threading.Thread(target=ap_thread)  # Define a thread for data receiving
        ap_threading.setDaemon(True)  # 'True' means it is a front thread,it would close when the mainloop() closes
        ap_threading.start()  # Thread starts

        LED.colorWipe(0, 16, 50)
        time.sleep(1)

        LED.colorWipe(0, 16, 100)
        time.sleep(1)

        LED.colorWipe(0, 16, 150)
        time.sleep(1)

        LED.colorWipe(0, 16, 200)
        time.sleep(1)

        LED.colorWipe(0, 16, 255)
        time.sleep(1)

        LED.colorWipe(35, 255, 35)


if __name__ == '__main__':
    switch.switchSetup()
    switch.set_all_switch_off()

    HOST = ''
    PORT = 10223  # Define port serial
    BUFSIZ = 1024  # Define buffer size
    ADDR = (HOST, PORT)

    try:
        LED = LED.LED()
        LED.colorWipe(255, 16, 0)
    except:
        print(
            'Use "sudo pip3 install rpi_ws281x" to install WS_281x package\n使用"sudo pip3 install rpi_ws281x"命令来安装rpi_ws281x')
        pass

    while 1:
        wifi_check()
        try:
            tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcpSerSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcpSerSock.bind(ADDR)
            tcpSerSock.listen(5)  # Start server,waiting for client
            print('waiting for connection...')
            tcpCliSock, addr = tcpSerSock.accept()
            print('...connected from :', addr)

            fpv = FPV.FPV()
            fps_threading = threading.Thread(target=FPV_thread)  # Define a thread for FPV and OpenCV
            fps_threading.setDaemon(True)  # 'True' means it is a front thread,it would close when the mainloop() closes
            fps_threading.start()  # Thread starts
            break
        except:
            LED.colorWipe(0, 0, 0)

        try:
            LED.colorWipe(0, 80, 255)
        except:
            pass

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

import SpiderG

SpiderG.move_init()

import os
import FPV
import info
import LED
import switch
switch.switchSetup()
switch.set_all_switch_off()

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





def act(commond):
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



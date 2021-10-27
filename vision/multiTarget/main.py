import sys
import time
from robomaster import robot
import cv2
import numpy as np

import connHelper
import newSignReco
import aim
from robomaster import blaster

pitchAngle = 0
yawAngle = 0
targetPoint = [0, 0]
aimFlag = True  # 通过这个变量控制是否瞄准
targetFlag = False
targetNum = 3  # 要打击目标的编号


def gimbalCallback(args):
    global pitchAngle
    global yawAngle
    global targetPoint
    # print(args)
    pitchAngle = args[0]
    yawAngle = args[1]
    if targetFlag and aimFlag:
        aim.aim(targetPoint, yOffset=-5, fire_type=blaster.INFRARED_FIRE)


if __name__ == '__main__':
    # if connHelper.start(ssid="Xiaomi_CC65OT", password="435782572") == False:
    #    sys.exit()
    time.sleep(1)
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_camera = ep_robot.camera
    ep_gimbal = ep_robot.gimbal
    ep_blaster = ep_robot.blaster
    aim.gimbalInit(ep_gimbal, ep_blaster)
    ep_gimbal.sub_angle(freq=5, callback=gimbalCallback)

    # 每次获取最新的1帧图像显示，并停留1秒
    ep_camera.start_video_stream(display=False)
    while True:
        try:
            # 读入数字模板
            for i in range(1, 4):
                newSignReco.Templates[i] = np.load('./' + str(i) + '.npy')
                # 读入图像
            img = ep_camera.read_cv2_image(strategy="newest")
            img = cv2.resize(img, (320, 180))
            # cv2.imshow('RoboMaster EP Vedio',img)
            imgT = img.copy()
            cx = int(imgT.shape[1] / 2 - 30)
            cy = int(imgT.shape[0] / 2)
            # 目标搜索
            objectInfo = []
            objectInfo = newSignReco.objectDetection(img, \
                                                     transhold=[[0, 160, 40], [15, 255, 255], [140, 160, 40],
                                                                [180, 255, 255]], \
                                                     roiTranshold=[[0, 0, 0], [15, 255, 255], [165, 0, 0],
                                                                   [179, 255, 255]])
            if len(objectInfo) == 0:
                cv2.putText(imgT, 'No Target!', (cx, cy), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255), 1, 8, 0)
                continue
            # 依次绘制
            for i in range(len(objectInfo)):
                contour, targetPt, num = objectInfo[i]
                # 绘制外接矩形
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(imgT, (x, y), (x + w, y + h), (0, 255, 0), 1)
                cv2.circle(imgT, targetPt, 1, (0, 255, 255), 2)  # 画红点
                # 坐标
                text = "(" + str(targetPt[0]) + ", " + str(targetPt[1]) + ")"
                cv2.putText(imgT, text, (targetPt[0] + 10, targetPt[1] + 10), \
                            cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 255, 255), 1, 8, 0)
                # 数字
                text = str(num)
                cv2.putText(imgT, text, (targetPt[0] + 10, targetPt[1]), \
                            cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 255, 255), 1, 8, 0)
            # 显示
            imgT = cv2.resize(imgT, (640, 360))
            cv2.imshow('RoboMaster EP Vedio', imgT)
            cv2.waitKey(1)
            # 依次检查是否为打击目标
            _targetFlag = False
            for i in range(len(objectInfo)):
                contour, targetPt, num = objectInfo[i]
                # 打击目标
                if num == targetNum:
                    targetPoint = targetPt
                    _targetFlag = True
                    break  # 确认一个打击目标后就终止循环
            targetFlag = _targetFlag

        except KeyboardInterrupt:
            ep_camera.stop_video_stream()
            ep_robot.close()
            print('User Interrupt')
            cv2.destroyAllWindows()
            break


    print('quit')
    sys.exit()
